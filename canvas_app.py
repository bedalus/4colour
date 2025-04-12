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
        """
        Updates the 'enclosed' status for all circles by traversing the outer face
        of the graph embedding.
        """
        num_circles = len(self.circles)

        # --- Edge Cases ---
        if num_circles <= 2:
            # With 0, 1, or 2 circles, none can be enclosed.
            for circle in self.circle_lookup.values():
                circle['enclosed'] = False
            # Update debug display if needed after status change
            if self.debug_enabled:
                self.ui_manager.show_debug_info()
            return

        # --- Find Starting Node ---
        start_node_id = -1
        min_y = float('inf')
        min_x_at_min_y = float('inf')

        for circle in self.circle_lookup.values():
            if circle['y'] < min_y:
                min_y = circle['y']
                min_x_at_min_y = circle['x']
                start_node_id = circle['id']
            elif circle['y'] == min_y:
                if circle['x'] < min_x_at_min_y:
                    min_x_at_min_y = circle['x']
                    start_node_id = circle['id']

        if start_node_id == -1:
             # Should not happen if num_circles > 0, but handle defensively
            return

        start_node = self.circle_lookup[start_node_id]

        # --- Initialize Traversal ---
        outer_border_ids = set()
        
        # Handle case where the start node has no connections
        if not start_node['ordered_connections']:
             # If the lowest node has no connections, it's trivially on the border.
             # If it's the *only* node, the edge case handled it.
             # If other nodes exist but aren't connected, they also aren't enclosed.
             # This logic assumes a single connected component for enclosure.
             # A more robust solution might handle disconnected components separately.
            for circle in self.circle_lookup.values():
                circle['enclosed'] = False
            if self.debug_enabled:
                self.ui_manager.show_debug_info()
            return

        # Find the first edge to traverse on the outer boundary.
        # For the lowest node, the edge leaving it with the smallest angle
        # (most counter-clockwise relative to vertical-down) should be part of the outer face.
        # However, our ordered_connections are clockwise from North (0 degrees).
        # The connection *entering* the start_node with the largest angle (closest to 360)
        # corresponds to the edge we "came from" if traversing clockwise.
        # The *next* connection in ordered_connections is the one we take *out*.

        # Calculate entry angles for the start node
        entry_angles = []
        for neighbor_id in start_node['connected_to']:
             angle = self.connection_manager.calculate_connection_entry_angle(start_node_id, neighbor_id)
             entry_angles.append({'neighbor_id': neighbor_id, 'angle': angle})

        # Find the connection with the largest entry angle (last edge if coming from outside)
        entry_angles.sort(key=lambda x: x['angle'], reverse=True)
        last_incoming_neighbor_id = entry_angles[0]['neighbor_id']

        # Find this neighbor in the ordered list
        try:
            last_incoming_index = start_node['ordered_connections'].index(last_incoming_neighbor_id)
        except ValueError:
             # Should not happen if connected_to and ordered_connections are consistent
             print(f"Error: Neighbor {last_incoming_neighbor_id} not found in ordered_connections of {start_node_id}")
             return # Or handle error more gracefully

        # The next connection clockwise is the first edge of our outer face traversal
        first_outgoing_index = (last_incoming_index + 1) % len(start_node['ordered_connections'])
        next_node_id = start_node['ordered_connections'][first_outgoing_index]

        # Initialize traversal state
        outer_border_ids.add(start_node_id)
        previous_node_id = start_node_id
        current_node_id = next_node_id
        
        # Safety break counter
        max_iterations = num_circles + 1 # Should complete in num_circles steps

        # --- Traversal Loop ---
        while current_node_id != start_node_id and max_iterations > 0:
            outer_border_ids.add(current_node_id)
            
            current_circle = self.circle_lookup.get(current_node_id)
            if not current_circle or not current_circle['ordered_connections']:
                # Error: Node disappeared or lost connections during traversal?
                print(f"Error during traversal: Node {current_node_id} invalid or has no connections.")
                break # Exit loop

            ordered_connections = current_circle['ordered_connections']

            # Find the index corresponding to the edge we *entered* from
            try:
                previous_node_index = ordered_connections.index(previous_node_id)
            except ValueError:
                print(f"Error: Previous node {previous_node_id} not found in ordered_connections of {current_node_id}")
                break

            # The next node in clockwise order defines the next edge of the outer face
            next_index = (previous_node_index + 1) % len(ordered_connections)
            next_node_id_candidate = ordered_connections[next_index]

            # Update for next iteration
            previous_node_id = current_node_id
            current_node_id = next_node_id_candidate
            
            max_iterations -= 1

        if max_iterations <= 0:
             print("Warning: Outer face traversal exceeded max iterations. Possible graph inconsistency.")

        # --- Update Status ---
        for circle_id, circle in self.circle_lookup.items():
            circle['enclosed'] = (circle_id not in outer_border_ids)

        # Update debug display if needed after status change
        if self.debug_enabled:
            self.ui_manager.show_debug_info()

def main():
    """Application entry point."""
    root = tk.Tk()
    app = CanvasApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()