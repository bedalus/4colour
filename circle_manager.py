"""
Circle Manager for the 4colour project.

This module handles circle creation, management and operations.
"""

from app_enums import ApplicationMode  # Import from app_enums instead

class CircleManager:
    """Manages circle operations and data."""
    
    def __init__(self, app):
        """Initialize with a reference to the main application.
        
        Args:
            app: The main CanvasApplication instance
        """
        self.app = app
        
    def get_circle_at_coords(self, x, y):
        """Find a circle at the given coordinates.
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            
        Returns:
            int or None: ID of the circle if found, None otherwise
        """
        for circle in self.app.circles:
            # Calculate distance between click and circle center
            circle_x = circle["x"]
            circle_y = circle["y"]
            distance = ((circle_x - x) ** 2 + (circle_y - y) ** 2) ** 0.5
            
            # If click is within circle radius, return circle ID
            if distance <= self.app.circle_radius:
                return circle["id"]
        
        return None
    
    def remove_circle_by_id(self, circle_id, bypass_lock=False):
        """Removes a circle and all its connections by its ID."""
        circle_data = self.app.circle_lookup.get(circle_id)

        if not circle_data:
            return False

        # Check lock status unless bypassed
        if not bypass_lock and circle_data.get("locked", False):
            return False
            
        # Check fixed status (fixed nodes should generally not be removed this way)
        if circle_data.get("fixed", False):
            return False

        # Remove all connections associated with this circle FIRST
        # Iterate over a copy of the list as remove_connection will modify it
        connections_to_remove = list(circle_data.get("connected_to", []))
        for connected_id in connections_to_remove:
            self.app.connection_manager.remove_connection(circle_id, connected_id)

        # Remove the circle from the canvas
        self.app.canvas.delete(circle_data["canvas_id"])

        # Remove from the main list (find by id)
        original_length = len(self.app.circles)
        self.app.circles = [c for c in self.app.circles if c["id"] != circle_id]

        # Remove from the lookup dictionary
        if circle_id in self.app.circle_lookup:
            del self.app.circle_lookup[circle_id]

        # If this was the last circle placed, reset the reference
        if self.app.last_circle_id == circle_id:
            self.app.last_circle_id = None
            
        # If this was the newly placed circle being cancelled, reset that too
        if self.app.newly_placed_circle_id == circle_id:
             self.app.newly_placed_circle_id = None

        # Update enclosure status as removing a circle might affect it
        self.app._update_enclosure_status() # Phase 14 Trigger Point
        
        return True
