"""
Canvas Application - 4colour project

This module implements a simple drawing canvas using tkinter.
"""

import tkinter as tk
from tkinter import ttk
import random

class CanvasApplication:
    """Main application class for the drawing canvas."""
    
    def __init__(self, root):
        """Initialize the application with the main window.
        
        Args:
            root: The tkinter root window
        """
        self.root = root
        self.root.title("4colour Canvas")
        self.root.geometry("800x600")
        
        # Initialize canvas dimensions
        self.canvas_width = 700
        self.canvas_height = 500
        self.circle_radius = 10
        
        # Available colors for circles
        self.available_colors = ["green", "blue", "red", "yellow"]
        
        # Store circle data
        self.circles = []
        self.next_id = 1
        self.last_circle_id = None
        
        # Dictionary for quick circle lookup by ID
        self.circle_lookup = {}
        
        # Dictionary to store connection information
        self.connections = {}
        
        # Debug overlay
        self.debug_enabled = False
        self.debug_text = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Create and configure all UI elements."""
        # Create control frame for buttons
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Add clear canvas button
        ttk.Button(control_frame, text="Clear Canvas", command=self._clear_canvas).pack(side=tk.LEFT, padx=2)
        
        # Add debug button
        ttk.Button(control_frame, text="Debug Info", command=self._toggle_debug).pack(side=tk.LEFT, padx=2)
        
        # Create canvas for drawing
        self.canvas = tk.Canvas(
            self.root, 
            width=self.canvas_width, 
            height=self.canvas_height,
            bg="white",
            bd=2,
            relief=tk.SUNKEN
        )
        self.canvas.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self._draw_on_click)
        
        # Store drawn items for potential resize handling
        self.drawn_items = []
        
    def _get_random_color(self):
        """Return a random color from the available colors.
        
        Returns:
            str: A randomly selected color name
        """
        return random.choice(self.available_colors)
        
    def _draw_on_click(self, event):
        """Draw a circle at the clicked position.
        
        Args:
            event: Mouse click event containing x and y coordinates
        """
        x, y = event.x, event.y
        color = self._get_random_color()
        
        # Create the circle on canvas
        circle_id = self.canvas.create_oval(
            x - self.circle_radius,
            y - self.circle_radius,
            x + self.circle_radius,
            y + self.circle_radius,
            fill=color,
            outline="black"
        )
        
        # Store circle data
        circle_data = {
            "id": self.next_id,
            "canvas_id": circle_id,
            "x": x,
            "y": y,
            "color": color,
            "connected_to": []  # This remains a list that can grow indefinitely
        }
        
        # Connect to previous circle if it exists
        if self.last_circle_id is not None:
            last_circle = self.circle_lookup.get(self.last_circle_id)
            if last_circle:
                # Draw a line connecting this circle to the previous one
                line_id = self.canvas.create_line(
                    last_circle["x"], 
                    last_circle["y"], 
                    x, 
                    y, 
                    width=1
                )
                
                # Update connection data
                circle_data["connected_to"].append(self.last_circle_id)
                last_circle["connected_to"].append(self.next_id)
                
                # Store the connection details
                connection_key = f"{self.next_id}_{self.last_circle_id}"
                self.connections[connection_key] = {
                    "line_id": line_id,
                    "from_circle": self.next_id,
                    "to_circle": self.last_circle_id
                }
        
        # Add circle to the list and lookup dictionary
        self.circles.append(circle_data)
        self.circle_lookup[self.next_id] = circle_data
        self.last_circle_id = self.next_id
        self.next_id += 1
        
        # Store the coordinates of drawn items (for compatibility with existing code)
        self.drawn_items.append((x, y))
        
        # Update debug display if enabled
        if self.debug_enabled:
            self._show_debug_info()
            
    def _clear_canvas(self):
        """Clear all items from the canvas."""
        self.canvas.delete("all")
        self.drawn_items.clear()
        self.circles.clear()
        self.circle_lookup.clear()  # Clear the lookup dictionary
        self.connections.clear()    # Clear connections data
        self.last_circle_id = None
        self.next_id = 1
        
        # Clear debug display
        if self.debug_text:
            self.debug_text = None
            
    def _toggle_debug(self):
        """Toggle the debug information display."""
        self.debug_enabled = not self.debug_enabled
        if self.debug_enabled:
            self._show_debug_info()
        else:
            # Clear the debug display
            if self.debug_text:
                self.canvas.delete(self.debug_text)
                self.debug_text = None
                
    def _show_debug_info(self):
        """Display debug information about the most recent circle."""
        # Clear previous debug text
        if self.debug_text:
            self.canvas.delete(self.debug_text)
            
        if not self.circles:
            info_text = "No circles drawn yet"
        else:
            latest_circle = self.circles[-1]
            info_text = (
                f"Circle ID: {latest_circle['id']}\n"
                f"Position: ({latest_circle['x']}, {latest_circle['y']})\n"
                f"Color: {latest_circle['color']}\n"
                f"Connected to: {', '.join(map(str, latest_circle['connected_to']))}"
            )
            
        # Display debug text at the top of the canvas
        self.debug_text = self.canvas.create_text(
            10, 10, 
            text=info_text, 
            anchor=tk.NW, 
            fill="black",
            font=("Arial", 10)
        )
        
    def add_connection(self, from_id, to_id):
        """Add a connection between two circles.
        
        Args:
            from_id: ID of the first circle
            to_id: ID of the second circle
            
        Returns:
            bool: True if connection was made, False otherwise
        """
        from_circle = self.circle_lookup.get(from_id)
        to_circle = self.circle_lookup.get(to_id)
        
        if not from_circle or not to_circle:
            return False
            
        # Check if connection already exists
        if to_id in from_circle["connected_to"] or from_id in to_circle["connected_to"]:
            return False
            
        # Draw the line
        line_id = self.canvas.create_line(
            from_circle["x"], from_circle["y"], 
            to_circle["x"], to_circle["y"], 
            width=1
        )
        
        # Update connection data
        from_circle["connected_to"].append(to_id)
        to_circle["connected_to"].append(from_id)
        
        # Store connection details
        connection_key = f"{from_id}_{to_id}"
        self.connections[connection_key] = {
            "line_id": line_id,
            "from_circle": from_id,
            "to_circle": to_id
        }
        
        return True

def main():
    """Application entry point."""
    root = tk.Tk()
    app = CanvasApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()