"""
Interaction Handler for the 4colour project.

This module handles user interactions and event bindings.
"""

from color_utils import get_color_from_priority
from app_enums import ApplicationMode  # Import from app_enums instead

ADJUST_MODE_BG = "#FFEEEE"
VCOLOR_FIX_MODE_BG = "#FFDDDD"
HIGHLIGHT_COLOR = 'purple'
HIGHLIGHT_TAG = "temp_highlight"

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
        # Clear any hint text
        self.app.ui_manager.show_hint_text("")
            
        # Don't allow transition to ADJUST mode from SELECTION mode
        # EXCEPTION: Allow if it's for a VCOLOR node
        if self.app._mode == ApplicationMode.SELECTION and new_mode == ApplicationMode.ADJUST:
            if not self.app.has_VCOLOR_nodes():
                print("DEBUG: Blocking SELECTION to ADJUST transition (not for VCOLOR node)")
                return
            else:
                print("DEBUG: Allowing SELECTION to ADJUST transition for VCOLOR node")
        
        print(f"DEBUG: Transitioning from {self.app._mode} to {new_mode}")
        
        old_mode = self.app._mode  # Store the old mode before changing
        
        # Special handling for exiting CREATE mode
        if old_mode == ApplicationMode.CREATE:
             # Lock all non-fixed circles and connections
            for circle in self.app.circles:
                if not circle.get("fixed", False):
                    circle["locked"] = True
            for connection_key, connection_data in self.app.connections.items():
                if not connection_data.get("fixed", False):
                    connection_data["locked"] = True
        
        # Common mode transition handling
        self._prepare_mode_transition(new_mode)
        
        # Update button text
        if self.app.mode_button and not hasattr(self.app, '_stored_mode_button_command'):
            if new_mode == ApplicationMode.ADJUST:
                self.app.mode_button.config(text="Engage create mode")
            else:
                self.app.mode_button.config(text="Engage adjust mode")
    
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
        # Use the deterministic colour assignment
        color_priority = self.app._assign_color_based_on_connections()  # Only get priority
        color_name = get_color_from_priority(color_priority)  # Get colour name for drawing
        
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
            fill=color_name,  # Use derived colour name
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
        """Handle 'y' key press to confirm circle connections."""
        if not self.app.in_selection_mode:
            return
            
        # Store IDs before state gets cleared
        new_circle_id = self.app.newly_placed_circle_id
        
        # First check - prevent connecting to enclosed nodes
        has_enclosed_nodes = False
        for circle_id in (self.app.selected_circles):
            circle = self.app.circle_lookup.get(circle_id)
            if circle and circle.get('enclosed', False):
                has_enclosed_nodes = True
        
        if has_enclosed_nodes:
            self.app.ui_manager.show_hint_text("Cannot connect to enclosed nodes")
            self.cancel_selection(None)
            return

        # Add all connections
        for circle_id in self.app.selected_circles:
            self.app.connection_manager.add_connection(new_circle_id, circle_id)

        # After all connections are made, check for colour conflicts and resolve them once
        if self.app.newly_placed_circle_id and self.app.selected_circles:
            # Check and resolve colour conflicts for the newly placed circle
            self.app.check_and_resolve_color_conflicts(self.app.newly_placed_circle_id)
        
        # Clear selection state
        self.app.selected_circles.clear()
        self.app.in_selection_mode = False
        
        # Update enclosure status 
        self.app._update_enclosure_status()
        
        # Check if the newly placed circle became enclosed
        if self.app.circle_lookup[new_circle_id]['enclosed']:
            self.app.ui_manager.show_hint_text("Node removed: Invalid placement! New nodes must be added to the exterior")
            self.app.circle_manager.remove_circle_by_id(new_circle_id, bypass_lock=True)
            self.app.newly_placed_circle_id = None
            self.app.in_selection_mode = False
            return
        else:
            # Only update last_circle_id if node wasn't removed
            self.app.last_circle_id = new_circle_id
            self.app.newly_placed_circle_id = None
            # Update enclosure status after connections are confirmed
            self.app._update_enclosure_status()
            
        # Update debug info if enabled
        if self.app.debug_enabled:
            self.app.ui_manager.show_debug_info()

    def cancel_selection(self, event):
        """Handle escape key press to cancel circle placement."""
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
            
            # Store the original enclosed status and position
            if circle:
                self.app.drag_state["orig_enclosed"] = circle.get("enclosed", False)
                self.app.drag_state["orig_x"] = circle.get("x", 0)
                self.app.drag_state["orig_y"] = circle.get("y", 0)
            
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

        # Check if a boundary circle became enclosed (before resetting drag state)
        if self.app.drag_state["type"] == "circle":
            circle_id = self.app.drag_state["id"]
            
            # Update enclosure status before checking
            self.app._update_enclosure_status()
            
            # Get the circle after enclosure update
            circle = self.app.circle_lookup.get(circle_id)
            
            # If it was originally not enclosed (on boundary) but now is enclosed
            if (circle and 
                not self.app.drag_state.get("orig_enclosed", True) and 
                circle.get("enclosed", False)):
                
                # Show warning message
                self.app.ui_manager.show_hint_text()
                self.app.ui_manager.show_hint_text("Invalid move! Boundary nodes must remain on the exterior")
                
                # Restore the original position
                orig_x = self.app.drag_state.get("orig_x", circle["x"])
                orig_y = self.app.drag_state.get("orig_y", circle["y"])
                
                # Calculate delta to move back
                delta_x = orig_x - circle["x"]
                delta_y = orig_y - circle["y"]
                
                # Update circle position data and visually move it back
                self.app.canvas.move(circle["canvas_id"], delta_x, delta_y)
                circle["x"] = orig_x
                circle["y"] = orig_y
                
                # Update all connected lines
                self.app.connection_manager.update_connections(circle_id)
        
        # Reset the drag state
        self.reset_drag_state()
        
        # Update enclosure status AFTER drag ends and ordered connections are updated
        if ordered_connections_updated:
             self.app._update_enclosure_status() # Phase 14 Trigger Point
             # The extreme node/midpoint indicators will be updated as part of _update_enclosure_status
             
        # Set the active circles for debug display before updating
        self._update_debug_for_circles(*debug_circle_ids)
        
        # Ensure final state reflects constraints after drag ends
        self._check_violations_and_update_button()

    def _update_connection_visuals(self, connection_key):
        """Updates the visual representation of a single connection."""
        connection = self.app.connections.get(connection_key)
        if not connection:
            return

        from_id = connection["from_circle"]
        to_id = connection["to_circle"]

        # Recalculate curve points
        points = self.app.connection_manager.calculate_curve_points(from_id, to_id)
        
        if points:
            # Update the existing line's coordinates instead of deleting and recreating it
            self.app.canvas.coords(connection["line_id"], *points)

        # Update midpoint handle position if it exists
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
            if has_violations:
                self.app.mode_button.config(state='disabled')
                self.app.ui_manager.show_hint_text("Warning: Connection angle too close to another. Adjust the midpoint until the warning clears.")
                return True
            else:
                self.app.mode_button.config(state='normal')
                self.app.ui_manager.show_hint_text("")
                return False

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

    def switch_to_VCOLOR_fix_mode(self):
        """Switch to ADJUST mode specifically for fixing VCOLOR nodes."""
        # Handle mode transition with specialised flag
        is_transition = self._prepare_mode_transition(ApplicationMode.ADJUST, for_VCOLOR_node_=True)
        
        # Additional setup for VCOLOR node fix mode
        if is_transition and self.app.mode_button:
            # Update button text using an f-string
            button_text = f"Fix {get_color_from_priority(5)}"
            self.app.mode_button.config(text=button_text)
            
            # Store the original mode button's command
            original_command = self.app.mode_button['command']
            self.app._stored_mode_button_command = original_command
            self.app.mode_button.config(
                command=lambda: self.app._focus_after(
                    self.app.handle_fix_VCOLOR_node_button
                )
            )
            print(f"DEBUG: Changed mode button to '{button_text}'") # Also update the debug print to use f-string
    
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
        """Update debug display for specified circles if debug is enabled."""
        if self.app.debug_enabled and circle_ids:
            self.app.ui_manager.set_active_circles(*circle_ids)
            self.app.ui_manager.show_debug_info()
    
    def _is_in_protected_zone(self, x, y):
        return x < self.app.PROXIMITY_LIMIT and y < self.app.PROXIMITY_LIMIT

    def _cleanup_adjust_mode(self):
        """Cleans up UI elements and state specific to ADJUST mode."""
        # Hide midpoint handles
        self.app.connection_manager.hide_midpoint_handles()
        
        # Clear angle visualizations
        self.app.ui_manager.clear_angle_visualizations()
            
        # Reset canvas background
        self.app.canvas.config(bg="white")
        
        # Clear highlight
        if self.app.highlighted_circle_id:
            self.app.canvas.delete(self.app.highlighted_circle_id)
            self.app.highlighted_circle_id = None

    def _cleanup_mode_ui(self, mode):
        """Clean up UI elements specific to the given mode."""
        if mode == ApplicationMode.SELECTION:
            self._clear_selection_state()
        elif mode == ApplicationMode.ADJUST:
            self._cleanup_adjust_mode_ui() # Renamed from _cleanup_adjust_mode

    def _setup_mode_ui(self, mode, for_VCOLOR_node_=False):
        """Set up UI elements specific to the given mode.""" 
        if mode == ApplicationMode.ADJUST:
            self._setup_adjust_mode_ui(for_VCOLOR_node_)

    def _cleanup_adjust_mode_ui(self):
        """Cleans up UI elements and state specific to ADJUST mode."""
        self.app.ui_manager.show_hint_text("")
        self.app.connection_manager.hide_midpoint_handles()
        self.app.ui_manager.clear_angle_visualizations()
        self.app.canvas.config(bg="white")
        if self.app.highlighted_circle_id:
            self.app.canvas.delete(self.app.highlighted_circle_id)
            self.app.highlighted_circle_id = None

    def _setup_adjust_mode_ui(self, for_VCOLOR_node_=False):
        """Sets up UI elements for ADJUST mode."""
        # Display specific hint based on whether it's VCOLOR fix mode or normal adjust mode
        if for_VCOLOR_node_:
            self.app.ui_manager.show_hint_text("Adjust the circle/connections if necessary, then click the 'Fix' button")
            self.app.canvas.config(bg=VCOLOR_FIX_MODE_BG)
        else:
            self.app.ui_manager.show_hint_text("The last node placed and its connections can be adjusted")
            self.app.canvas.config(bg=ADJUST_MODE_BG)
            
        self.app.connection_manager.show_midpoint_handles()
        self.app._update_enclosure_status()
        self._unlock_and_highlight_last_node()

    def _unlock_and_highlight_last_node(self):
        """Unlocks the last placed node and its connections, and highlights it."""
        if self.app.last_circle_id is not None and self.app.last_circle_id > 0:
            last_circle_data = self.app.circle_lookup.get(self.app.last_circle_id)
            if last_circle_data and not last_circle_data.get("fixed", False):
                # Unlock the circle
                last_circle_data["locked"] = False
                print(f"DEBUG: Unlocked last node {self.app.last_circle_id} for ADJUST mode")

                # Draw highlight
                radius = self.app.circle_radius
                x, y = last_circle_data["x"], last_circle_data["y"]
                if self.app.highlighted_circle_id:
                    self.app.canvas.delete(self.app.highlighted_circle_id)
                self.app.highlighted_circle_id = self.app.canvas.create_oval(
                    x - radius - 3, y - radius - 3,
                    x + radius + 3, y + radius + 3,
                    outline=HIGHLIGHT_COLOR, width=3, tags=HIGHLIGHT_TAG
                )

                # Unlock its connections
                for connected_id in last_circle_data.get("connected_to", []):
                    connection_key = self.app.connection_manager.get_connection_key(self.app.last_circle_id, connected_id)
                    connection = self.app.connections.get(connection_key)
                    if connection and not connection.get("fixed", False):
                        connection["locked"] = False

    def _prepare_mode_transition(self, new_mode, for_VCOLOR_node_=False):
        """Handle common mode transition tasks.""" 
        old_mode = self.app._mode

        # Skip if already in the target mode or blocked
        if old_mode == new_mode:
            return False

        # Clean up previous mode UI and unbind events
        self._cleanup_mode_ui(old_mode)
        self.unbind_mode_events(old_mode)

        # Set new mode
        self.app._mode = new_mode

        # Bind events and set up new mode UI
        self.bind_mode_events(new_mode)
        self._setup_mode_ui(new_mode, for_VCOLOR_node_)

        # Special handling for ADJUST mode setup (unlocking last node is now in _setup_adjust_mode_ui)
        if new_mode == ApplicationMode.ADJUST:
            # Return True only if the transition was specifically for a VCOLOR node fix
            return for_VCOLOR_node_

        return True # Return True indicating a successful transition occurred
