"""
Interaction Handler for the 4colour project.

This module handles user interactions and event bindings.
"""

import tkinter as tk  # Add this import for tk.DISABLED
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
        """Set the application mode and handle all related state transitions."""
        # Validate the mode transition
        if new_mode == self.app._mode:
            print(f"DEBUG: Already in {new_mode} mode, ignoring transition")
            return
            
        # Don't allow transition to ADJUST mode from SELECTION mode
        # EXCEPTION: Allow if it's for a red node
        if self.app._mode == ApplicationMode.SELECTION and new_mode == ApplicationMode.ADJUST:
            if not self.app.color_manager.red_node_id:
                print("DEBUG: Blocking SELECTION to ADJUST transition (not for red node)")
                return
            else:
                print("DEBUG: Allowing SELECTION to ADJUST transition for red node")
        
        print(f"DEBUG: Transitioning from {self.app._mode} to {new_mode}")
        
        old_mode = self.app._mode  # Store the old mode before changing
        
        # Special handling for exiting CREATE mode
        if old_mode == ApplicationMode.CREATE:
             # Lock all non-fixed circles and connections
            for circle in self.app.circles:
                if not circle.get("fixed", False):
                    circle["locked"] = True
            for connection_key, connection in self.app.connections.items():
                 if not connection.get("fixed", False):
                    connection["locked"] = True
        
        # Common mode transition handling
        self._prepare_mode_transition(new_mode)
        
        # Update button text
        if self.app.mode_button and not hasattr(self.app, '_stored_mode_button_command'):
            if new_mode == ApplicationMode.ADJUST:
                self.app.mode_button.config(text="Engage create mode")
            else:
                self.app.mode_button.config(text="Engage adjust mode")
        
        # The unlocking of the last node is now handled in _prepare_mode_transition
    
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
            self.app.root.bind("<Escape>", self.app._cancel_selection)  # Add escape binding
            self.app._bound_events[ApplicationMode.SELECTION] = True

    def unbind_selection_mode_events(self):
        """Unbind events for selection mode."""
        if self.app._bound_events[ApplicationMode.SELECTION]:
            self.app.canvas.unbind("<Button-1>")
            self.app.root.unbind("<y>")
            self.app.root.unbind("<Escape>")  # Remove escape binding
            self.app._bound_events[ApplicationMode.SELECTION] = False

    def bind_adjust_mode_events(self):
        """Bind events for adjust mode."""
        if not self.app._bound_events[ApplicationMode.ADJUST]:
            # Use our unified event handlers instead of separate ones
            self.app.canvas.bind("<Button-1>", self.app._drag_start)
            self.app.canvas.bind("<B1-Motion>", self.app._drag_motion)
            self.app.canvas.bind("<ButtonRelease-1>", self.app._drag_end)
            self.app._bound_events[ApplicationMode.ADJUST] = True

    def unbind_adjust_mode_events(self):
        """Unbind events for adjust mode."""
        if self.app._bound_events[ApplicationMode.ADJUST]:
            self.app.canvas.unbind("<Button-1>")
            self.app.canvas.unbind("<B1-Motion>")
            self.app.canvas.unbind("<ButtonRelease-1>")
            self.app._bound_events[ApplicationMode.ADJUST] = False
    
    def toggle_mode(self):
        """Toggle between create and adjust modes."""
        if self.app._mode == ApplicationMode.ADJUST:
            self._prepare_mode_transition(ApplicationMode.CREATE)
            if self.app.mode_button:
                self.app.mode_button.config(text="Engage adjust mode")
        elif self.app._mode == ApplicationMode.CREATE:
            self._prepare_mode_transition(ApplicationMode.ADJUST)
            if self.app.mode_button:
                self.app.mode_button.config(text="Engage create mode")

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
            
        # Check for proximity restrictions - prevent placement too close to origin or fixed nodes
        if self._is_in_protected_zone(x, y):
            return
            
        # Normal mode: draw a new circle
        # Use the deterministic color assignment
        color_priority = self.app._assign_color_based_on_connections()  # Only get priority
        color_name = get_color_from_priority(color_priority)  # Get color name for drawing
        
        # Detect if the new point is too close to an existing circle
        r = self.app.circle_radius
        min_distance = float('inf')
        closest_circle = None
        for c in self.app.circles:
            dx = x - c["x"]
            dy = y - c["y"]
            dist = (dx**2 + dy**2) ** 0.5
            if dist < min_distance:
                closest_circle = c
                min_distance = dist

        if closest_circle and min_distance < 3 * r:
            dx = x - closest_circle["x"]
            dy = y - closest_circle["y"]
            dist = (dx**2 + dy**2) ** 0.5
            
            x = closest_circle["x"] + dx * 4 * r / dist
            y = closest_circle["y"] + dy * 4 * r / dist

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
            "enclosed": False,  # New field for Phase 14: Track outer border
            "locked": False # New field for Phase 16: Lock elements outside ADJUST mode
        }
        
        # Add circle to the list and lookup dictionary
        self.app.circles.append(circle_data)
        self.app.circle_lookup[self.app.next_id] = circle_data
        
        # Store this circle's ID as the one to be connected
        self.app.newly_placed_circle_id = self.app.next_id
        self.app.next_id += 1
        self.app.drawn_items.append((x, y))
        
        # Enter selection mode - this applies for all nodes now that we have fixed starting nodes
        self.app.in_selection_mode = True
        self.app.ui_manager.show_hint_text()
        
        # Update enclosure status after adding a new circle
        self.app._update_enclosure_status() # Phase 14 Trigger Point
        
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
            
        # Prevent confirming with no selections
        if not self.app.selected_circles:
            return
            
        # Connect the newly placed circle to all selected circles
        for circle_id in self.app.selected_circles:
            self.app.connection_manager.add_connection(self.app.newly_placed_circle_id, circle_id)
        
        # After all connections are made, check for color conflicts and resolve them once
        if self.app.newly_placed_circle_id and self.app.selected_circles:
            # Check and resolve color conflicts for the newly placed circle
            priority = self.app.color_manager.check_and_resolve_color_conflicts(self.app.newly_placed_circle_id)
            
            # Note: We don't need to check if priority is 4 here, as the color_manager
            # will handle showing the fix button and entering adjust mode if needed
        
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
            
        # Update enclosure status after connections are confirmed
        self.app._update_enclosure_status() # Phase 14 Trigger Point
            
        # Update debug info if enabled
        if self.app.debug_enabled:
            self.app.ui_manager.show_debug_info()

    def cancel_selection(self, event):
        """Handle escape key press to cancel circle placement.
        
        Args:
            event: Key press event
        """
        if not self.app.in_selection_mode:
            return

        if self.app.newly_placed_circle_id:
            # Use the circle manager's remove method since it handles all cleanup
            # Pass bypass_lock=True to ensure the circle can be removed even if locked
            self.app.circle_manager.remove_circle_by_id(self.app.newly_placed_circle_id, bypass_lock=True)
            
            # Reset selection state
            self.app.newly_placed_circle_id = None
            self._clear_selection_state()
            
            # Exit selection mode
            self.app.in_selection_mode = False

    def reset_drag_state(self):
        """Reset the drag state to its default values."""
        self.app.drag_state = {
            "active": False,
            "type": None,
            "id": None,
            "start_x": 0,
            "start_y": 0,
            "last_x": 0,
            "last_y": 0,
            "curve_x": 0,  # Added for midpoint dragging
            "curve_y": 0   # Added for midpoint dragging
        }
    
    def drag_start(self, event):
        """Start dragging an object (circle or midpoint).

        Args:
            event: Mouse press event containing x and y coordinates
        """
        # Remove highlight as soon as a drag starts
        if self.app.highlighted_circle_id:
            self.app.canvas.delete(self.app.highlighted_circle_id)
            self.app.highlighted_circle_id = None

        if not self.app.in_edit_mode:
            return

        # Reset any existing drag state first
        self.reset_drag_state()

        # Save the starting coordinates
        self.app.drag_state["start_x"] = event.x
        self.app.drag_state["last_x"] = event.x
        self.app.drag_state["start_y"] = event.y
        self.app.drag_state["last_y"] = event.y

        # Track circles to display in debug info
        debug_circle_ids = []

        # Check if we're clicking on a midpoint handle first
        clicked_item = self.app.canvas.find_closest(event.x, event.y)
        if clicked_item:
            tags = self.app.canvas.gettags(clicked_item[0])
            if "midpoint_handle" in tags:
                for tag in tags:
                    if "_" in tag and tag in self.app.midpoint_handles:
                        connection_key = tag
                        connection = self.app.connections.get(connection_key)
                        
                        # Extract circle IDs from connection key for debug display
                        try:
                            parts = connection_key.split("_")
                            if len(parts) == 2:
                                circle1_id = int(parts[0])
                                circle2_id = int(parts[1])
                                debug_circle_ids = [circle1_id, circle2_id]
                                
                                # FIX: Allow dragging midpoint handles connected to the last circle,
                                # regardless of lock status
                                if (self.app.last_circle_id == circle1_id or 
                                    self.app.last_circle_id == circle2_id):
                                    self.app.drag_state["active"] = True
                                    self.app.drag_state["type"] = "midpoint"
                                    self.app.drag_state["id"] = tag
                                    
                                    # Update debug display
                                    self._update_debug_for_circles(*debug_circle_ids)
                                    return
                        except (ValueError, AttributeError):
                            pass
                            
                        # For non-last circle connections, check lock status
                        if connection and (connection.get("fixed", False) or connection.get("locked", False)):
                            # FIX: Update debug display even if locked
                            self._update_debug_for_circles(*debug_circle_ids)
                            return # Stop if locked

                        self.app.drag_state["active"] = True
                        self.app.drag_state["type"] = "midpoint"
                        self.app.drag_state["id"] = tag
                        
                        # Update debug display
                        self._update_debug_for_circles(*debug_circle_ids)
                        return

        # Check circles second
        circle_id = self.app.get_circle_at_coords(event.x, event.y)
        if circle_id is not None:
            debug_circle_ids = [circle_id]
            circle = self.app.circle_lookup.get(circle_id)
            
            # Check fixed and locked status from the circle data
            # FIX: Update debug display even if locked
            self._update_debug_for_circles(*debug_circle_ids)
                
            if circle and (circle.get("fixed", False) or circle.get("locked", False)):
                return  # Stop if locked

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
        x, y = event.x, event.y  # Fixed: Properly get both coordinates
        # Update last position
        # Calculate the delta from the last position
        delta_x = x - self.app.drag_state["last_x"]
        delta_y = y - self.app.drag_state["last_y"]
        
        # Handle object-specific drag logic
        if self.app.drag_state["type"] == "circle":
            # Pass the circle_id from drag state as first parameter
            self.drag_circle_motion(self.app.drag_state["id"], delta_x, delta_y)
        elif self.app.drag_state["type"] == "midpoint":
            self.drag_midpoint_motion(x, y)
        
        # Update last position
        self.app.drag_state["last_x"] = x
        self.app.drag_state["last_y"] = y
        
        # Stop event propagation
        return "break"
    
    def drag_end(self, event):
        """End dragging any object.
        
        Args:
            event: Mouse release event
        """
        if not self.app.in_edit_mode or not self.app.drag_state["active"]:
            return

        # --- ENFORCE MINIMUM DISTANCE CONSTRAINT ON MIDPOINT HANDLE RELEASE ---
        if self.app.drag_state["type"] == "midpoint":
            connection_key = self.app.drag_state["id"]
            connection = self.app.connections.get(connection_key)
            if connection:
                from_circle = self.app.circle_lookup.get(connection["from_circle"])
                to_circle = self.app.circle_lookup.get(connection["to_circle"])
                if from_circle and to_circle:
                    base_mid_x, base_mid_y = self.app.connection_manager.calculate_midpoint(from_circle, to_circle)
                    new_curve_x = self.app.drag_state.get("curve_x", 0)
                    new_curve_y = self.app.drag_state.get("curve_y", 0)
                    min_dist = 20
                    def dist_sq(x1, y1, x2, y2):
                        # FIX: Corrected distance calculation (was y2-y2)
                        return (x1 - x2) ** 2 + (y1 - y2) ** 2 
                    new_mid_x = base_mid_x + new_curve_x / 2
                    new_mid_y = base_mid_y + new_curve_y / 2
                    from_dist_sq = dist_sq(new_mid_x, new_mid_y, from_circle["x"], from_circle["y"])
                    to_dist_sq = dist_sq(new_mid_x, new_mid_y, to_circle["x"], to_circle["y"])
                    min_dist_sq = min_dist ** 2
                    if from_dist_sq < min_dist_sq or to_dist_sq < min_dist_sq:
                        # If too close, reset drag state curve values before applying them later
                        self.app.drag_state["curve_x"] = self.app.drag_state.get("orig_curve_x", 0)
                        self.app.drag_state["curve_y"] = self.app.drag_state.get("orig_curve_y", 0)

        # Show or clear warning hint for angle constraint after midpoint handle is released
        if self.app.drag_state["type"] == "midpoint":
            connection_key = self.app.drag_state["id"]
            connection = self.app.connections.get(connection_key)
            if connection:
                # Apply the final curve offset before evaluating the constraint
                connection["curve_X"] = self.app.drag_state.get("curve_x", connection.get("curve_X", 0))
                connection["curve_Y"] = self.app.drag_state.get("curve_y", connection.get("curve_Y", 0))
                from_id = connection["from_circle"]
                to_id = connection["to_circle"]
                angle_violation = (
                    self.app.connection_manager.is_entry_angle_too_close(from_id, to_id, min_angle=2) or
                    self.app.connection_manager.is_entry_angle_too_close(to_id, from_id, min_angle=2)
                )
                if angle_violation:
                    self.app.ui_manager.show_edit_hint_text(
                        "Warning: Connection angle too close to another. Adjust the midpoint until the warning clears."
                    )
                else:
                    self.app.ui_manager.show_edit_hint_text()
        
        # Clear any angle visualization lines when dragging ends
        self.app.ui_manager.clear_angle_visualizations()
        
        # Flag to check if ordered connections were updated
        ordered_connections_updated = False
        
        # Track which circle IDs to display in debug
        debug_circle_ids = []
        
        # Update ordered connections based on what was dragged
        if self.app.drag_state["type"] == "circle":
            # Get the dragged circle's ID
            circle_id = self.app.drag_state["id"]
            circle = self.app.circle_lookup.get(circle_id)
            if circle:
                debug_circle_ids.append(circle_id)  # Changed from single ID to list
                # First update all connections for the circle visually
                self.app.connection_manager.update_connections(circle_id)
                
                # Then update the ordered connections
                self.app.connection_manager.update_ordered_connections(circle_id)
                ordered_connections_updated = True
                
                # Update ordered connections for all connected circles
                for connected_id in circle["connected_to"]:
                    self.app.connection_manager.update_ordered_connections(connected_id)
        
        elif self.app.drag_state["type"] == "midpoint":
            # Extract the connection key and update both connected circles
            connection_key = self.app.drag_state["id"]
            
            # For midpoint drag, show both connected circles
            try:
                parts = connection_key.split("_")
                if len(parts) == 2:
                    from_id = int(parts[0])
                    to_id = int(parts[1])
                    debug_circle_ids.extend([from_id, to_id])  # Add both circles
            except (ValueError, AttributeError):
                pass
            
            # Now apply the curve update that was calculated during drag_motion
            if "curve_x" in self.app.drag_state and "curve_y" in self.app.drag_state:
                connection = self.app.connections.get(connection_key)
                if connection:
                    from_id = connection["from_circle"]
                    to_id = connection["to_circle"]
                    
                    # Update the connection with the stored curve offsets
                    self.app.connection_manager.update_connection_curve(
                        from_id, 
                        to_id, 
                        self.app.drag_state["curve_x"], 
                        self.app.drag_state["curve_y"]
                    )
            
            # Extract circle IDs from the connection key (format: "smaller_id_larger_id")
            try:
                parts = connection_key.split("_")
                if len(parts) == 2:
                    from_id = int(parts[0])
                    to_id = int(parts[1])
                    
                    # Update ordered connections for both circles
                    self.app.connection_manager.update_ordered_connections(from_id)
                    self.app.connection_manager.update_ordered_connections(to_id)
                    ordered_connections_updated = True
            except (ValueError, AttributeError):
                pass  # Skip if connection key cannot be parsed
        
        # Check final angles and set line color
        if self.app.drag_state["type"] == "midpoint":
            connection_key = self.app.drag_state["id"]
            connection = self.app.connections.get(connection_key)
            if connection:
                from_id = connection["from_circle"]
                to_id = connection["to_circle"]
                angle_violation = (
                    self.app.connection_manager.is_entry_angle_too_close(from_id, to_id, min_angle=2) or
                    self.app.connection_manager.is_entry_angle_too_close(to_id, from_id, min_angle=2)
                )
                self.app.canvas.itemconfig(connection["line_id"], 
                    fill="red" if angle_violation else "black")

        # Reset the drag state BEFORE updating enclosure status
        self.reset_drag_state()
        
        # Update enclosure status AFTER drag ends and ordered connections are updated
        if ordered_connections_updated:
             self.app._update_enclosure_status() # Phase 14 Trigger Point
             # The extreme node/midpoint indicators will be updated as part of _update_enclosure_status
             
        # Set the active circles for debug display before updating
        self._update_debug_for_circles(*debug_circle_ids)
        
        # Ensure final state reflects constraints after drag ends
        self._check_violations_and_update_button() # Add final check here

    def _update_connection_visuals(self, connection_key):
        """Updates the visual representation of a single connection."""
        connection = self.app.connections.get(connection_key)
        if not connection:
            return

        from_id = connection["from_circle"]
        to_id = connection["to_circle"]

        # 1. Check for angle violations
        angle_violation = (
            self.app.connection_manager.is_entry_angle_too_close(from_id, to_id, min_angle=2) or
            self.app.connection_manager.is_entry_angle_too_close(to_id, from_id, min_angle=2)
        )
        line_color = "red" if angle_violation else "black"

        # 2. Recalculate curve points
        points = self.app.connection_manager.calculate_curve_points(from_id, to_id)
        
        if points:
            # 3. Delete the old line canvas item
            # Restoring delete/create method
            self.app.canvas.delete(connection["line_id"])
            
            # 4. Create a new line canvas item with updated points and color
            new_line_id = self.app.canvas.create_line(
                points,
                width=1,
                smooth=True,
                tags="line",
                fill=line_color # Apply color immediately
            )
            
            # 5. Update the connection data with the new canvas ID
            connection["line_id"] = new_line_id
            
            # 6. Ensure the new line is drawn below circles
            self.app.canvas.lower(new_line_id)
        else:
            pass

        # 7. Update midpoint handle position if it exists
        if connection_key in self.app.midpoint_handles:
            handle_x, handle_y = self.app.connection_manager.calculate_midpoint_handle_position(
                from_id, to_id
            )
            handle_id = self.app.midpoint_handles[connection_key]
            self.app.canvas.coords(
                handle_id,
                handle_x - self.app.midpoint_radius,
                handle_y - self.app.midpoint_radius,
                handle_x + self.app.midpoint_radius,
                handle_y + self.app.midpoint_radius
            )

    def _check_violations_and_update_button(self):
        """Checks all connections for angle violations and updates the mode button state."""
        if self.app.mode_button:
            has_violations = self.app.connection_manager.has_angle_violations()
            self.app.mode_button.config(state='disabled' if has_violations else 'normal')
    
    def drag_circle_motion(self, circle_id, dx, dy):
        """Handle circle dragging motion."""
        circle = self.app.circle_lookup.get(circle_id)
        if not circle:
            return
        
        # Calculate the new position
        new_x = circle["x"] + dx
        new_y = circle["y"] + dy
        
        # Prevent dragging into the protected zone
        if self._is_in_protected_zone(new_x, new_y):
            return
        
        # Update circle position data and visually move it
        self.app.canvas.move(circle["canvas_id"], dx, dy)
        circle["x"] = new_x
        circle["y"] = new_y

        # Update visuals for all connected lines
        connections_to_update = list(circle.get("connected_to", [])) # Create a copy for safe iteration if needed
        
        for connected_id in connections_to_update:
            connection_key = self.app.connection_manager.get_connection_key(circle_id, connected_id)
            
            # Check if the connection actually exists in the main dictionary
            if connection_key not in self.app.connections:
                continue # Skip to the next connected_id

            # If the key exists, proceed with the update
            self._update_connection_visuals(connection_key) 

        # Update the button state based on overall violations
        self._check_violations_and_update_button() 

    def drag_midpoint_motion(self, x, y):
        """Handle midpoint dragging motion, enforcing minimum distance and angle constraints."""
        connection_key = self.app.drag_state["id"]
        connection = self.app.connections.get(connection_key)
        if not connection:
            return
        
        # Prevent dragging into the protected zone
        if self._is_in_protected_zone(x, y):
            return

        # Calculate new curve offset
        from_circle = self.app.circle_lookup.get(connection["from_circle"])
        to_circle = self.app.circle_lookup.get(connection["to_circle"])
        if not from_circle or not to_circle:
            return

        base_mid_x, base_mid_y = self.app.connection_manager.calculate_midpoint(from_circle, to_circle)
        new_curve_x = (x - base_mid_x) * 2
        new_curve_y = (y - base_mid_y) * 2

        # Enforce minimum distance constraint
        min_dist = 20
        def dist_sq(x1, y1, x2, y2):
            return (x1 - x2) ** 2 + (y1 - y2) ** 2
        new_mid_x = base_mid_x + new_curve_x / 2
        new_mid_y = base_mid_y + new_curve_y / 2
        from_dist_sq = dist_sq(new_mid_x, new_mid_y, from_circle["x"], from_circle["y"])
        # FIX: Add the missing y-coordinate for the to_circle
        to_dist_sq = dist_sq(new_mid_x, new_mid_y, to_circle["x"], to_circle["y"]) 
        min_dist_sq = min_dist ** 2
        if from_dist_sq < min_dist_sq or to_dist_sq < min_dist_sq:
            return # Don't update if too close

        # Store curve offset in drag state and temporarily in connection for visual update
        self.app.drag_state["curve_x"] = new_curve_x
        self.app.drag_state["curve_y"] = new_curve_y
        connection["curve_X"] = new_curve_x # Temporary update for calculate_curve_points
        connection["curve_Y"] = new_curve_y

        # Update the visuals for this specific connection
        self._update_connection_visuals(connection_key) # Call helper

        # Update the button state based on overall violations
        self._check_violations_and_update_button() # Call helper

        # Move the handle itself (visual only, position derived from x, y)
        handle_id = self.app.midpoint_handles.get(connection_key)
        if handle_id:
            self.app.canvas.coords(
                handle_id,
                x - self.app.midpoint_radius, y - self.app.midpoint_radius,
                x + self.app.midpoint_radius, y + self.app.midpoint_radius
            )

        # Clear previous visualization lines before drawing new ones (specific to midpoint drag)
        self.app.ui_manager.clear_angle_visualizations()
        self.app.ui_manager.draw_connection_angle_visualizations(connection_key)
        
        # Revert temporary curve update in connection dict after visuals are done for this frame
        # The actual update happens in drag_end
        connection["curve_X"] = self.app.drag_state.get("orig_curve_x", connection.get("curve_X", 0)) # Revert using original or default
        connection["curve_Y"] = self.app.drag_state.get("orig_curve_y", connection.get("curve_Y", 0))

    def switch_to_red_fix_mode(self, circle_id):
        """Switch to ADJUST mode specifically for fixing red nodes.
        
        Args:
            circle_id: ID of the red node that needs fixing
        """
        # Handle mode transition with specialized flag
        is_transition = self._prepare_mode_transition(ApplicationMode.ADJUST, for_red_node=True)
        
        # Additional setup for red node fix mode
        if is_transition and self.app.mode_button:
            # Update button text
            self.app.mode_button.config(text="Fix Red")
            
            # Store the original mode button's command
            original_command = self.app.mode_button['command']
            self.app._stored_mode_button_command = original_command
            self.app.mode_button.config(
                command=lambda: self.app._focus_after(
                    self.app.color_manager.handle_fix_red_node_button
                )
            )
            print("DEBUG: Changed mode button to 'Fix Red'")
    
    def _clear_selection_state(self):
        """Clear all selection-related state and UI elements."""
        # Remove selection indicators
        for indicator_id in self.app.selection_indicators.values():
            self.app.canvas.delete(indicator_id)
        self.app.selection_indicators = {}
        self.app.selected_circles = []
        
        # Clear hint text
        if self.app.hint_text_id:
            self.app.canvas.delete(self.app.hint_text_id)
            self.app.hint_text_id = None
    
    def _update_debug_for_circles(self, *circle_ids):
        """Update debug display for specified circles if debug is enabled.
        
        Args:
            *circle_ids: Variable number of circle IDs to show in debug
        """
        if self.app.debug_enabled and circle_ids:
            self.app.ui_manager.set_active_circles(*circle_ids)
            self.app.ui_manager.show_debug_info()
    
    def _is_in_protected_zone(self, x, y):
        """Check if coordinates are in the protected zone.
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            
        Returns:
            bool: True if coordinates are in protected zone
        """
        return x < self.app.PROXIMITY_LIMIT and y < self.app.PROXIMITY_LIMIT
    
    def _prepare_mode_transition(self, new_mode, for_red_node=False):
        """Handle common mode transition tasks."""
        # Check for angle violations when leaving adjust mode
        if self.app._mode == ApplicationMode.ADJUST and new_mode != ApplicationMode.ADJUST:
            if self.app.connection_manager.has_angle_violations():
                print("DEBUG: Cannot leave adjust mode while connections have angle violations")
                return False
                
        old_mode = self.app._mode
        
        # Skip if already in the target mode
        if old_mode == new_mode:
            return
            
        # Clean up previous mode
        if old_mode == ApplicationMode.SELECTION:
            self._clear_selection_state()
        elif old_mode == ApplicationMode.ADJUST:
            # Hide midpoint handles
            self.app.connection_manager.hide_midpoint_handles()
            
            # Clear angle visualizations
            self.app.ui_manager.clear_angle_visualizations()
            
            # Clear adjust mode state
            if self.app.edit_hint_text_id:
                self.app.canvas.delete(self.app.edit_hint_text_id)
                self.app.edit_hint_text_id = None
                
            # Reset canvas background
            self.app.canvas.config(bg="white")
            
            # Clear highlight
            if self.app.highlighted_circle_id:
                self.app.canvas.delete(self.app.highlighted_circle_id)
                self.app.highlighted_circle_id = None
        
        # Unbind events for previous mode
        self.unbind_mode_events(old_mode)
        
        # Set new mode
        self.app._mode = new_mode
        
        # Bind events for new mode
        self.bind_mode_events(new_mode)
        
        # Setup for new mode
        if new_mode == ApplicationMode.ADJUST:
            # Set up ADJUST mode UI
            self.app.ui_manager.show_edit_hint_text()
            self.app.canvas.config(bg="#FFDDDD" if for_red_node else "#FFEEEE")
            self.app.connection_manager.show_midpoint_handles()
            self.app._update_enclosure_status()
            
            # Always unlock the last placed circle and its connections
            if self.app.last_circle_id is not None and self.app.last_circle_id > 0:  # Ensure it's not a fixed node
                last_circle_data = self.app.circle_lookup.get(self.app.last_circle_id)
                if last_circle_data and not last_circle_data.get("fixed", False):
                    # Unlock the circle
                    last_circle_data["locked"] = False
                    print(f"DEBUG: Unlocked last node {self.app.last_circle_id} for ADJUST mode")

                    # Draw highlight
                    radius = self.app.circle_radius
                    x, y = last_circle_data["x"], last_circle_data["y"]
                    # Delete previous highlight if it exists
                    if self.app.highlighted_circle_id:
                        self.app.canvas.delete(self.app.highlighted_circle_id)
                    self.app.highlighted_circle_id = self.app.canvas.create_oval(
                        x - radius - 3, y - radius - 3,
                        x + radius + 3, y + radius + 3,
                        outline='purple', width=3, tags="temp_highlight"
                    )

                    # Unlock its connections
                    for connected_id in last_circle_data.get("connected_to", []):
                        connection_key = self.app.connection_manager.get_connection_key(self.app.last_circle_id, connected_id)
                        connection = self.app.connections.get(connection_key)
                        if connection and not connection.get("fixed", False):
                            connection["locked"] = False  # Unlock connections
            
            if for_red_node:
                # Special handling for red node fix
                return True
                
        return False
