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
        
        # If all priorities 1-3 are used, handle special case
        if priority == 4:
            self.reassign_color_network(circle_id)
        
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
            # If all lower priorities are used, call network reassignment
            return self.reassign_color_network(circle_id)
        
        # Update the circle with the new priority
        circle_data["color_priority"] = new_priority
        
        # Get color name for visual update
        new_color_name = get_color_from_priority(new_priority)
        
        # Update the visual appearance of the circle
        self.app.canvas.itemconfig(circle_data["canvas_id"], fill=new_color_name)
        
        return new_priority
    
    def reassign_color_network(self, circle_id):
        """
        Reassigns colors in a network when all lower priority colors are used.
        Currently just assigns the highest priority color (red).
        
        Parameters:
            circle_id (int): The ID of the circle to reassign color for
            
        Returns:
            int: The newly assigned color priority (4 for red)
        """
        # For now, this function just assigns red (highest priority)
        new_priority = 4
        # Get color name for visual update
        new_color_name = get_color_from_priority(new_priority)
        
        circle_data = self.app.circle_lookup.get(circle_id)
        if circle_data:
            circle_data["color_priority"] = new_priority
            # Also update visual appearance
            self.app.canvas.itemconfig(circle_data["canvas_id"], fill=new_color_name)
        return new_priority
    
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
        
        # Update debug display if enabled
        if self.app.debug_enabled:
            self.app.ui_manager.show_debug_info()
            
        return True
