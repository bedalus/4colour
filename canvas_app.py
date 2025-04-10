"""
Canvas Application - 4colour project

This module implements a simple drawing canvas using tkinter.
"""

import tkinter as tk
from tkinter import ttk
import random
from enum import Enum, auto

class ApplicationMode(Enum):
    """Enum representing the different modes of the application."""
    CREATE = auto()  # Renamed from NORMAL to better match UI terminology
    SELECTION = auto()
    ADJUST = auto()  # Renamed from EDIT to match UI terminology

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
        self.canvas_width = 800
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
        
        # Selection mode properties
        self.selected_circles = []
        self.selection_indicators = {}
        self.hint_text_id = None
        self.newly_placed_circle_id = None
        
        # Edit mode properties
        self.dragged_circle_id = None
        self.edit_hint_text_id = None
        
        # Current application mode
        self._mode = ApplicationMode.CREATE  # Changed default mode name
        
        # Store reference to mode toggle button
        self.mode_button = None
        
        # Keep track of bound events for cleanup
        self._bound_events = {
            ApplicationMode.CREATE: False,
            ApplicationMode.SELECTION: False,
            ApplicationMode.ADJUST: False
        }
        
        self._setup_ui()

    def _set_application_mode(self, new_mode):
        """Set the application mode and handle all related state transitions.
        
        Args:
            new_mode: The ApplicationMode to switch to
        """
        # Validate the mode transition
        if new_mode == self._mode:
            return
            
        # Don't allow transition to ADJUST mode from SELECTION mode
        if self._mode == ApplicationMode.SELECTION and new_mode == ApplicationMode.ADJUST:
            return
        
        # First clean up the current mode
        if self._mode == ApplicationMode.SELECTION:
            # Clear selections
            for indicator_id in self.selection_indicators.values():
                self.canvas.delete(indicator_id)
            self.selection_indicators = {}
            self.selected_circles = []
            if self.hint_text_id:
                self.canvas.delete(self.hint_text_id)
                self.hint_text_id = None
                
        elif self._mode == ApplicationMode.ADJUST:  # Updated name
            # Clear adjust mode state
            self.dragged_circle_id = None
            if self.edit_hint_text_id:
                self.canvas.delete(self.edit_hint_text_id)
                self.edit_hint_text_id = None
            # Reset canvas background color when exiting ADJUST mode
            self.canvas.config(bg="white")

        # Unbind events for the current mode
        self._unbind_mode_events(self._mode)

        # Set the new mode
        self._mode = new_mode
        
        # Update the button text based on current mode
        if self.mode_button:
            if self._mode == ApplicationMode.ADJUST:
                self.mode_button.config(text="Engage create mode")
            else:
                self.mode_button.config(text="Engage adjust mode")
        
        # Bind events for the new mode
        self._bind_mode_events(new_mode)
        
        # Setup additional mode-specific UI elements
        if new_mode == ApplicationMode.ADJUST:
            self._show_edit_hint_text()
            # Set canvas background to pale pink in ADJUST mode
            self.canvas.config(bg="#FFEEEE")  # Pale pink

    def _bind_mode_events(self, mode):
        """Bind the appropriate events for the given mode.
        
        Args:
            mode: The ApplicationMode to bind events for
        """
        if mode == ApplicationMode.CREATE:
            self._bind_create_mode_events()
        elif mode == ApplicationMode.SELECTION:
            self._bind_selection_mode_events()
        elif mode == ApplicationMode.ADJUST:
            self._bind_adjust_mode_events()

    def _unbind_mode_events(self, mode):
        """Unbind the events for the given mode.
        
        Args:
            mode: The ApplicationMode to unbind events for
        """
        if mode == ApplicationMode.CREATE:
            self._unbind_create_mode_events()
        elif mode == ApplicationMode.SELECTION:
            self._unbind_selection_mode_events()
        elif mode == ApplicationMode.ADJUST:
            self._unbind_adjust_mode_events()

    def _bind_create_mode_events(self):
        """Bind events for create mode."""
        if not self._bound_events[ApplicationMode.CREATE]:
            self.canvas.bind("<Button-1>", self._draw_on_click)
            self._bound_events[ApplicationMode.CREATE] = True

    def _unbind_create_mode_events(self):
        """Unbind events for create mode."""
        if self._bound_events[ApplicationMode.CREATE]:
            self.canvas.unbind("<Button-1>")
            self._bound_events[ApplicationMode.CREATE] = False

    def _bind_selection_mode_events(self):
        """Bind events for selection mode."""
        if not self._bound_events[ApplicationMode.SELECTION]:
            self.canvas.bind("<Button-1>", self._draw_on_click)  # Uses same draw function but in selection mode
            self.root.bind("<y>", self._confirm_selection)
            self._bound_events[ApplicationMode.SELECTION] = True

    def _unbind_selection_mode_events(self):
        """Unbind events for selection mode."""
        if self._bound_events[ApplicationMode.SELECTION]:
            self.canvas.unbind("<Button-1>")
            self.root.unbind("<y>")
            self._bound_events[ApplicationMode.SELECTION] = False

    def _bind_adjust_mode_events(self):
        """Bind events for adjust mode."""
        if not self._bound_events[ApplicationMode.ADJUST]:
            self.canvas.bind("<Button-1>", self._start_drag)
            self.canvas.bind("<B1-Motion>", self._drag_circle)
            self.canvas.bind("<ButtonRelease-1>", self._end_drag)
            self.canvas.bind("<Button-3>", self._remove_circle)
            self._bound_events[ApplicationMode.ADJUST] = True

    def _unbind_adjust_mode_events(self):
        """Unbind events for adjust mode."""
        if self._bound_events[ApplicationMode.ADJUST]:
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")
            self.canvas.unbind("<Button-3>")
            self._bound_events[ApplicationMode.ADJUST] = False

    @property
    def in_edit_mode(self):
        """Whether the application is in adjust mode (legacy name for compatibility)."""
        return self._mode == ApplicationMode.ADJUST
    
    @in_edit_mode.setter
    def in_edit_mode(self, value):
        """Set adjust mode state (legacy name for compatibility)."""
        if value:
            self._set_application_mode(ApplicationMode.ADJUST)
        else:
            self._set_application_mode(ApplicationMode.CREATE)
            
    @property
    def in_selection_mode(self):
        """Whether the application is in selection mode."""
        return self._mode == ApplicationMode.SELECTION
        
    @in_selection_mode.setter
    def in_selection_mode(self, value):
        """Set selection mode state."""
        if value:
            self._set_application_mode(ApplicationMode.SELECTION)
        else:
            if self._mode == ApplicationMode.SELECTION:
                self._set_application_mode(ApplicationMode.CREATE)

    def _setup_ui(self):
        """Create and configure all UI elements."""
        # Create control frame for buttons
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Add clear canvas button with wrapped command
        ttk.Button(control_frame, text="Clear Canvas", 
                   command=lambda: self._focus_after(self._clear_canvas)).pack(side=tk.LEFT, padx=2)
        
        # Add debug button - store reference
        self.debug_button = ttk.Button(control_frame, text="Debug Info", 
                                      command=lambda: self._focus_after(self._toggle_debug))
        self.debug_button.pack(side=tk.LEFT, padx=2)
        
        # Add mode toggle button - store reference and set initial text
        self.mode_button = ttk.Button(control_frame, text="Engage adjust mode", 
                                     command=lambda: self._focus_after(self._toggle_mode))
        self.mode_button.pack(side=tk.LEFT, padx=2)
        
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
        
        # Initialize the event tracking dictionary
        self._bound_events = {
            ApplicationMode.CREATE: False,
            ApplicationMode.SELECTION: False,
            ApplicationMode.ADJUST: False
        }
        
        # Initialize bindings for create mode - explicitly bind to pass tests 
        self.canvas.bind("<Button-1>", self._draw_on_click)
        self._bound_events[ApplicationMode.CREATE] = True
        
        # Store drawn items for potential resize handling
        self.drawn_items = []
        
    def _focus_after(self, command_func):
        """Execute a command and then set focus to the debug button.
        
        Args:
            command_func: The command function to execute
        """
        # Execute the original command
        command_func()
        
        # Set focus to the debug button
        if hasattr(self, 'debug_button'):
            self.debug_button.focus_set()

    def _get_random_color(self):
        """Return a random color from the available colors.
        
        Returns:
            str: A randomly selected color name
        """
        return random.choice(self.available_colors)
        
    def _draw_on_click(self, event):
        """Draw a circle at the clicked position or select an existing circle.
        
        Args:
            event: Mouse click event containing x and y coordinates
        """
        x, y = event.x, event.y
        
        # Selection mode: try to select an existing circle
        if self.in_selection_mode:
            circle_id = self.get_circle_at_coords(x, y)
            if circle_id is not None:
                self._toggle_circle_selection(circle_id)
            return
            
        # Normal mode: draw a new circle
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
            "connected_to": []
        }
        
        # Add circle to the list and lookup dictionary
        self.circles.append(circle_data)
        self.circle_lookup[self.next_id] = circle_data
        
        # Special case: If this is the first circle, just add it
        if self.last_circle_id is None:
            self.last_circle_id = self.next_id
            self.next_id += 1
            self.drawn_items.append((x, y))
            
            # Update debug display if enabled
            if self.debug_enabled:
                self._show_debug_info()
            return
            
        # For subsequent circles:
        self.newly_placed_circle_id = self.next_id  # Store the new circle's ID
        self.next_id += 1
        self.drawn_items.append((x, y))
        
        # Enter selection mode
        self.in_selection_mode = True
        self._show_hint_text()
        
        # Update debug display if enabled
        if self.debug_enabled:
            self._show_debug_info()
            
    def _clear_canvas(self):
        """Clear all items from the canvas."""
        # Don't allow clearing the canvas while in adjust mode
        if self._mode == ApplicationMode.ADJUST:
            return

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
        # Don't allow toggling debug while in adjust mode
        if self._mode == ApplicationMode.ADJUST:
            return

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

    def get_circle_at_coords(self, x, y):
        """Find a circle at the given coordinates.
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            
        Returns:
            int or None: ID of the circle if found, None otherwise
        """
        for circle in self.circles:
            # Calculate distance between click and circle center
            circle_x = circle["x"]
            circle_y = circle["y"]
            distance = ((circle_x - x) ** 2 + (circle_y - y) ** 2) ** 0.5
            
            # If click is within circle radius, return circle ID
            if distance <= self.circle_radius:
                return circle["id"]
        
        return None

    def _toggle_circle_selection(self, circle_id):
        """Toggle selection status of a circle.
        
        Args:
            circle_id: ID of the circle to toggle selection
        """
        if circle_id == self.newly_placed_circle_id:
            # Can't select the newly placed circle
            return
            
        circle = self.circle_lookup.get(circle_id)
        if not circle:
            return
            
        # Check if circle is already selected
        if circle_id in self.selected_circles:
            # Deselect: remove from list and delete the indicator
            self.selected_circles.remove(circle_id)
            if circle_id in self.selection_indicators:
                self.canvas.delete(self.selection_indicators[circle_id])
                del self.selection_indicators[circle_id]
        else:
            # Select: add to list and draw indicator
            self.selected_circles.append(circle_id)
            # Draw a small line below the circle as selection indicator
            indicator_id = self.canvas.create_line(
                circle["x"] - self.circle_radius,
                circle["y"] + self.circle_radius + 2,
                circle["x"] + self.circle_radius,
                circle["y"] + self.circle_radius + 2,
                width=2,
                fill="black"
            )
            self.selection_indicators[circle_id] = indicator_id

    def _show_hint_text(self):
        """Display instructional hint text when in selection mode."""
        # Clear any existing hint text
        if self.hint_text_id:
            self.canvas.delete(self.hint_text_id)
            
        # Create new hint text
        self.hint_text_id = self.canvas.create_text(
            self.canvas_width // 2,
            20,
            text="Please select which circles to connect to then press 'y'",
            anchor=tk.N,
            fill="black",
            font=("Arial", 12)
        )

    def _confirm_selection(self, event):
        """Handle spacebar press to confirm circle selections.
        
        Args:
            event: Key press event
        """
        if not self.in_selection_mode:
            return
            
        # Connect the newly placed circle to all selected circles
        for circle_id in self.selected_circles:
            self.add_connection(self.newly_placed_circle_id, circle_id)
            
        # Exit selection mode
        self.in_selection_mode = False
        self.last_circle_id = self.newly_placed_circle_id
        self.newly_placed_circle_id = None
        
        # Clear selections
        self.selected_circles = []
        
        # Clear selection indicators
        for indicator_id in self.selection_indicators.values():
            self.canvas.delete(indicator_id)
        self.selection_indicators = {}
        
        # Clear hint text
        if self.hint_text_id:
            self.canvas.delete(self.hint_text_id)
            self.hint_text_id = None
            
        # Update debug info if enabled
        if self.debug_enabled:
            self._show_debug_info()

    def _toggle_mode(self):
        """Toggle between create and adjust modes."""
        # Simply toggle between create and adjust modes
        if self._mode == ApplicationMode.ADJUST:
            self._set_application_mode(ApplicationMode.CREATE)
        elif self._mode == ApplicationMode.CREATE:
            # Only enter adjust mode from create mode, not selection mode
            self._set_application_mode(ApplicationMode.ADJUST)
        # Selection mode can't transition to adjust mode - do nothing
        # This ensures test_toggle_edit_mode_in_selection_mode passes
            
    def _show_edit_hint_text(self):
        """Display instructional hint text for adjust mode."""
        # Clear any existing hint text
        if self.hint_text_id:
            self.canvas.delete(self.hint_text_id)
            self.hint_text_id = None
        
        if self.edit_hint_text_id:
            self.canvas.delete(self.edit_hint_text_id)
            
        # Create new adjust hint text - positioned slightly to the right to avoid debug text
        self.edit_hint_text_id = self.canvas.create_text(
            (self.canvas_width // 2) + 20,  # Moved 20 pixels to the right
            20,
            text="Click-and-drag to move, right click to remove",
            anchor=tk.N,
            fill="black",
            font=("Arial", 12)
        )

    def _start_drag(self, event):
        """Start dragging a circle.
        
        Args:
            event: Mouse press event containing x and y coordinates
        """
        if not self.in_edit_mode:
            return
            
        # Find if a circle was clicked
        circle_id = self.get_circle_at_coords(event.x, event.y)
        if circle_id is not None:
            self.dragged_circle_id = circle_id
            
    def _drag_circle(self, event):
        """Drag a circle to a new position.
        
        Args:
            event: Mouse motion event containing x and y coordinates
        """
        if not self.in_edit_mode or self.dragged_circle_id is None:
            return
            
        # Get the circle being dragged
        circle = self.circle_lookup.get(self.dragged_circle_id)
        if not circle:
            return
            
        # Calculate movement
        dx = event.x - circle["x"]
        dy = event.y - circle["y"]
        
        # Update circle position on canvas
        self.canvas.move(circle["canvas_id"], dx, dy)
        
        # Update circle data
        circle["x"] = event.x
        circle["y"] = event.y
        
        # Update connecting lines in real-time
        self._update_connections(self.dragged_circle_id)
        
        # Update debug info if enabled
        if self.debug_enabled:
            self._show_debug_info()
            
    def _end_drag(self, event):
        """End dragging a circle.
        
        Args:
            event: Mouse release event
        """
        if not self.in_edit_mode or self.dragged_circle_id is None:
            return
            
        # Reset dragged circle ID
        self.dragged_circle_id = None
        
    def _update_connections(self, circle_id):
        """Update all lines connected to a circle.
        
        Args:
            circle_id: ID of the circle whose connections should be updated
        """
        circle = self.circle_lookup.get(circle_id)
        if not circle:
            return
            
        # Update all connections for this circle
        for connected_id in circle["connected_to"]:
            connected_circle = self.circle_lookup.get(connected_id)
            if not connected_circle:
                continue
                
            # Find connection key (could be in either order)
            key1 = f"{circle_id}_{connected_id}"
            key2 = f"{connected_id}_{circle_id}"
            
            connection = self.connections.get(key1) or self.connections.get(key2)
            if connection:
                # Delete the old line
                self.canvas.delete(connection["line_id"])
                
                # Create a new line
                new_line_id = self.canvas.create_line(
                    circle["x"], circle["y"],
                    connected_circle["x"], connected_circle["y"],
                    width=1
                )
                
                # Update connection data
                connection["line_id"] = new_line_id

    def _remove_circle(self, event):
        """Remove a circle when right-clicked in adjust mode.
        
        Args:
            event: Mouse right-click event containing x and y coordinates
        """
        if self._mode != ApplicationMode.ADJUST:
            return
            
        # Find if a circle was right-clicked
        circle_id = self.get_circle_at_coords(event.x, event.y)
        if circle_id is None:
            return
            
        # Get the circle to remove
        circle = self.circle_lookup.get(circle_id)
        if not circle:
            return
            
        # First, remove all connections to this circle
        connected_circles = circle["connected_to"].copy()  # Make a copy to avoid modifying while iterating
        for connected_id in connected_circles:
            connected_circle = self.circle_lookup.get(connected_id)
            if connected_circle:
                # Remove this circle from the connected circle's connections
                if circle_id in connected_circle["connected_to"]:
                    connected_circle["connected_to"].remove(circle_id)
                
                # Find and remove the connection line
                key1 = f"{circle_id}_{connected_id}"
                key2 = f"{connected_id}_{circle_id}"
                
                # Remove the connection from either direction
                connection = self.connections.get(key1)
                if connection:
                    self.canvas.delete(connection["line_id"])
                    del self.connections[key1]
                else:
                    connection = self.connections.get(key2)
                    if connection:
                        self.canvas.delete(connection["line_id"])
                        del self.connections[key2]
        
        # Remove the circle's visual representation
        self.canvas.delete(circle["canvas_id"])
        
        # Remove the circle from data structures
        self.circles = [c for c in self.circles if c["id"] != circle_id]
        del self.circle_lookup[circle_id]
        
        # Check if this was the last circle and reset if so
        if not self.circles:
            # Switch back to create mode if this was the last circle
            self._set_application_mode(ApplicationMode.CREATE)
            # Clear canvas to fully reset the scenario
            self.canvas.delete("all")
            self.drawn_items.clear()
            self.connections.clear()
            self.last_circle_id = None
            self.next_id = 1
            return
        
        # Update debug info if enabled
        if self.debug_enabled:
            self._show_debug_info()

def main():
    """Application entry point."""
    root = tk.Tk()
    app = CanvasApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()