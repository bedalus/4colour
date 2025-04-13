"""
UI Manager for the 4colour project.

This module handles the UI elements and their behavior.
"""

import tkinter as tk
import math
from app_enums import ApplicationMode  # Import from app_enums instead

class UIManager:
    """Manages the UI components and their operations."""
    
    def __init__(self, app):
        """Initialize with a reference to the main application.
        
        Args:
            app: The main CanvasApplication instance
        """
        self.app = app
        self.active_circle_id = None  # Add this line
        self.active_circle_ids = []  # Change from single ID to list
        
    def focus_after(self, command_func):
        """Execute a command and then set focus to the debug button.
        
        Args:
            command_func: The command function to execute
        """
        # Execute the original command
        command_func()
        
        # Set focus to the debug button
        if hasattr(self.app, 'debug_button'):
            self.app.debug_button.focus_set()
    
    def toggle_debug(self):
        """Toggle the debug information display."""
        # Don't allow toggling debug while in adjust mode
        if self.app._mode == ApplicationMode.ADJUST:  # Fixed: Using imported ApplicationMode
            return

        self.app.debug_enabled = not self.app.debug_enabled
        if self.app.debug_enabled:
            self.show_debug_info()
        else:
            # Clear the debug display
            if self.app.debug_text:
                self.app.canvas.delete(self.app.debug_text)
                self.app.debug_text = None
                
    def set_active_circle(self, circle_id):
        """Set the ID of the circle to display debug info for.
        
        Args:
            circle_id: ID of the circle to focus on
        """
        self.active_circle_id = circle_id

    def set_active_circles(self, *circle_ids):
        """Set the IDs of circles to display debug info for.
        
        Args:
            *circle_ids: Variable number of circle IDs to focus on
        """
        self.active_circle_ids = list(circle_ids)
    
    def show_debug_info(self):
        """Display debug information about the most recent circle."""
        # Clear previous debug text
        if self.app.debug_text:
            self.app.canvas.delete(self.app.debug_text)
            
        if not self.app.circles:
            info_text = "No circles drawn yet"
        else:
            circles_info = []
            
            # Show active circles if set, otherwise latest circle
            if self.active_circle_ids:
                for circle_id in self.active_circle_ids:
                    if circle_id in self.app.circle_lookup:
                        circle = self.app.circle_lookup[circle_id]
                        circles_info.append(self._format_circle_info(circle))
            elif self.app.circles:
                latest_circle = self.app.circles[-1]
                circles_info.append(self._format_circle_info(latest_circle))

            info_text = "\n\n".join(circles_info)  # Separate multiple circle infos with blank line
            
            self.active_circle_ids = []  # Reset after showing
            
        # Display debug text at the top of the canvas
        self.app.debug_text = self.app.canvas.create_text(
            10, 10, 
            text=info_text, 
            anchor=tk.NW, 
            fill="black",
            font=("Arial", 10)
        )

    def _format_circle_info(self, circle):
        """Format debug info for a single circle.
        
        Args:
            circle: Circle data dictionary
            
        Returns:
            str: Formatted debug info text
        """
        # Derive color name from priority for display
        from color_utils import get_color_from_priority
        color_name = get_color_from_priority(circle['color_priority'])
        
        # Format ordered connections list if it exists
        ordered_connections_str = "None"
        if "ordered_connections" in circle and circle["ordered_connections"]:
            # Format as clockwise order: 1→2→3
            ordered_connections_str = "→".join(map(str, circle["ordered_connections"]))
        
        return (
            f"Circle ID: {circle['id']}\n"
            f"Position: ({circle['x']}, {circle['y']})\n"
            f"Color: {color_name} (priority: {circle['color_priority']})\n"
            f"Connected to: {', '.join(map(str, circle['connected_to']))}\n"
            f"Clockwise order: {ordered_connections_str}\n"
            f"Enclosed: {circle['enclosed']}"
        )
    
    def show_hint_text(self):
        """Display instructional hint text when in selection mode."""
        # Clear any existing hint text
        if self.app.hint_text_id:
            self.app.canvas.delete(self.app.hint_text_id)
            
        # Create new hint text
        self.app.hint_text_id = self.app.canvas.create_text(
            self.app.canvas_width // 2,
            20,
            text="Please select which circles to connect to then press 'y'",
            anchor=tk.N,
            fill="black",
            font=("Arial", 12)
        )
    
    def show_edit_hint_text(self):
        """Display instructional hint text for adjust mode."""
        # Clear any existing hint text
        if self.app.hint_text_id:
            self.app.canvas.delete(self.app.hint_text_id)
            self.app.hint_text_id = None
        
        if self.app.edit_hint_text_id:
            self.app.canvas.delete(self.app.edit_hint_text_id)
            
        # Create new adjust hint text - positioned slightly to the right to avoid debug text
        self.app.edit_hint_text_id = self.app.canvas.create_text(
            (self.app.canvas_width // 2) + 20,  # Moved 20 pixels to the right
            20,
            text="Click-and-drag to move, right click to remove",
            anchor=tk.N,
            fill="black",
            font=("Arial", 12)
        )
    
    def clear_canvas(self):
        """Clear all items from the canvas."""
        # Don't allow clearing the canvas while in adjust mode
        if self.app._mode == ApplicationMode.ADJUST:  # Fixed: Using imported ApplicationMode
            return

        # More efficient to just clear everything at once
        self.app.canvas.delete("all")
        self.app.drawn_items.clear()
        self.app.circles.clear()
        self.app.circle_lookup.clear()
        self.app.connections.clear()
        self.app.midpoint_handles.clear()
        self.app.last_circle_id = None
        self.app.next_id = 1
        
        # Clear debug display
        if self.app.debug_text:
            self.app.debug_text = None

    def draw_angle_visualization_line(self, circle_id, other_circle_id, angle, connection_key=None):
        """Draw a visualization line showing the angle a connection enters a circle.
        
        Args:
            circle_id: ID of the circle to visualize angle for
            other_circle_id: ID of the other circle in the connection
            angle: Entry angle in degrees (0-360, clockwise from North)
            connection_key: Optional pre-computed connection key to avoid recalculation
            
        Returns:
            int: Canvas ID of the created visualization line
        """
        # Get the circle data
        circle = self.app.circle_lookup.get(circle_id)
        if not circle:
            return None
        
        # Get the circle center
        cx, cy = circle["x"], circle["y"]
        
        # Calculate the endpoint using trigonometry
        # Convert angle to radians for math functions
        angle_rad = math.radians(angle)
        # Multiply radius by 3 for better visualization
        length = 3 * self.app.circle_radius
        
        # Calculate endpoint using trigonometric functions
        # sin(angle) gives x component, cos(angle) gives y component
        # Negate cos since y increases downward in Tkinter
        x2 = cx + length * math.sin(angle_rad)
        y2 = cy - length * math.cos(angle_rad)
        
        # Use provided connection_key or calculate it if not provided
        if connection_key is None:
            connection_key = self.app.connection_manager.get_connection_key(circle_id, other_circle_id)
        
        # Draw the line
        line_id = self.app.canvas.create_line(
            cx, cy, x2, y2,
            fill="gray50",
            width=1,
            dash=(4, 2),  # Dashed line for better visibility
            tags=("angle_viz", f"angle_{connection_key}")
        )
        
        return line_id
    
    def draw_connection_angle_visualizations(self, connection_key):
        """Draw visualization lines for both circles in a connection.
        
        Args:
            connection_key: Key identifying the connection (e.g. "1_2")
            
        Returns:
            list: List of canvas IDs for the created visualization lines
        """
        # Extract circle IDs from the connection key
        try:
            parts = connection_key.split("_")
            if len(parts) != 2:
                return []
            
            circle1_id = int(parts[0])
            circle2_id = int(parts[1])
        except (ValueError, AttributeError):
            return []
        
        viz_ids = []
        
        # Calculate the angle for the first circle
        angle1 = self.app.connection_manager.calculate_connection_entry_angle(circle1_id, circle2_id)
        line_id1 = self.draw_angle_visualization_line(circle1_id, circle2_id, angle1, connection_key)
        if line_id1:
            viz_ids.append(line_id1)
        
        # Calculate the angle for the second circle
        angle2 = self.app.connection_manager.calculate_connection_entry_angle(circle2_id, circle1_id)
        line_id2 = self.draw_angle_visualization_line(circle2_id, circle1_id, angle2, connection_key)
        if line_id2:
            viz_ids.append(line_id2)
        
        return viz_ids
    
    def clear_angle_visualizations(self):
        """Remove all angle visualization lines from the canvas."""
        self.app.canvas.delete("angle_viz")
