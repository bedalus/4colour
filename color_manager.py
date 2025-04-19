"""
Color Manager for the 4colour project.

This module handles color assignment and color conflict resolution.
"""

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
            self.update_circle_color(circle_id, new_priority)
            self.red_node_id = circle_id
            print(f"DEBUG: Red node {circle_id} created in check_and_resolve_color_conflicts")
            self.app.handle_red_node_creation(circle_id)
            return new_priority
        
        # Update the circle with the new priority and visual appearance
        self.update_circle_color(circle_id, new_priority)
        
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

        # Find an enclosed neighbor to swap color with
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
            print(f"DEBUG: Swapping red node (ID:{circle_id}) with enclosed {get_color_from_priority(swap_target_original_priority)} node (ID:{swap_target_id})")
            self.update_circle_color(circle_id, swap_target_original_priority)
            self.update_circle_color(swap_target_id, original_circle_priority) # Assign red (4) to the target

            # Check for conflicts after the swap
            final_priority_original = self.check_and_resolve_color_conflicts(circle_id)
            final_priority_target = self.check_internal_red_conflict(swap_target_id)
            return final_priority_original
        
        # If we get here, no viable swaps were found
        raise RuntimeError(f"ERROR: No viable enclosed neighbor found for node {circle_id} to swap with.")

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
        
        # Update debug display if enabled and this circle is active
        if self.app.debug_enabled and (self.app.ui_manager.active_circle_id == circle_id or circle_id in self.app.ui_manager.active_circle_ids):
            self.app.ui_manager.show_debug_info()

        return True
        
    def check_internal_red_conflict(self, circle_id):
        """Check if a circle has any adjacent red nodes and log a warning if found.
        
        Args:
            circle_id: ID of the circle to check
            
        Returns:
            int: The current color priority of the circle
        """
        circle = self.app.circle_lookup.get(circle_id)
        if not circle:
            return None
            
        current_priority = circle["color_priority"]
        connected_circles = circle.get("connected_to", [])
        adjacent_red_nodes = []
        
        for connected_id in connected_circles:
            connected_circle = self.app.circle_lookup.get(connected_id)
            if connected_circle and connected_circle["color_priority"] == 4:
                adjacent_red_nodes.append(connected_id)
                
        if adjacent_red_nodes:
            warning_msg = f"UNHANDLED INTERNAL RED CONFLICT: Red node {circle_id} is adjacent to other red nodes: {adjacent_red_nodes}"
            print(warning_msg)
        
        return current_priority

    def handle_red_node_creation(self, circle_id):
        """Handle the creation of a red node by showing the fix button and entering adjust mode."""
        print(f"DEBUG: handle_red_node_creation called for circle {circle_id}")
        
        # Store the circle ID for ADJUST mode
        self.app.last_circle_id = circle_id
        
        # Delegate mode switching to interaction handler
        self.app.interaction_handler.switch_to_red_fix_mode()
        
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
