"""
Canvas Application - 4colour project

This module implements a simple drawing canvas using tkinter.
"""

import tkinter as tk
from tkinter import ttk
import math  # Add math import for infinity

# Import the enum from the new location
from app_enums import ApplicationMode

# Import our component modules
from ui_manager import UIManager
from circle_manager import CircleManager
from connection_manager import ConnectionManager  
from interaction_handler import InteractionHandler
from color_manager import ColorManager

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
        self.midpoint_radius = 5  # Size of the midpoint handle
        
        # Initialize application state
        self.circles = []
        self.next_id = 1
        self.last_circle_id = None
        self.circle_lookup = {}
        self.connections = {}
        self.midpoint_handles = {}
        
        # Debug overlay
        self.debug_enabled = False
        self.debug_text = None
        
        # Selection mode properties
        self.selected_circles = []
        self.selection_indicators = {}
        self.hint_text_id = None
        self.newly_placed_circle_id = None
        
        # Edit mode properties
        self.edit_hint_text_id = None
        
        # Current application mode
        self._mode = ApplicationMode.CREATE
        
        # Keep track of bound events for cleanup
        self._bound_events = {
            ApplicationMode.CREATE: False,
            ApplicationMode.SELECTION: False,
            ApplicationMode.ADJUST: False
        }
        
        # Drag state management
        self.drag_state = {
            "active": False,
            "type": None,
            "id": None,
            "start_x": 0,
            "start_y": 0,
            "last_x": 0,
            "last_y": 0
        }
        
        # Store drawn items for potential resize handling
        self.drawn_items = []
        
        # Initialize UI components
        self._setup_ui()
        
        # Initialize component managers
        self.ui_manager = UIManager(self)
        self.circle_manager = CircleManager(self)
        self.connection_manager = ConnectionManager(self)
        self.interaction_handler = InteractionHandler(self)
        self.color_manager = ColorManager(self)

        # Initialize drag state
        self.interaction_handler.reset_drag_state()  # Moved reset call here
        
        # Bind initial events for CREATE mode
        self.interaction_handler.bind_mode_events(self._mode)

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
        
        # Initialize bindings for create mode
        self.canvas.bind("<Button-1>", self._draw_on_click)
        self._bound_events[ApplicationMode.CREATE] = True

    # Properties for backward compatibility
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
    
    # Delegate methods to the appropriate managers
    def _focus_after(self, command_func):
        return self.ui_manager.focus_after(command_func)
        
    def _toggle_debug(self):
        return self.ui_manager.toggle_debug()
        
    def _show_debug_info(self):
        return self.ui_manager.show_debug_info()
        
    def _clear_canvas(self):
        return self.ui_manager.clear_canvas()
        
    def _draw_on_click(self, event):
        return self.interaction_handler.draw_on_click(event)
        
    def _toggle_circle_selection(self, circle_id):
        return self.interaction_handler.toggle_circle_selection(circle_id)
        
    def _show_hint_text(self):
        return self.ui_manager.show_hint_text()
        
    def _confirm_selection(self, event):
        return self.interaction_handler.confirm_selection(event)
        
    def _toggle_mode(self):
        return self.interaction_handler.toggle_mode()
        
    def _show_edit_hint_text(self):
        return self.ui_manager.show_edit_hint_text()
        
    def _reset_drag_state(self):
        return self.interaction_handler.reset_drag_state()
        
    def _drag_start(self, event):
        return self.interaction_handler.drag_start(event)
        
    def _drag_motion(self, event):
        return self.interaction_handler.drag_motion(event)
        
    def _drag_end(self, event):
        return self.interaction_handler.drag_end(event)
        
    def _drag_circle_motion(self, x, y, dx, dy):
        return self.interaction_handler.drag_circle_motion(x, y, dx, dy)
        
    def _drag_midpoint_motion(self, x, y):
        return self.interaction_handler.drag_midpoint_motion(x, y)
        
    def _remove_circle(self, event):
        return self.circle_manager.remove_circle(event)
        
    def _remove_circle_by_id(self, circle_id):
        return self.circle_manager.remove_circle_by_id(circle_id)
        
    def _remove_circle_connections(self, circle_id):
        return self.connection_manager.remove_circle_connections(circle_id)
        
    def _handle_last_circle_removed(self):
        return self.circle_manager.handle_last_circle_removed()
        
    def _set_application_mode(self, new_mode):
        return self.interaction_handler.set_application_mode(new_mode)
        
    def _bind_mode_events(self, mode):
        return self.interaction_handler.bind_mode_events(mode)
        
    def _unbind_mode_events(self, mode):
        return self.interaction_handler.unbind_mode_events(mode)
        
    def _bind_create_mode_events(self):
        return self.interaction_handler.bind_create_mode_events()
        
    def _unbind_create_mode_events(self):
        return self.interaction_handler.unbind_create_mode_events()
        
    def _bind_selection_mode_events(self):
        return self.interaction_handler.bind_selection_mode_events()
        
    def _unbind_selection_mode_events(self):
        return self.interaction_handler.unbind_selection_mode_events()
        
    def _bind_adjust_mode_events(self):
        return self.interaction_handler.bind_adjust_mode_events()
        
    def _unbind_adjust_mode_events(self):
        return self.interaction_handler.unbind_adjust_mode_events()
        
    def _cancel_selection(self, event):
        return self.interaction_handler.cancel_selection(event)

    # Public methods from the original implementation
    def add_connection(self, from_id, to_id):
        return self.connection_manager.add_connection(from_id, to_id)
        
    def get_circle_at_coords(self, x, y):
        return self.circle_manager.get_circle_at_coords(x, y)
        
    def get_connection_curve_offset(self, from_id, to_id):
        return self.connection_manager.get_connection_curve_offset(from_id, to_id)
        
    def update_connection_curve(self, from_id, to_id, curve_x, curve_y):
        return self.connection_manager.update_connection_curve(from_id, to_id, curve_x, curve_y)

    # Color-related methods delegated to ColorManager
    def _assign_color_based_on_connections(self, circle_id=None):
        return self.color_manager.assign_color_based_on_connections(circle_id)
        
    def _check_and_resolve_color_conflicts(self, circle_id):
        return self.color_manager.check_and_resolve_color_conflicts(circle_id)
        
    def _reassign_color_network(self, circle_id):
        return self.color_manager.reassign_color_network(circle_id)
        
    def _update_circle_color(self, circle_id, color_priority):
        return self.color_manager.update_circle_color(circle_id, color_priority)

    # Connection-related methods delegated to ConnectionManager
    def _calculate_midpoint(self, from_circle, to_circle):
        return self.connection_manager.calculate_midpoint(from_circle, to_circle)
        
    def _calculate_curve_points(self, from_id, to_id):
        return self.connection_manager.calculate_curve_points(from_id, to_id)
        
    def _draw_midpoint_handle(self, connection_key, x, y):
        return self.connection_manager.draw_midpoint_handle(connection_key, x, y)
        
    def _show_midpoint_handles(self):
        return self.connection_manager.show_midpoint_handles()
        
    def _hide_midpoint_handles(self):
        return self.connection_manager.hide_midpoint_handles()
        
    def _calculate_midpoint_handle_position(self, from_id, to_id):
        return self.connection_manager.calculate_midpoint_handle_position(from_id, to_id)
        
    def _update_connections(self, circle_id):
        return self.connection_manager.update_connections(circle_id)

    def _update_enclosure_status(self):
        """Updates the 'enclosed' status for all circles by traversing the outer boundary.
        
        Algorithm: 
        1. Find topmost-leftmost circle as starting point
        2. Account for curved connections when finding boundary
        3. Traverse clockwise around outer boundary
        4. Mark all circles not on boundary as enclosed
        """
        if len(self.circles) <= 2:
            # 0-2 circles cannot enclose anything
            for circle in self.circle_lookup.values():
                circle['enclosed'] = False
            return

        # Find topmost-leftmost node (minimum y, then minimum x due to inverted y-axis)
        start_node = None
        min_y = float('inf')
        min_x = float('inf')
        for circle in self.circles:
            if circle['y'] < min_y or (circle['y'] == min_y and circle['x'] < min_x):
                min_y = circle['y']
                min_x = circle['x']
                start_node = circle

        if not start_node or not start_node['ordered_connections']:
            # No valid starting point or no connections
            for circle in self.circle_lookup.values():
                circle['enclosed'] = False
            return

        # Initialize boundary tracking
        boundary_nodes = set()
        boundary_nodes.add(start_node['id'])
        
        # Find first boundary edge by calculating corrected angles
        current_id = start_node['id']
        current_node = start_node

        # Find initial outgoing edge - crucial fix for y-axis inversion
        min_angle = float('inf')
        next_id = None
        
        for neighbor_id in current_node['ordered_connections']:
            # Calculate angle with correction for inverted y-axis
            angle = self._calculate_corrected_angle(current_node, neighbor_id)
            if angle < min_angle:  # Use minimum angle for inverted y-axis
                min_angle = angle
                next_id = neighbor_id

        if not next_id:
            return

        # Traverse boundary clockwise
        while next_id and next_id != start_node['id']:
            current_id = next_id
            boundary_nodes.add(current_id)
            
            current_node = self.circle_lookup[current_id]
            if not current_node['ordered_connections']:
                break

            # Get previous node's position in ordered connections
            try:
                prev_idx = current_node['ordered_connections'].index(
                    previous_id if 'previous_id' in locals() else start_node['id']
                )
                # Take next connection clockwise (account for end of list)
                next_idx = (prev_idx + 1) % len(current_node['ordered_connections'])
                next_id = current_node['ordered_connections'][next_idx]
            except ValueError:
                break  # Exit if we can't find previous node in connections
                
            previous_id = current_id

        # Update enclosed status for all circles
        for circle in self.circles:
            circle['enclosed'] = circle['id'] not in boundary_nodes

        if self.debug_enabled:
            self.ui_manager.show_debug_info()

    def _calculate_corrected_angle(self, circle, neighbor_id):
        """Calculate angle between circles with correction for inverted y-axis.
        
        Args:
            circle: Dictionary containing the source circle's data
            neighbor_id: ID of the neighboring circle
            
        Returns:
            float: Corrected angle in degrees (0-360)
        """
        neighbor = self.circle_lookup.get(neighbor_id)
        if not neighbor:
            return 0
            
        # Get vector components
        dx = neighbor['x'] - circle['x']
        dy = neighbor['y'] - circle['y']
        
        # Account for any curve offset
        curve_x, curve_y = self.connection_manager.get_connection_curve_offset(
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

def main():
    """Application entry point."""
    root = tk.Tk()
    app = CanvasApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()