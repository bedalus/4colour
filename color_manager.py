"""
Color Manager for the 4colour project.

This module handles colour assignment and colour conflict resolution.
"""

from color_utils import get_color_from_priority, determine_color_priority_for_connections

class ColorManager:
    """Manages colour assignment and conflict resolution."""
    
    def __init__(self, app):
        """Initialize with a reference to the main application."""
        self.app = app
    
    def assign_color_based_on_connections(self, circle_id=None):
        # For new circles or initial assignment, use priority 1 (yellow)
        if circle_id is None:
            return 1
            
        # For existing circles, get its connected circles
        circle = self.app.circle_lookup.get(circle_id)
        if not circle or not circle["connected_to"]:
            # No connections, or circle doesn't exist
            return 1
            
        # Get all colours used by connected circles
        used_priorities = set()
        for connected_id in circle["connected_to"]:
            connected_circle = self.app.circle_lookup.get(connected_id)
            if connected_circle and "color_priority" in connected_circle:
                used_priorities.add(connected_circle["color_priority"])
        
        # Use the colour utility function to determine the appropriate priority
        priority = determine_color_priority_for_connections(used_priorities)
        
        return priority

    def update_circle_color(self, circle_id, color_priority):
        """Update a circle's colour priority both in data and visually."""
        circle = self.app.circle_lookup.get(circle_id)
        if not circle:
            return False

        # Update data - only priority
        circle["color_priority"] = color_priority

        # Get colour name from priority for visual update
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
