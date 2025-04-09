"""
Canvas Application - 4colour project

This module implements a simple drawing canvas using tkinter.
"""

import tkinter as tk
from tkinter import ttk

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
        self.circle_radius = 5
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Create and configure all UI elements."""
        # Create control frame for buttons
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Add resize buttons
        ttk.Button(control_frame, text="+", command=self._increase_canvas_size).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="-", command=self._decrease_canvas_size).pack(side=tk.LEFT, padx=2)
        
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
        
    def _draw_on_click(self, event):
        """Draw a circle at the clicked position.
        
        Args:
            event: Mouse click event containing x and y coordinates
        """
        x, y = event.x, event.y
        circle = self.canvas.create_oval(
            x - self.circle_radius,
            y - self.circle_radius,
            x + self.circle_radius,
            y + self.circle_radius,
            fill="black"
        )
        # Store the coordinates of drawn items
        self.drawn_items.append((x, y))
        
    def _increase_canvas_size(self):
        """Increase the canvas dimensions by 50 pixels."""
        self.canvas_width += 50
        self.canvas_height += 50
        self._resize_canvas()
        
    def _decrease_canvas_size(self):
        """Decrease the canvas dimensions by 50 pixels."""
        # Ensure canvas doesn't get too small
        if self.canvas_width > 100 and self.canvas_height > 100:
            self.canvas_width -= 50
            self.canvas_height -= 50
            self._resize_canvas()
    
    def _resize_canvas(self):
        """Handle canvas resizing, maintaining drawn items."""
        # Configure the canvas with new dimensions
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)
        
        # Clear the canvas
        self.canvas.delete("all")
        
        # Redraw all items
        for x, y in self.drawn_items:
            self.canvas.create_oval(
                x - self.circle_radius, 
                y - self.circle_radius,
                x + self.circle_radius,
                y + self.circle_radius,
                fill="black"
            )

def main():
    """Application entry point."""
    root = tk.Tk()
    app = CanvasApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()