"""
Color Manager for the 4colour project.

This module handles color assignment and color conflict resolution.
"""

import tkinter as tk
from color_utils import get_color_from_priority, find_lowest_available_priority, determine_color_priority_for_connections
from app_enums import ApplicationMode

class ColorManager:
    """Manages color assignment and conflict resolution."""
    
    def __init__(self, app):
        """Initialize with a reference to the main application.
        
        Args:
            app: The main CanvasApplication instance
        """
        self.app = app
        self.red_node_id = None  # Track the ID of a node that needs color fixing
        self.next_red_node_id = None  # Track a red node that will need fixing after current operation
    
    def assign_color_based_on_connections(self, circle_id=None):
        """Assign a color priority to a circle based on its connections.
        
        This function implements the deterministic color assignment logic.
        It ensures that no two connected circles have the same color by
        selecting the lowest priority color that doesn't cause conflicts.
        
        Args:
            circle_id: Optional ID of an existing circle to reassign color.
                      If None, this is assumed to be for a new circle.
        
        Returns:
            int: The assigned color priority
        """
        # For new circles or initial assignment, use priority 1 (yellow)
        if circle_id is None:
            return 1
            
        # For existing circles, get its connected circles
        circle = self.app.circle_lookup.get(circle_id)
        if not circle or not circle["connected_to"]:
            # No connections, or circle doesn't exist
            return 1
            
        # Get all colors used by connected circles
        used_priorities = set()
        for connected_id in circle["connected_to"]:
            connected_circle = self.app.circle_lookup.get(connected_id)
            if connected_circle and "color_priority" in connected_circle:
                used_priorities.add(connected_circle["color_priority"])
        
        # Use the color utility function to determine the appropriate priority
        priority = determine_color_priority_for_connections(used_priorities)
        
        # If priority 4 (red) is assigned, track it but don't swap automatically
        if priority == 4:
            self.red_node_id = circle_id
            print(f"DEBUG: Red node {circle_id} created in assign_color_based_on_connections")
            try:
                # Try to call the method - if it fails, we'll know
                self.app.handle_red_node_creation(circle_id)
            except Exception as e:
                print(f"ERROR: Failed to handle red node creation: {e}")
        
        return priority
    
    def check_and_resolve_color_conflicts(self, circle_id):
        """
        Checks for color conflicts after connections are made and resolves them.
        A conflict exists when two connected circles have the same color priority.
        
        Args:
            circle_id: ID of the circle to check for conflicts
            
        Returns:
            int: The color priority after resolving conflicts
        """
        # Get the current circle's data
        circle_data = self.app.circle_lookup.get(circle_id)
        if not circle_data:
            return None
            
        current_priority = circle_data["color_priority"]
        
        # Get all directly connected circles
        connected_circles = circle_data.get("connected_to", [])
        
        # If no connections, no conflicts to resolve
        if not connected_circles:
            return current_priority
        
        # Check for conflicts
        has_conflict = False
        used_priorities = set()
        
        for connected_id in connected_circles:
            connected_circle = self.app.circle_lookup.get(connected_id)
            if not connected_circle:
                continue
                
            connected_priority = connected_circle["color_priority"]
            used_priorities.add(connected_priority)
            if connected_priority == current_priority:
                has_conflict = True
        
        # If no conflict, keep the current priority
        if not has_conflict:
            return current_priority
        
        # Find the lowest priority that isn't used by any connected circle
        available_priority = find_lowest_available_priority(used_priorities)
        
        # If there are available priorities, use the lowest one
        if available_priority is not None:
            new_priority = available_priority
        else:
            # If all lower priorities are used, tag this node for manual fixing
            new_priority = 4
            circle_data["color_priority"] = new_priority
            new_color_name = get_color_from_priority(new_priority)
            self.app.canvas.itemconfig(circle_data["canvas_id"], fill=new_color_name)
            
            self.red_node_id = circle_id
            print(f"DEBUG: Red node {circle_id} created in check_and_resolve_color_conflicts")
            try:
                # Try to call the method - if it fails, we'll know
                self.app.handle_red_node_creation(circle_id)
            except Exception as e:
                print(f"ERROR: Failed to handle red node creation: {e}")
            
            return new_priority
        
        # Update the circle with the new priority
        circle_data["color_priority"] = new_priority
        
        # Get color name for visual update
        new_color_name = get_color_from_priority(new_priority)
        
        # Update the visual appearance of the circle
        self.app.canvas.itemconfig(circle_data["canvas_id"], fill=new_color_name)
        
        # Check for adjacent red nodes after conflict resolution
        if new_priority == 4:  # If this node is now red
            # Check all neighbors for red
            adjacent_red_nodes = []
            for connected_id in connected_circles:
                connected_circle = self.app.circle_lookup.get(connected_id)
                if connected_circle and connected_circle["color_priority"] == 4:
                    adjacent_red_nodes.append(connected_id)
                    
            if adjacent_red_nodes:
                warning_msg = f"WARNING: Red node {circle_id} is adjacent to other red nodes: {adjacent_red_nodes}"
                print(warning_msg)
                # Warning is only shown in console, not in UI
        
        return new_priority
    
    def reassign_color_network(self, circle_id):
        """
        Reassigns colors when a circle is assigned priority 4 (red).
        Attempts to swap priority 4 with an 'enclosed' neighbor.

        Parameters:
            circle_id (int): The ID of the circle initially assigned priority 4.

        Returns:
            int: The final color priority assigned to the circle_id.
        """
        circle_data = self.app.circle_lookup.get(circle_id)
        if not circle_data:
            return 4 # Should not happen if called correctly

        original_circle_priority = 4 # This circle was just assigned red

        swap_target_id = None
        swap_target_original_priority = None

        # Find an enclosed neighbor to swap with
        # BUG FIX: The current implementation stops at the first enclosed neighbor, but
        # not all neighbors might be suitable for swap. We need to check them all.
        enclosed_neighbors = []
        
        for connected_id in circle_data.get("connected_to", []):
            connected_circle_data = self.app.circle_lookup.get(connected_id)
            if connected_circle_data and connected_circle_data.get("enclosed") is True:
                enclosed_neighbors.append((connected_id, connected_circle_data))
        
        # If no enclosed neighbors found, this is unexpected according to Four Color Theorem logic
        if not enclosed_neighbors:
            print(f"WARNING: Node {circle_id} has no enclosed neighbors for swapping red priority!")
            # Ensure the circle is visually red and return priority 4
            self.update_circle_color(circle_id, original_circle_priority)
            return original_circle_priority
        
        # Try each enclosed neighbor until we find one that works
        for neighbor_id, neighbor_data in enclosed_neighbors:
            swap_target_id = neighbor_id
            swap_target_original_priority = neighbor_data["color_priority"]
            
            # Perform the swap
            print(f"DEBUG: Swapping priority 4 from node {circle_id} with priority {swap_target_original_priority} from enclosed node {swap_target_id}")
            self.update_circle_color(circle_id, swap_target_original_priority)
            self.update_circle_color(swap_target_id, original_circle_priority) # Assign red (4) to the target

            # Check for conflicts after the swap
            final_priority_original = self.check_and_resolve_color_conflicts(circle_id)
            final_priority_swapped = self.check_and_resolve_color_conflicts(swap_target_id)

            # If we created a new red node elsewhere during swap, handle it specially
            if self.red_node_id is not None and self.red_node_id != circle_id:
                print(f"WARNING: Swap created a new red node {self.red_node_id}. This will need manual fixing.")
                # Store info about this new problem
                self.next_red_node_id = self.red_node_id
                # Clear current red node ID to complete current fix operation
                self.red_node_id = None

            # If no conflicts arose, we're done
            if final_priority_original == swap_target_original_priority and final_priority_swapped == original_circle_priority:
                return final_priority_original
            
            # Otherwise, try the next neighbor
            print(f"WARNING: Swap with node {swap_target_id} resulted in conflicts. Trying next neighbor.")
            
            # Undo this swap since it didn't work
            self.update_circle_color(circle_id, original_circle_priority)
            self.update_circle_color(swap_target_id, swap_target_original_priority)
        
        # If we get here, no viable swaps were found
        print(f"WARNING: No viable enclosed neighbor found for node {circle_id} to swap with.")
        self.update_circle_color(circle_id, original_circle_priority)
        return original_circle_priority

    def fix_red_node(self):
        """Manually triggered function to fix a red node by swapping with an enclosed neighbor."""
        if self.red_node_id is None:
            return False
            
        # Store the ID and clear the tracking variable
        circle_id = self.red_node_id
        self.red_node_id = None
        
        # Now perform the actual swap using reassign_color_network
        new_priority = self.reassign_color_network(circle_id)
        
        # Hide the fix button and transition back to CREATE mode
        self.app.handle_red_node_fixed()
        
        return new_priority != 4  # Return True if we successfully changed from red

    def update_circle_color(self, circle_id, color_priority):
        """Update a circle's color priority both in data and visually.

        Args:
            circle_id: ID of the circle to update
            color_priority: New color priority to assign

        Returns:
            bool: True if update was successful, False otherwise
        """
        circle = self.app.circle_lookup.get(circle_id)
        if not circle:
            return False

        # Update data - only priority
        circle["color_priority"] = color_priority

        # Get color name from priority for visual update
        color_name = get_color_from_priority(color_priority)

        # Update visual appearance
        self.app.canvas.itemconfig(
            circle["canvas_id"],
            fill=color_name
        )
        
        # Check for adjacent red nodes whenever we assign a red color
        if color_priority == 4:
            self.check_for_adjacent_red_nodes(circle_id)

        # Update debug display if enabled and this circle is active
        if self.app.debug_enabled and (self.app.ui_manager.active_circle_id == circle_id or circle_id in self.app.ui_manager.active_circle_ids):
            self.app.ui_manager.show_debug_info()

        return True

    def check_for_adjacent_red_nodes(self, circle_id):
        """Check if a circle has any adjacent red nodes and log a warning if found.
        
        Args:
            circle_id: ID of the circle to check
        """
        circle = self.app.circle_lookup.get(circle_id)
        if not circle:
            return
            
        connected_circles = circle.get("connected_to", [])
        adjacent_red_nodes = []
        
        for connected_id in connected_circles:
            connected_circle = self.app.circle_lookup.get(connected_id)
            if connected_circle and connected_circle["color_priority"] == 4:
                adjacent_red_nodes.append(connected_id)
                
        if adjacent_red_nodes:
            warning_msg = f"WARNING: Red node {circle_id} is adjacent to other red nodes: {adjacent_red_nodes}"
            print(warning_msg)

    def handle_red_node_creation(self, circle_id):
        """Handle the creation of a red node by showing the fix button and entering adjust mode."""
        print(f"DEBUG: handle_red_node_creation called for circle {circle_id}")
        
        # Store the circle ID for ADJUST mode
        self.app.last_circle_id = circle_id
        
        # IMPORTANT: Exit selection mode first to properly clean up any pending state
        if self.app._mode == ApplicationMode.SELECTION:
            # Complete any pending selection operations
            for indicator_id in self.app.selection_indicators.values():
                self.app.canvas.delete(indicator_id)
            self.app.selection_indicators = {}
            self.app.selected_circles = []
            if self.app.hint_text_id:
                self.app.canvas.delete(self.app.hint_text_id)
                self.app.hint_text_id = None
        
        # Ensure we're completely out of CREATE or SELECTION mode
        if self.app._mode != ApplicationMode.ADJUST:
            print(f"DEBUG: Explicitly switching to ADJUST mode from {self.app._mode}")
            # Unbind current mode events
            self.app.interaction_handler.unbind_mode_events(self.app._mode)
            # Set new mode
            self.app._mode = ApplicationMode.ADJUST
            # Update button text
            if self.app.mode_button:
                self.app.mode_button.config(text="Fix Red")
            # Set up ADJUST mode UI
            self.app.ui_manager.show_edit_hint_text()
            self.app.canvas.config(bg="#FFDDDD")  # Pale pink
            # Bind new mode events AFTER setting the mode to ensure proper setup
            self.app.interaction_handler.bind_mode_events(ApplicationMode.ADJUST)
            # Update connections and show handles
            self.app.connection_manager.show_midpoint_handles()
            self.app._update_enclosure_status()
            
            # Ensure the red node is unlocked so it can be moved
            red_node = self.app.circle_lookup.get(circle_id)
            if red_node:
                red_node["locked"] = False
                print(f"DEBUG: Unlocked red node {circle_id} for movement")
            
            # Store the original mode button's command function
            if hasattr(self.app, 'mode_button'):
                # Store original command and replace with fix red command
                original_command = self.app.mode_button['command']
                self.app._stored_mode_button_command = original_command
                self.app.mode_button.config(command=lambda: self.app._focus_after(self.handle_fix_red_node_button))
                
                print("DEBUG: Changed mode button to 'Fix Red'")
            
            # Add a small delay to ensure all UI updates are processed
            self.app.root.after(100, lambda: print("DEBUG: Mode transition complete"))

    def handle_red_node_fixed(self):
        """Handle operations after a red node has been fixed."""
        print("DEBUG: Red node fixed")
        
        # Restore the mode toggle button's original functionality
        if hasattr(self.app, 'mode_button') and hasattr(self.app, '_stored_mode_button_command'):
            # Restore the original command
            self.app.mode_button.config(command=self.app._stored_mode_button_command)
            delattr(self.app, '_stored_mode_button_command')
            print("DEBUG: Restored mode button's original command")
        
        # Check if we have a pending red node to fix
        if self.next_red_node_id is not None:
            # We have another red node that needs fixing
            print(f"DEBUG: Found pending red node {self.next_red_node_id} to fix")
            # Set it as the current red node
            self.red_node_id = self.next_red_node_id
            self.next_red_node_id = None
            # Handle the new red node (stays in ADJUST mode)
            self.handle_red_node_creation(self.red_node_id)
        else:
            # No pending red nodes, return to CREATE mode
            print("DEBUG: Auto transitioning back to CREATE mode")
            self.app._set_application_mode(ApplicationMode.CREATE)
            # Button text will be updated by the mode transition
    
    def handle_fix_red_node_button(self):
        """Handler for the Fix Red button click."""
        if self.fix_red_node():
            # If successful, update the debug info
            if self.app.debug_enabled:
                self.app.ui_manager.show_debug_info()
