"""
UI Manager for the 4colour project.

This module manages the UI elements and interactions with the canvas.
"""

import tkinter as tk
import math
from app_enums import ApplicationMode  # Import from app_enums instead

class UIManager:
    """Manages UI elements and display features."""
    
    def __init__(self, app):
        """Initialize with a reference to the main application.
        
        Args:
            app: The main CanvasApplication instance
        """
        self.app = app
        self.warning_text_id = None  # For displaying warnings on canvas
        self.active_circle_id = None
        self.active_circle_ids = []
        
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
        self.app.debug_enabled = not self.app.debug_enabled
        if self.app.debug_enabled:
            self.show_debug_info()
        else:
            # Clear the debug display
            if self.app.debug_text:
                self.app.canvas.delete(self.app.debug_text)
                self.app.debug_text = None
                
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
        
        # Display debug text on the right side of the canvas using a monospaced font
        # Use current canvas dimensions to position text correctly
        self.app.debug_text = self.app.canvas.create_text(
            self.app.canvas_width - 50, 10, 
            text=info_text, 
            anchor=tk.NE,  # Right-align text at the top
            fill="black",
            font=("Courier", 10)  # Use Courier, which is a common monospaced font
        )

    def _format_circle_info(self, circle):
        """Format debug info for a single circle.
        
        Args:
            circle: Circle data dictionary
            
        Returns:
            str: Formatted debug info text with right-justified values
        """
        # Derive color name from priority for display
        from color_utils import get_color_from_priority
        color_name = get_color_from_priority(circle['color_priority'])
        
        # Format ordered connections list if it exists
        ordered_connections_str = "None"
        if "ordered_connections" in circle and circle["ordered_connections"]:
            # Format as clockwise order: 1→2→3
            ordered_connections_str = "→".join(map(str, circle["ordered_connections"]))
        
        # Create individual lines with values and labels
        lines = [
            f"{circle['id']} : Circle ID",
            f"({circle['x']}, {circle['y']}) : Position",
            f"{color_name} (priority: {circle['color_priority']}) : Color",
            f"{', '.join(map(str, circle['connected_to']))} : Connected to",
            f"{ordered_connections_str} : Clockwise order",
            f"{circle['enclosed']} : Enclosed"
        ]
        
        # Calculate maximum line length for right justification
        max_length = max(len(line) for line in lines)
        
        # Right-justify each line by adding leading spaces
        justified_lines = []
        for line in lines:
            justified_lines.append(" " * (max_length - len(line)) + line)
        
        # Join lines into a single string
        return "\n".join(justified_lines)
    
    def show_hint_text(self):
        """Display instructional hint text when in selection mode."""
        # Clear any existing hint text
        if self.app.hint_text_id:
            self.app.canvas.delete(self.app.hint_text_id)
            
        # Create new hint text - use current canvas width for horizontal centering
        self.app.hint_text_id = self.app.canvas.create_text(
            self.app.canvas_width // 2,
            20,
            text="Please select which circles to connect to then press 'y', or press Escape to cancel",
            anchor=tk.N,
            fill="black",
            font=("Arial", 12)
        )
    
    def show_edit_hint_text(self):
        """Display hint text specific to ADJUST mode."""
        # Clear any existing hint text first
        if self.app.hint_text_id:
            self.app.canvas.delete(self.app.hint_text_id)
            self.app.hint_text_id = None
        if self.app.edit_hint_text_id:
            self.app.canvas.delete(self.app.edit_hint_text_id) # Clear previous edit hint

        # Calculate position for the hint text
        canvas_width = self.app.canvas_width
        x_pos = (canvas_width // 2)
        y_pos = 20

        # Create the new hint text for ADJUST mode
        hint = "You may adjust the last node and its connections"
        self.app.edit_hint_text_id = self.app.canvas.create_text(
            x_pos,
            y_pos,
            text=hint,
            anchor=tk.N, # Anchor to the top center
            fill="gray50",
            font=("Arial", 10)
        )
    
    def clear_canvas(self):
        """Clear the canvas and reset application state."""
        # Reset mode button if it's currently in "Fix Red" mode
        if hasattr(self.app, '_stored_mode_button_command') and self.app.mode_button:
            # Restore the original command
            self.app.mode_button.config(command=self.app._stored_mode_button_command)
            delattr(self.app, '_stored_mode_button_command')
            print("DEBUG: Restored mode button's original command after canvas clear")
        
        # Reset any color manager state related to red nodes
        if hasattr(self.app, 'color_manager'):
            self.app.color_manager.red_node_id = None
            self.app.color_manager.next_red_node_id = None
        
        # Clear the canvas - delete all items except fixed nodes/connections
        for item in self.app.canvas.find_all():
            tags = self.app.canvas.gettags(item)
            if 'fixed_circle' not in tags and 'fixed_connection' not in tags:
                self.app.canvas.delete(item)
        
        # Keep fixed nodes/connections, but clear everything else
        self.app.circles = [c for c in self.app.circles if c.get('fixed')]
        
        # Important: Make sure the fixed nodes have clean connection lists
        for circle in self.app.circles:
            circle["connected_to"] = [c for c in circle["connected_to"] if any(fixed_circle["id"] == c for fixed_circle in self.app.circles)]
            circle["ordered_connections"] = circle["connected_to"].copy()
        
        self.app.circle_lookup = {c['id']: c for c in self.app.circles}
        
        # Reset connections, keeping only fixed ones
        fixed_connections = {}
        for key, conn in self.app.connections.items():
            if conn.get('fixed'):
                fixed_connections[key] = conn
        self.app.connections = fixed_connections
        
        # Clear midpoint handles
        self.app.midpoint_handles.clear()
        
        # Reset ID counter but preserve fixed nodes
        self.app.next_id = 1
        
        # Reset other application state
        self.app.last_circle_id = None
        self.app.selected_circles = []
        self.app.selection_indicators = {}
        self.app.highlighted_circle_id = None
        self.app.newly_placed_circle_id = None
        
        # Always reset to CREATE mode
        self.app._set_application_mode(ApplicationMode.CREATE)
        
        # Ensure the boundary state is properly reset and fixed nodes are connected
        if self.app.circles and len(self.app.circles) >= 2:
            # Make sure fixed nodes A and B are connected properly
            if self.app.FIXED_NODE_A_ID in self.app.circle_lookup and self.app.FIXED_NODE_B_ID in self.app.circle_lookup:
                fixed_node_a = self.app.circle_lookup[self.app.FIXED_NODE_A_ID]
                fixed_node_b = self.app.circle_lookup[self.app.FIXED_NODE_B_ID]
                
                # Ensure they're connected to each other
                if self.app.FIXED_NODE_B_ID not in fixed_node_a["connected_to"]:
                    fixed_node_a["connected_to"].append(self.app.FIXED_NODE_B_ID)
                if self.app.FIXED_NODE_A_ID not in fixed_node_b["connected_to"]:
                    fixed_node_b["connected_to"].append(self.app.FIXED_NODE_A_ID)
                    
                # Update the ordered connections
                self.app.connection_manager.update_ordered_connections(self.app.FIXED_NODE_A_ID)
                self.app.connection_manager.update_ordered_connections(self.app.FIXED_NODE_B_ID)
                
                # Ensure the connection exists in the connections dictionary
                connection_key = f"{self.app.FIXED_NODE_A_ID}_{self.app.FIXED_NODE_B_ID}"
                if connection_key not in self.app.connections:
                    # Recreate the connection
                    points = self.app.connection_manager.calculate_curve_points(
                        self.app.FIXED_NODE_A_ID, self.app.FIXED_NODE_B_ID)
                    
                    line_id = self.app.canvas.create_line(
                        points,
                        width=1,
                        smooth=True,
                        tags=("line", "fixed_connection")
                    )
                    
                    self.app.canvas.lower("line")
                    
                    self.app.connections[connection_key] = {
                        "line_id": line_id,
                        "from_circle": self.app.FIXED_NODE_A_ID,
                        "to_circle": self.app.FIXED_NODE_B_ID,
                        "curve_X": 0,
                        "curve_Y": 0,
                        "fixed": True
                    }
        else:
            # If we have no fixed nodes, recreate them
            self.app._initialize_fixed_nodes()
        
        # Update enclosure status for boundary detection
        self.app.boundary_manager.update_enclosure_status()
        
        # Update debug info if enabled
        if self.app.debug_enabled:
            self.show_debug_info()
        
        # Clear the hint text
        if self.app.hint_text_id:
            self.app.canvas.delete(self.app.hint_text_id)
            self.app.hint_text_id = None
            
        # Clear the edit hint text
        if self.app.edit_hint_text_id:
            self.app.canvas.delete(self.app.edit_hint_text_id)
            self.app.edit_hint_text_id = None
        
        # Reset any warnings
        self.clear_warning()

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

    def clear_warning(self):
        """Remove the warning message from the canvas."""
        if self.warning_text_id:
            self.app.canvas.delete(self.warning_text_id)
            self.warning_text_id = None
