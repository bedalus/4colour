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
        """Remove a circle by its ID and cleanup all associated connections.
        
        Args:
            circle_id: ID of the circle to remove
            bypass_lock: Whether to bypass the lock check (for Escape during creation)
            
        Returns:
            bool: True if the circle was successfully removed, False otherwise
        """
        # Get the circle to remove
        circle = self.app.circle_lookup.get(circle_id)
        if not circle:
            return False
            
        # Check if this is a fixed node - prevent removal
        # For locked nodes, only prevent removal if bypass_lock is False
        if circle.get("fixed", False) or (not bypass_lock and circle.get("locked", False)) or circle_id in (self.app.FIXED_NODE_A_ID, self.app.FIXED_NODE_B_ID):
            return False
            
        # First, remove all connections to this circle
        self.app._remove_circle_connections(circle_id)
        
        # Remove the circle's visual representation
        self.app.canvas.delete(circle["canvas_id"])
        
        # Remove the circle from data structures
        self.app.circles = [c for c in self.app.circles if c["id"] != circle_id]
        del self.app.circle_lookup[circle_id]
        
        # Check if this was the last circle and handle special case
        if not self.app.circles:
            self.handle_last_circle_removed()
            return True
        
        # Update debug info if enabled
        if self.app.debug_enabled:
            self.app.ui_manager.show_debug_info()
            
        return True
    
    def handle_last_circle_removed(self):
        """Handle the special case when the last circle is removed."""
        # Switch back to create mode if this was the last circle
        self.app._set_application_mode(ApplicationMode.CREATE)  # Fixed: Using imported ApplicationMode
        # Clear canvas to fully reset the scenario
        self.app.canvas.delete("all")
        self.app.drawn_items.clear()
        self.app.connections.clear()
        self.app.last_circle_id = None
        self.app.next_id = 1
