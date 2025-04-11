"""
Connection Manager for the 4colour project.

This module handles connection creation, management, and operations.
"""

from app_enums import ApplicationMode  # Import from app_enums instead

class ConnectionManager:
    """Manages connections between circles."""
    
    def __init__(self, app):
        """Initialize with a reference to the main application.
        
        Args:
            app: The main CanvasApplication instance
        """
        self.app = app
        
    def add_connection(self, from_id, to_id):
        """Add a connection between two circles.
        
        Args:
            from_id: ID of the first circle
            to_id: ID of the second circle
            
        Returns:
            bool: True if connection was made, False otherwise
        """
        from_circle = self.app.circle_lookup.get(from_id)
        to_circle = self.app.circle_lookup.get(to_id)
        
        if not from_circle or not to_circle:
            return False
            
        # Check if connection already exists
        if to_id in from_circle["connected_to"] or from_id in to_circle["connected_to"]:
            return False
        
        # Calculate points for the curved line
        points = self.calculate_curve_points(from_id, to_id)
        if not points:
            return False
            
        # Draw the curved line
        line_id = self.app.canvas.create_line(
            points,  # All points for the curved line
            width=1,
            smooth=True,  # Enable line smoothing for curves
            tags="line"  # Add tag for line
        )
        
        # Ensure the line is below all circles
        self.app.canvas.lower("line")
        
        # Update connection data
        from_circle["connected_to"].append(to_id)
        to_circle["connected_to"].append(from_id)
        
        # Store connection details with default curve values (0,0)
        connection_key = f"{from_id}_{to_id}"
        self.app.connections[connection_key] = {
            "line_id": line_id,
            "from_circle": from_id,
            "to_circle": to_id,
            "curve_X": 0,  # Default: no curve offset in X direction
            "curve_Y": 0   # Default: no curve offset in Y direction
        }
        
        return True
    
    def remove_circle_connections(self, circle_id):
        """Remove all connections for a specific circle.
        
        Args:
            circle_id: ID of the circle whose connections should be removed
        """
        # Get the circle
        circle = self.app.circle_lookup.get(circle_id)
        if not circle:
            return
            
        connected_circles = circle["connected_to"].copy()  # Make a copy to avoid modifying while iterating
        for connected_id in connected_circles:
            connected_circle = self.app.circle_lookup.get(connected_id)
            if connected_circle:
                # Remove this circle from the connected circle's connections
                if circle_id in connected_circle["connected_to"]:
                    connected_circle["connected_to"].remove(circle_id)
                
                # Find and remove the connection line and midpoint handle
                key1 = f"{circle_id}_{connected_id}"
                key2 = f"{connected_id}_{circle_id}"
                
                # Remove the connection from either direction
                connection = self.app.connections.get(key1)
                connection_key = key1
                
                if connection:
                    self.app.canvas.delete(connection["line_id"])
                    del self.app.connections[key1]
                else:
                    connection = self.app.connections.get(key2)
                    connection_key = key2
                    if connection:
                        self.app.canvas.delete(connection["line_id"])
                        del self.app.connections[key2]
                
                # Remove midpoint handle if exists
                if connection_key in self.app.midpoint_handles:
                    self.app.canvas.delete(self.app.midpoint_handles[connection_key])
                    del self.app.midpoint_handles[connection_key]
    
    def calculate_midpoint(self, from_circle, to_circle):
        """Calculate the midpoint between two circles.
        
        Args:
            from_circle: Dictionary containing the first circle's data
            to_circle: Dictionary containing the second circle's data
            
        Returns:
            tuple: (x, y) coordinates of the midpoint
        """
        # Simple midpoint formula: (x1+x2)/2, (y1+y2)/2
        mid_x = (from_circle["x"] + to_circle["x"]) / 2
        mid_y = (from_circle["y"] + to_circle["y"]) / 2
        return (mid_x, mid_y)

    def calculate_curve_points(self, from_id, to_id):
        """Calculate the points needed to draw a curved line between two circles.
        
        Args:
            from_id: ID of the first circle
            to_id: ID of the second circle
            
        Returns:
            list: [x1, y1, midx, midy, x2, y2] coordinates for the curved line
        """
        from_circle = self.app.circle_lookup.get(from_id)
        to_circle = self.app.circle_lookup.get(to_id)
        
        if not from_circle or not to_circle:
            return []
            
        # Get the base midpoint
        mid_x, mid_y = self.calculate_midpoint(from_circle, to_circle)
        
        # Apply the curve offset if any
        curve_x, curve_y = self.get_connection_curve_offset(from_id, to_id)
        mid_x += curve_x
        mid_y += curve_y
        
        # Return coordinates for all three points
        return [
            from_circle["x"], from_circle["y"],  # Start point
            mid_x, mid_y,                       # Middle point with offset
            to_circle["x"], to_circle["y"]      # End point
        ]
        
    def get_connection_curve_offset(self, from_id, to_id):
        """Get the curve offset for a connection between two circles.
        
        Args:
            from_id: ID of the first circle
            to_id: ID of the second circle
            
        Returns:
            tuple: (curve_X, curve_Y) offset values or (0, 0) if not found
        """
        # Check both possible connection key orientations
        key1 = f"{from_id}_{to_id}"
        key2 = f"{to_id}_{from_id}"
        
        connection = self.app.connections.get(key1) or self.app.connections.get(key2)
        if not connection:
            return (0, 0)
            
        # Return the curve offsets, defaulting to 0 if not set
        curve_x = connection.get("curve_X", 0)
        curve_y = connection.get("curve_Y", 0)
        return (curve_x, curve_y)
    
    def update_connection_curve(self, from_id, to_id, curve_x, curve_y):
        """Update the curve offset for a connection.
        
        Args:
            from_id: ID of the first circle
            to_id: ID of the second circle
            curve_x: X offset from the midpoint
            curve_y: Y offset from the midpoint
            
        Returns:
            bool: True if the update was successful, False otherwise
        """
        # Check both possible connection key orientations
        key1 = f"{from_id}_{to_id}"
        key2 = f"{to_id}_{from_id}"
        
        connection = self.app.connections.get(key1) or self.app.connections.get(key2)
        if not connection:
            return False
            
        # Update the curve offsets
        connection["curve_X"] = curve_x
        connection["curve_Y"] = curve_y
        
        # Get the actual connection key used
        connection_key = key1 if key1 in self.app.connections else key2
        
        # Calculate points for the curved line - we need them for the line
        points = self.calculate_curve_points(from_id, to_id)
        if not points or len(points) < 6:
            return False
        
        # Delete and redraw the connection line
        self.app.canvas.delete(connection["line_id"])
        new_line_id = self.app.canvas.create_line(
            points,  # All points for the curved line
            width=1,
            smooth=True,  # Enable line smoothing for curves
            tags="line"  # Add tag for line
        )
        # Ensure new line stays below circles
        self.app.canvas.lower("line")
        
        connection["line_id"] = new_line_id
        
        # If in adjust mode, update the midpoint handle position
        if self.app._mode == ApplicationMode.ADJUST and connection_key in self.app.midpoint_handles:  # Fixed: Using imported ApplicationMode
            # Delete old handle
            self.app.canvas.delete(self.app.midpoint_handles[connection_key])
            
            # Calculate the position for this handle using the new method
            handle_x, handle_y = self.calculate_midpoint_handle_position(from_id, to_id)
            
            # Create new handle at updated position
            handle_id = self.draw_midpoint_handle(connection_key, handle_x, handle_y)
            
            # Update reference
            self.app.midpoint_handles[connection_key] = handle_id
        
        return True

    def draw_midpoint_handle(self, connection_key, x, y):
        """Draw a handle at the midpoint of a connection.
        
        Args:
            connection_key: The key for the connection
            x: X coordinate of the midpoint
            y: Y coordinate of the midpoint
            
        Returns:
            int: Canvas ID of the created handle
        """
        # Draw a small black square at the midpoint with the connection key as part of its tags
        handle_id = self.app.canvas.create_rectangle(
            x - self.app.midpoint_radius,
            y - self.app.midpoint_radius,
            x + self.app.midpoint_radius,
            y + self.app.midpoint_radius,
            fill="black",  # Black square
            outline="white",  # White outline for visibility
            width=1,
            tags=("midpoint_handle", connection_key)
        )
        
        return handle_id
    
    def show_midpoint_handles(self):
        """Show handles at the midpoint of each connection."""
        # Clear any existing handles
        self.hide_midpoint_handles()
        
        # Create handles for all connections
        for connection_key, connection in self.app.connections.items():
            from_id = connection["from_circle"]
            to_id = connection["to_circle"]
            
            # Calculate the position for this handle using the new helper method
            handle_x, handle_y = self.calculate_midpoint_handle_position(from_id, to_id)
            
            # Create the handle
            handle_id = self.draw_midpoint_handle(connection_key, handle_x, handle_y)
            
            # Store reference to the handle
            self.app.midpoint_handles[connection_key] = handle_id

    def calculate_midpoint_handle_position(self, from_id, to_id):
        """Calculate the position for the midpoint handle between two circles.
        
        Args:
            from_id: ID of the first circle
            to_id: ID of the second circle
            
        Returns:
            tuple: (x, y) coordinates for the midpoint handle
        """
        from_circle = self.app.circle_lookup.get(from_id)
        to_circle = self.app.circle_lookup.get(to_id)
        
        if not from_circle or not to_circle:
            return (0, 0)
            
        # Get the base midpoint
        base_mid_x, base_mid_y = self.calculate_midpoint(from_circle, to_circle)
        
        # Apply HALF the curve offset for the handle position
        curve_x, curve_y = self.get_connection_curve_offset(from_id, to_id)
        handle_x = base_mid_x + (curve_x / 2)
        handle_y = base_mid_y + (curve_y / 2)
        
        return (handle_x, handle_y)

    def hide_midpoint_handles(self):
        """Hide all midpoint handles."""
        # Delete all handles from the canvas
        for handle_id in self.app.midpoint_handles.values():
            self.app.canvas.delete(handle_id)
            
        # Clear the dictionary
        self.app.midpoint_handles.clear()

    def update_connections(self, circle_id):
        """Update all lines connected to a circle.
        
        Args:
            circle_id: ID of the circle whose connections should be updated
        """
        circle = self.app.circle_lookup.get(circle_id)
        if not circle:
            return
            
        # Update all connections for this circle
        for connected_id in circle["connected_to"]:
            connected_circle = self.app.circle_lookup.get(connected_id)
            if not connected_circle:
                continue
                
            # Find connection key (could be in either order)
            key1 = f"{circle_id}_{connected_id}"
            key2 = f"{connected_id}_{circle_id}"
            
            connection = self.app.connections.get(key1) or self.app.connections.get(key2)
            if connection:
                # Get the actual connection key used
                connection_key = key1 if key1 in self.app.connections else key2
                
                # Preserve existing curve values
                curve_x = connection.get("curve_X", 0)
                curve_y = connection.get("curve_Y", 0)
                
                # Update connection using these values - this will redraw everything
                self.update_connection_curve(connection["from_circle"], connection["to_circle"], curve_x, curve_y)
