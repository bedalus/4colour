"""
Interaction Handler for the 4colour project.

This module handles user interactions and event bindings.
"""

from color_utils import get_color_from_priority
from app_enums import ApplicationMode  # Import from app_enums instead

class InteractionHandler:
    """Handles user interactions and mode switching."""
    
    def __init__(self, app):
        """Initialize with a reference to the main application.
        
        Args:
            app: The main CanvasApplication instance
        """
        self.app = app
        
    def set_application_mode(self, new_mode):
        """Set the application mode and handle all related state transitions.
        
        Args:
            new_mode: The ApplicationMode to switch to
        """
        # Validate the mode transition
        if new_mode == self.app._mode:
            return
            
        # Don't allow transition to ADJUST mode from SELECTION mode
        if self.app._mode == ApplicationMode.SELECTION and new_mode == ApplicationMode.ADJUST:  # Fixed: Using imported ApplicationMode
            return
        
        # First clean up the current mode
        if self.app._mode == ApplicationMode.SELECTION:  # Fixed: Using imported ApplicationMode
            # Clear selections
            for indicator_id in self.app.selection_indicators.values():
                self.app.canvas.delete(indicator_id)
            self.app.selection_indicators = {}
            self.app.selected_circles = []
            if self.app.hint_text_id:
                self.app.canvas.delete(self.app.hint_text_id)
                self.app.hint_text_id = None
                
        elif self.app._mode == ApplicationMode.ADJUST:  # Fixed: Using imported ApplicationMode
            # Hide midpoint handles when exiting ADJUST mode
            self.app.connection_manager.hide_midpoint_handles()
            
            # Clear angle visualizations when exiting ADJUST mode
            self.app.ui_manager.clear_angle_visualizations()
            
            # Clear adjust mode state
            if self.app.edit_hint_text_id:
                self.app.canvas.delete(self.app.edit_hint_text_id)
                self.app.edit_hint_text_id = None
            # Reset canvas background color when exiting ADJUST mode
            self.app.canvas.config(bg="white")

        # Unbind events for the current mode
        self.unbind_mode_events(self.app._mode)

        # Set the new mode
        self.app._mode = new_mode
        
        # Update the button text based on current mode
        if self.app.mode_button:
            if self.app._mode == ApplicationMode.ADJUST:  # Fixed: Using imported ApplicationMode
                self.app.mode_button.config(text="Engage create mode")
            else:
                self.app.mode_button.config(text="Engage adjust mode")
        
        # Bind events for the new mode
        self.bind_mode_events(new_mode)
        
        # Setup additional mode-specific UI elements
        if new_mode == ApplicationMode.ADJUST:  # Fixed: Using imported ApplicationMode
            self.app.ui_manager.show_edit_hint_text()
            # Set canvas background to pale pink in ADJUST mode
            self.app.canvas.config(bg="#FFEEEE")  # Pale pink
            # Show midpoint handles in ADJUST mode
            self.app.connection_manager.show_midpoint_handles()
    
    def bind_mode_events(self, mode):
        """Bind the appropriate events for the given mode.
        
        Args:
            mode: The ApplicationMode to bind events for
        """
        if mode == ApplicationMode.CREATE:
            self.bind_create_mode_events()
        elif mode == ApplicationMode.SELECTION:
            self.bind_selection_mode_events()
        elif mode == ApplicationMode.ADJUST:
            self.bind_adjust_mode_events()

    def unbind_mode_events(self, mode):
        """Unbind the events for the given mode.
        
        Args:
            mode: The ApplicationMode to unbind events for
        """
        if mode == ApplicationMode.CREATE:
            self.unbind_create_mode_events()
        elif mode == ApplicationMode.SELECTION:
            self.unbind_selection_mode_events()
        elif mode == ApplicationMode.ADJUST:
            self.unbind_adjust_mode_events()

    def bind_create_mode_events(self):
        """Bind events for create mode."""
        if not self.app._bound_events[ApplicationMode.CREATE]:
            self.app.canvas.bind("<Button-1>", self.app._draw_on_click)
            self.app._bound_events[ApplicationMode.CREATE] = True

    def unbind_create_mode_events(self):
        """Unbind events for create mode."""
        if self.app._bound_events[ApplicationMode.CREATE]:
            self.app.canvas.unbind("<Button-1>")
            self.app._bound_events[ApplicationMode.CREATE] = False

    def bind_selection_mode_events(self):
        """Bind events for selection mode."""
        if not self.app._bound_events[ApplicationMode.SELECTION]:
            self.app.canvas.bind("<Button-1>", self.app._draw_on_click)  # Uses same draw function but in selection mode
            self.app.root.bind("<y>", self.app._confirm_selection)
            self.app._bound_events[ApplicationMode.SELECTION] = True

    def unbind_selection_mode_events(self):
        """Unbind events for selection mode."""
        if self.app._bound_events[ApplicationMode.SELECTION]:
            self.app.canvas.unbind("<Button-1>")
            self.app.root.unbind("<y>")
            self.app._bound_events[ApplicationMode.SELECTION] = False

    def bind_adjust_mode_events(self):
        """Bind events for adjust mode."""
        if not self.app._bound_events[ApplicationMode.ADJUST]:
            # Use our unified event handlers instead of separate ones
            self.app.canvas.bind("<Button-1>", self.app._drag_start)
            self.app.canvas.bind("<B1-Motion>", self.app._drag_motion)
            self.app.canvas.bind("<ButtonRelease-1>", self.app._drag_end)
            self.app.canvas.bind("<Button-3>", self.app._remove_circle)
            self.app._bound_events[ApplicationMode.ADJUST] = True

    def unbind_adjust_mode_events(self):
        """Unbind events for adjust mode."""
        if self.app._bound_events[ApplicationMode.ADJUST]:
            self.app.canvas.unbind("<Button-1>")
            self.app.canvas.unbind("<B1-Motion>")
            self.app.canvas.unbind("<ButtonRelease-1>")
            self.app.canvas.unbind("<Button-3>")
            self.app._bound_events[ApplicationMode.ADJUST] = False
    
    def toggle_mode(self):
        """Toggle between create and adjust modes."""
        # Simply toggle between create and adjust modes
        if self.app._mode == ApplicationMode.ADJUST:
            self.set_application_mode(ApplicationMode.CREATE)
        elif self.app._mode == ApplicationMode.CREATE:
            # Only enter adjust mode from create mode, not selection mode
            self.set_application_mode(ApplicationMode.ADJUST)
        # Selection mode can't transition to adjust mode - do nothing

    def draw_on_click(self, event):
        """Draw a circle at the clicked position or select an existing circle.
        
        Args:
            event: Mouse click event containing x and y coordinates
        """
        x, y = event.x, event.y
        
        # Selection mode: try to select an existing circle
        if self.app.in_selection_mode:
            circle_id = self.app.get_circle_at_coords(x, y)
            if circle_id is not None:
                self.toggle_circle_selection(circle_id)
            return
            
        # Normal mode: draw a new circle
        # Use the deterministic color assignment
        color_priority = self.app._assign_color_based_on_connections()  # Only get priority
        color_name = get_color_from_priority(color_priority)  # Get color name for drawing
        
        # Create the circle on canvas
        circle_id = self.app.canvas.create_oval(
            x - self.app.circle_radius,
            y - self.app.circle_radius,
            x + self.app.circle_radius,
            y + self.app.circle_radius,
            fill=color_name,  # Use derived color name
            outline="black",
            tags="circle"  # Add tag for circle
        )
        
        # Store circle data - now also with ordered_connections list and enclosed status
        circle_data = {
            "id": self.app.next_id,
            "canvas_id": circle_id,
            "x": x,
            "y": y,
            "color_priority": color_priority,
            "connected_to": [],
            "ordered_connections": [],  # New field for storing connections in clockwise order
            "enclosed": False  # New field for Phase 14: Track outer border
        }
        
        # Add circle to the list and lookup dictionary
        self.app.circles.append(circle_data)
        self.app.circle_lookup[self.app.next_id] = circle_data
        
        # Special case: If this is the first circle, just add it
        if self.app.last_circle_id is None:
            self.app.last_circle_id = self.app.next_id
            self.app.next_id += 1
            self.app.drawn_items.append((x, y))
            
            # Update debug display if enabled
            if self.app.debug_enabled:
                self.app.ui_manager.show_debug_info()
            return
            
        # For subsequent circles:
        self.app.newly_placed_circle_id = self.app.next_id  # Store the new circle's ID
        self.app.next_id += 1
        self.app.drawn_items.append((x, y))
        
        # Enter selection mode
        self.app.in_selection_mode = True
        self.app.ui_manager.show_hint_text()
        
        # Update debug display if enabled
        if self.app.debug_enabled:
            self.app.ui_manager.show_debug_info()

    def toggle_circle_selection(self, circle_id):
        """Toggle selection status of a circle.
        
        Args:
            circle_id: ID of the circle to toggle selection
        """
        if circle_id == self.app.newly_placed_circle_id:
            # Can't select the newly placed circle
            return
            
        circle = self.app.circle_lookup.get(circle_id)
        if not circle:
            return
            
        # Check if circle is already selected
        if circle_id in self.app.selected_circles:
            # Deselect: remove from list and delete the indicator
            self.app.selected_circles.remove(circle_id)
            if circle_id in self.app.selection_indicators:
                self.app.canvas.delete(self.app.selection_indicators[circle_id])
                del self.app.selection_indicators[circle_id]
        else:
            # Select: add to list and draw indicator
            self.app.selected_circles.append(circle_id)
            # Draw a small line below the circle as selection indicator
            indicator_id = self.app.canvas.create_line(
                circle["x"] - self.app.circle_radius,
                circle["y"] + self.app.circle_radius + 2,
                circle["x"] + self.app.circle_radius,
                circle["y"] + self.app.circle_radius + 2,
                width=2,
                fill="black"
            )
            self.app.selection_indicators[circle_id] = indicator_id

    def confirm_selection(self, event):
        """Handle y key press to confirm circle selections.
        
        Args:
            event: Key press event
        """
        if not self.app.in_selection_mode:
            return
            
        # Connect the newly placed circle to all selected circles
        for circle_id in self.app.selected_circles:
            self.app.connection_manager.add_connection(self.app.newly_placed_circle_id, circle_id)
        
        # After all connections are made, check for color conflicts and resolve them once
        if self.app.newly_placed_circle_id and self.app.selected_circles:
            # Check and resolve color conflicts for the newly placed circle
            priority = self.app.color_manager.check_and_resolve_color_conflicts(self.app.newly_placed_circle_id)
            
        # Exit selection mode
        self.app.in_selection_mode = False
        self.app.last_circle_id = self.app.newly_placed_circle_id
        self.app.newly_placed_circle_id = None
        
        # Clear selections
        self.app.selected_circles = []
        
        # Clear selection indicators
        for indicator_id in self.app.selection_indicators.values():
            self.app.canvas.delete(indicator_id)
        self.app.selection_indicators = {}
        
        # Clear hint text
        if self.app.hint_text_id:
            self.app.canvas.delete(self.app.hint_text_id)
            self.app.hint_text_id = None
            
        # Update debug info if enabled
        if self.app.debug_enabled:
            self.app.ui_manager.show_debug_info()

    def reset_drag_state(self):
        """Reset the drag state to its default values."""
        self.app.drag_state = {
            "active": False,
            "type": None,
            "id": None,
            "start_x": 0,
            "start_y": 0,
            "last_x": 0,
            "last_y": 0
        }
    
    def drag_start(self, event):
        """Start dragging an object (circle or midpoint).
        
        Args:
            event: Mouse press event containing x and y coordinates
        """
        if not self.app.in_edit_mode:
            return
        
        # Reset any existing drag state first
        self.reset_drag_state()
        
        # Save the starting coordinates
        self.app.drag_state["start_x"] = event.x
        self.app.drag_state["last_x"] = event.x
        self.app.drag_state["start_y"] = event.y
        self.app.drag_state["last_y"] = event.y
            
        # Check if we're clicking on a midpoint handle first
        clicked_item = self.app.canvas.find_closest(event.x, event.y)
        if clicked_item:
            tags = self.app.canvas.gettags(clicked_item[0])
            if "midpoint_handle" in tags:
                # Find which connection this midpoint belongs to
                for tag in tags:
                    if "_" in tag and tag in self.app.midpoint_handles:
                        self.app.drag_state["active"] = True
                        self.app.drag_state["type"] = "midpoint"
                        self.app.drag_state["id"] = tag
                        return
        
        # If not a midpoint, check if it's a circle
        circle_id = self.app.get_circle_at_coords(event.x, event.y)
        if circle_id is not None:
            self.app.drag_state["active"] = True
            self.app.drag_state["type"] = "circle"
            self.app.drag_state["id"] = circle_id
    
    def drag_motion(self, event):
        """Handle any object's dragging motion.
        
        Args:
            event: Mouse motion event
        """
        if not self.app.in_edit_mode or not self.app.drag_state["active"]:
            return
            
        # Get current mouse position
        x, y = event.x, event.y
        
        # Calculate the delta from the last position
        delta_x = x - self.app.drag_state["last_x"]
        delta_y = y - self.app.drag_state["last_y"]
        
        # Update last position
        self.app.drag_state["last_x"] = x
        self.app.drag_state["last_y"] = y
        
        # Handle object-specific drag logic
        if self.app.drag_state["type"] == "circle":
            # Pass the circle_id from drag state as first parameter
            circle_id = self.app.drag_state["id"]
            self.drag_circle_motion(circle_id, delta_x, delta_y)
        elif self.app.drag_state["type"] == "midpoint":
            self.drag_midpoint_motion(x, y)
            
        # Update debug info if enabled
        if self.app.debug_enabled:
            self.app.ui_manager.show_debug_info()
        
        # Stop event propagation
        return "break"
    
    def drag_end(self, event):
        """End dragging any object.
        
        Args:
            event: Mouse release event
        """
        if not self.app.in_edit_mode or not self.app.drag_state["active"]:
            return
        
        # Clear any angle visualization lines when dragging ends
        self.app.ui_manager.clear_angle_visualizations()
        
        # Update ordered connections based on what was dragged
        if self.app.drag_state["type"] == "circle":
            # Get the dragged circle's ID
            circle_id = self.app.drag_state["id"]
            circle = self.app.circle_lookup.get(circle_id)
            
            if circle:
                # Update the dragged circle's ordered connections
                self.app.connection_manager.update_ordered_connections(circle_id)
                
                # Update ordered connections for all connected circles
                for connected_id in circle["connected_to"]:
                    self.app.connection_manager.update_ordered_connections(connected_id)
        
        elif self.app.drag_state["type"] == "midpoint":
            # Extract the connection key and update both connected circles
            connection_key = self.app.drag_state["id"]
            
            # Extract circle IDs from the connection key (format: "smaller_id_larger_id")
            try:
                parts = connection_key.split("_")
                if len(parts) == 2:
                    from_id = int(parts[0])
                    to_id = int(parts[1])
                    
                    # Update ordered connections for both circles
                    self.app.connection_manager.update_ordered_connections(from_id)
                    self.app.connection_manager.update_ordered_connections(to_id)
            except (ValueError, AttributeError):
                pass  # Skip if connection key cannot be parsed
        
        # Reset the drag state
        self.reset_drag_state()
    
    def drag_circle_motion(self, circle_id, dx, dy):
        """Handle circle dragging motion.
        
        Args:
            circle_id: ID of the circle being dragged
            dx: Change in X position
            dy: Change in Y position
        """
        circle = self.app.circle_lookup.get(circle_id)
        if not circle:
            return
        
        # Update circle position on canvas
        self.app.canvas.move(circle["canvas_id"], dx, dy)
        
        # Update circle data
        circle["x"] += dx
        circle["y"] += dy
        
        # Update connecting lines in real-time
        self.app.connection_manager.update_connections(circle_id)
        
        # Update debug info if enabled
        if self.app.debug_enabled:
            self.app.ui_manager.show_debug_info()
    
    def drag_midpoint_motion(self, x, y):
        """Handle midpoint dragging motion.
        
        Args:
            x: Current X coordinate
            y: Current Y coordinate
        """
        connection_key = self.app.drag_state["id"]
        connection = self.app.connections.get(connection_key)
        if not connection:
            return
        
        # Get the circle IDs for this connection
        from_id = connection["from_circle"]
        to_id = connection["to_circle"]
        
        # Get the circles
        from_circle = self.app.circle_lookup.get(from_id)
        to_circle = self.app.circle_lookup.get(to_id)
        if not from_circle or not to_circle:
            return
        
        # Calculate the base midpoint (without any curve offset)
        base_mid_x, base_mid_y = self.app.connection_manager.calculate_midpoint(from_circle, to_circle)
        
        # Calculate the new curve offset based on the current position
        # Double the offset to make the curve follow the handle correctly
        new_curve_x = (x - base_mid_x) * 2
        new_curve_y = (y - base_mid_y) * 2
        
        # Update the connection curve with the new offset
        self.app.connection_manager.update_connection_curve(from_id, to_id, new_curve_x, new_curve_y)
        
        # Clear any existing angle visualizations
        self.app.ui_manager.clear_angle_visualizations()
        
        # Draw new angle visualizations for the current connection
        self.app.ui_manager.draw_connection_angle_visualizations(connection_key)
        
        # Stop event propagation
        return "break"
