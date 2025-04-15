"""
Color Manager for the 4colour project.

This module handles color assignment and color conflict resolution.
"""

from color_utils import get_color_from_priority, find_lowest_available_priority, determine_color_priority_for_connections

class ColorManager:
    """Manages color assignment and conflict resolution."""
    
    def __init__(self, app):
        """Initialize with a reference to the main application.
        
        Args:
            app: The main CanvasApplication instance
        """
        self.app = app
        self.red_node_id = None  # Track the ID of a node that needs color fixing
    
    # No ApplicationMode references in this class, so no fixes needed
    
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
            # Trigger the UI to show the fix button and enter adjust mode
            self.app.handle_red_node_creation(circle_id)
            
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
            # Trigger the UI to show the fix button and enter adjust mode
            self.app.handle_red_node_creation(circle_id)
            
            return new_priority
        
        # Update the circle with the new priority
        circle_data["color_priority"] = new_priority
        
        # Get color name for visual update
        new_color_name = get_color_from_priority(new_priority)
        
        # Update the visual appearance of the circle
        self.app.canvas.itemconfig(circle_data["canvas_id"], fill=new_color_name)
        
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
        
        # Hide the fix button after we're done
        self.app.hide_fix_red_button()
        
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
