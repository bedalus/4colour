"""
UI Manager for the 4colour project.

This module handles the UI elements and their behavior.
"""

import tkinter as tk
from app_enums import ApplicationMode  # Import from app_enums instead

class UIManager:
    """Manages the UI components and their operations."""
    
    def __init__(self, app):
        """Initialize with a reference to the main application.
        
        Args:
            app: The main CanvasApplication instance
        """
        self.app = app
        
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
                
    def show_debug_info(self):
        """Display debug information about the most recent circle."""
        # Clear previous debug text
        if self.app.debug_text:
            self.app.canvas.delete(self.app.debug_text)
            
        if not self.app.circles:
            info_text = "No circles drawn yet"
        else:
            latest_circle = self.app.circles[-1]
            # Derive color name from priority for display
            from color_utils import get_color_from_priority
            color_name = get_color_from_priority(latest_circle['color_priority'])
            info_text = (
                f"Circle ID: {latest_circle['id']}\n"
                f"Position: ({latest_circle['x']}, {latest_circle['y']})\n"
                # Display derived color name and priority
                f"Color: {color_name} (priority: {latest_circle['color_priority']})\n"
                f"Connected to: {', '.join(map(str, latest_circle['connected_to']))}"
            )
            
        # Display debug text at the top of the canvas
        self.app.debug_text = self.app.canvas.create_text(
            10, 10, 
            text=info_text, 
            anchor=tk.NW, 
            fill="black",
            font=("Arial", 10)
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
