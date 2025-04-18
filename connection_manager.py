"""
Connection Manager for the 4colour project.

This module handles connection creation, management, and operations.
"""

import math
from app_enums import ApplicationMode  # Import from app_enums instead

class ConnectionManager:
    """Manages connections between circles."""
    
    def __init__(self, app):
        """Initialize with a reference to the main application.
        
        Args:
            app: The main CanvasApplication instance
        """
        self.app = app
        
    def add_connection(self, from_circle_id, to_circle_id):
        """Adds a connection between two circles."""
        connection_key = self.get_connection_key(from_circle_id, to_circle_id)

        # Prevent duplicate connections
        if connection_key in self.app.connections:
            return

        circle1 = self.app.circle_lookup.get(from_circle_id)
        circle2 = self.app.circle_lookup.get(to_circle_id)

        if not circle1 or not circle2:
            return

        # Update connected_to lists
        if to_circle_id not in circle1.get("connected_to", []):
            circle1.setdefault("connected_to", []).append(to_circle_id)
        else:
            pass
            
        if from_circle_id not in circle2.get("connected_to", []):
             circle2.setdefault("connected_to", []).append(from_circle_id)
        else:
            pass


        # Calculate initial curve points (straight line)
        points = self.calculate_curve_points(from_circle_id, to_circle_id)
        if not points:
             # Attempt to rollback connected_to lists? Maybe not necessary if points fail rarely.
             return 

        # Create the line on canvas
        line_id = self._create_connection_line(points, connection_key)

        # Store connection data
        connection_data = self._update_connection_data(connection_key, from_circle_id, to_circle_id, line_id)
        
        # Verify immediately after adding
        if connection_key in self.app.connections:
             pass
        else:
             pass


        # Update ordered connections for both circles
        self.update_ordered_connections(from_circle_id)
        self.update_ordered_connections(to_circle_id)

        # Create and store midpoint handle if in adjust mode
        if self.app.in_edit_mode:
            self.create_midpoint_handle(connection_key)
            
        # Update enclosure status as connections changing might affect it
        self.app._update_enclosure_status() # Phase 14 Trigger Point
        

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
                
                # Update ordered connections for the connected circle
                self.update_ordered_connections(connected_id)
    
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
        new_line_id = self._create_connection_line(points, connection_key)
        
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
        
        # Update ordered connections for both circles as curve changes affect angles
        self.update_ordered_connections(from_id)
        self.update_ordered_connections(to_id)
        
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
    
    def calculate_tangent_vector(self, circle_id, other_circle_id):
        """Calculate the tangent vector of the curve where it meets the specified circle.
        
        Using quadratic Bezier curve math, where:
        P(t) = (1-t)²P₀ + 2(1-t)tP₁ + t²P₂
        
        The derivative (tangent) at endpoints is:
        At P₀ (t=0): P'(0) = 2(P₁ - P₀)
        At P₂ (t=1): P'(1) = 2(P₂ - P₁)
        
        Args:
            circle_id: ID of the circle to calculate tangent at
            other_circle_id: ID of the other circle in the connection
            
        Returns:
            tuple: (dx, dy) normalized tangent vector or (0, 0) if calculation fails
        """
        # Get both circles
        circle = self.app.circle_lookup.get(circle_id)
        other_circle = self.app.circle_lookup.get(other_circle_id)
        
        if not circle or not other_circle:
            return (0, 0)
        
        # Get circle centers
        cx, cy = circle["x"], circle["y"]
        ox, oy = other_circle["x"], other_circle["y"]
        
        # Calculate the midpoint with curve offset
        curve_x, curve_y = self.get_connection_curve_offset(circle_id, other_circle_id)
        base_mid_x, base_mid_y = self.calculate_midpoint(circle, other_circle)
        mid_x = base_mid_x + curve_x
        mid_y = base_mid_y + curve_y
        
        # Simple model: vector from circle center toward midpoint
        dx = mid_x - cx
        dy = mid_y - cy
        
        # Normalize the vector
        magnitude = math.sqrt(dx*dx + dy*dy)
        if magnitude > 0:
            dx /= magnitude
            dy /= magnitude
        
        return (dx, dy)
    
    def calculate_connection_entry_angle(self, circle_id, other_circle_id):
        """Calculate the angle at which a connection enters a circle.
        
        The angle is measured in degrees clockwise from vertical (North),
        ranging from 0 to 360 degrees.
        
        Args:
            circle_id: ID of the circle to calculate angle for
            other_circle_id: ID of the other circle in the connection
            
        Returns:
            float: Angle in degrees (0-360) or 0 if calculation fails
        """
        # Get the tangent vector (pointing outward from circle)
        dx, dy = self.calculate_tangent_vector(circle_id, other_circle_id)
        
        if dx == 0 and dy == 0:
            return 0
        
        # For entry angle, we need the opposite direction (inward)
        dx = -dx
        dy = -dy
        
        # In Tkinter, positive y is downward, so we need to flip the y-component
        # to convert to standard angle measurement
        # atan2(dx, -dy) gives angle clockwise from North (0,0) is top-left
        angle_rad = math.atan2(dx, -dy)
        angle_deg = angle_rad * (180 / math.pi)
        
        # Ensure angle is between 0 and 360
        return angle_deg % 360

    def is_entry_angle_too_close(self, node_id, other_node_id, min_angle=2):
        """
        Check if the entry angle between the connection (node_id, other_node_id)
        and any other connection at node_id is within min_angle degrees.
        Returns True if a violation is found, otherwise False.
        """
        this_angle = self.calculate_connection_entry_angle(node_id, other_node_id)
        for other_id in self.app.circle_lookup[node_id]["connected_to"]:
            if other_id == other_node_id:
                continue
            angle = self.calculate_connection_entry_angle(node_id, other_id)
            diff = abs((this_angle - angle + 180) % 360 - 180)
            if diff < min_angle:
                return True
        return False
    
    def get_connection_key(self, circle1_id, circle2_id):
        """Get a consistent key for a connection between two circles.
        
        Args:
            circle1_id: ID of the first circle
            circle2_id: ID of the second circle
            
        Returns:
            str: Connection key in format "smaller_id_larger_id"
        """
        # Always put the smaller ID first for consistency
        if circle1_id < circle2_id:
            return f"{circle1_id}_{circle2_id}"
        else:
            return f"{circle2_id}_{circle1_id}"

    def update_ordered_connections(self, circle_id):
        """Update the ordered list of connections for a circle based on entry angles.
        
        This orders connections clockwise around the circle starting from North (0 degrees)
        and ensures the ordering remains consistent even when connections are modified.
        
        Args:
            circle_id: ID of the circle to update ordering for
        """
        circle = self.app.circle_lookup.get(circle_id)
        if not circle:
            return
        
        if not circle["connected_to"]:
            # No connections, clear the ordered list
            circle["ordered_connections"] = []
            return
        
        # Create list of tuples with (connected_id, angle) for sorting
        connection_angles = []
        for connected_id in circle["connected_to"]:
            angle = self.calculate_connection_entry_angle(circle_id, connected_id)
            connection_angles.append((connected_id, angle))
        
        # Sort by angle (ascending, 0-360 degrees clockwise from North)
        connection_angles.sort(key=lambda x: x[1])
        
        # Extract just the connection IDs in the sorted order
        ordered_connections = [conn_id for conn_id, _ in connection_angles]
        
        # Update the circle's ordered_connections list
        circle["ordered_connections"] = ordered_connections

    def calculate_corrected_angle(self, circle, neighbor_id):
        """Calculate angle between circles with correction for inverted y-axis.
        
        Args:
            circle: Dictionary containing the source circle's data
            neighbor_id: ID of the neighboring circle
            
        Returns:
            float: Corrected angle in degrees (0-360)
        """
        neighbor = self.app.circle_lookup.get(neighbor_id)
        if not neighbor:
            return 0
            
        # Get vector components
        dx = neighbor['x'] - circle['x']
        dy = neighbor['y'] - circle['y']
        
        # Account for any curve offset
        curve_x, curve_y = self.get_connection_curve_offset(
            circle['id'], 
            neighbor_id
        )
        
        # Adjust vector by half the curve offset
        dx += curve_x / 2
        dy += curve_y / 2
        
        # Calculate angle with correction for inverted y-axis
        # atan2 with -dy to flip the y-axis back to mathematical convention
        angle_rad = math.atan2(dx, -dy)  # Note: swapped order and negated dy
        angle_deg = math.degrees(angle_rad)
        
        # Normalize to 0-360 range, maintaining clockwise orientation
        return (angle_deg) % 360

    def has_angle_violations(self):
        """Check if any connections currently have angle violations."""
        for connection_key, connection in self.app.connections.items():
            from_id = connection["from_circle"]
            to_id = connection["to_circle"]
            if (self.is_entry_angle_too_close(from_id, to_id, min_angle=2) or
                self.is_entry_angle_too_close(to_id, from_id, min_angle=2)):
                return True
        return False

    def remove_connection(self, circle1_id, circle2_id):
        """Removes a connection between two circles and cleans up associated data."""
        connection_key = self.get_connection_key(circle1_id, circle2_id)

        connection = self.app.connections.get(connection_key)
        if not connection:
            return

        # Remove canvas items first
        if "line_id" in connection:
            self.app.canvas.delete(connection["line_id"])
        if connection_key in self.app.midpoint_handles:
            self.app.canvas.delete(self.app.midpoint_handles[connection_key])
            del self.app.midpoint_handles[connection_key]

        # Remove from the main connections dictionary
        if connection_key in self.app.connections:
            del self.app.connections[connection_key]
        else:
            pass


        # Remove references from both circles' connected_to lists
        circle1 = self.app.circle_lookup.get(circle1_id)
        circle2 = self.app.circle_lookup.get(circle2_id)

        if circle1:            
            if circle2_id in circle1.get("connected_to", []):
                circle1["connected_to"].remove(circle2_id)
            else:
                pass


        if circle2:
            if circle1_id in circle2.get("connected_to", []):
                circle2["connected_to"].remove(circle1_id)
            else:
                pass


        # Update ordered connections for both circles after removal
        if circle1:
            self.update_ordered_connections(circle1_id)
        if circle2:
            self.update_ordered_connections(circle2_id)
            
        # Update enclosure status as connections changing might affect it
        self.app._update_enclosure_status() # Phase 14 Trigger Point

    def _create_connection_line(self, points, connection_key=None):
        """Create a line on canvas for a connection.
        
        Args:
            points: List of coordinates for the line
            connection_key: Optional connection key for debugging
            
        Returns:
            int: Canvas ID of the created line
        """
        line_id = self.app.canvas.create_line(
            points,
            width=1,
            smooth=True,
            tags="line",
            fill="black"
        )
        self.app.canvas.lower(line_id)  # Ensure line is below circles
        return line_id

    def _update_connection_data(self, connection_key, from_id, to_id, line_id, curve_x=0, curve_y=0):
        """Update or create connection data in the connections dictionary.
        
        Args:
            connection_key: The unique key for this connection
            from_id: ID of the first circle
            to_id: ID of the second circle
            line_id: Canvas ID for the connection line
            curve_x: X offset for curve control point
            curve_y: Y offset for curve control point
            
        Returns:
            dict: The connection data that was stored
        """
        connection_data = {
            "line_id": line_id,
            "from_circle": from_id,
            "to_circle": to_id,
            "curve_X": curve_x,
            "curve_Y": curve_y,
            "locked": False  # Phase 16: Lock elements outside ADJUST mode
        }
        
        self.app.connections[connection_key] = connection_data
        return connection_data
