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
        
        # Add these new instance variables
        self.extreme_node_indicator = None
        self.extreme_midpoint_indicator = None

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
        """Updates the 'enclosed' status for all circles by traversing the outer boundary."""
        # First, ensure any existing indicators are cleared
        if self.extreme_node_indicator:
            self.canvas.delete(self.extreme_node_indicator)
            self.extreme_node_indicator = None
        if self.extreme_midpoint_indicator:
            self.canvas.delete(self.extreme_midpoint_indicator)
            self.extreme_midpoint_indicator = None

        # Handle empty or small graphs (no enclosure possible)
        if len(self.circles) <= 2:
            for circle in self.circle_lookup.values():
                circle['enclosed'] = False
            return # No boundary to traverse

        # --- Determine Start Node based on Most Extreme Connection Edge ---
        start_node = None
        extreme_handle_pos = None
        extreme_connection_key = None
        min_handle_y = float('inf')
        min_handle_x = float('inf')

        # 1. Find the most extreme connection edge (based on midpoint handle position)
        for conn_key, connection in self.connections.items():
            handle_x, handle_y = self.connection_manager.calculate_midpoint_handle_position(
                connection["from_circle"],
                connection["to_circle"]
            )
            if handle_y < min_handle_y or (handle_y == min_handle_y and handle_x < min_handle_x):
                min_handle_y = handle_y
                min_handle_x = handle_x
                extreme_handle_pos = (handle_x, handle_y)
                extreme_connection_key = conn_key

        # 2. The start node is the extreme connection's most extreme endpoint
        extreme_connection = self.connections[extreme_connection_key]
        node1_id = extreme_connection["from_circle"]
        node2_id = extreme_connection["to_circle"]
        node1 = self.circle_lookup.get(node1_id)
        node2 = self.circle_lookup.get(node2_id)

        # Select the more extreme node (min y, then min x) between the two
        if node1['y'] < node2['y'] or (node1['y'] == node2['y'] and node1['x'] < node2['x']):
            start_node = node1
        else:
            start_node = node2

        # --- End of Start Node Determination ---

        # Draw indicators if in adjust mode
        if self._mode == ApplicationMode.ADJUST:
            # Draw indicator around the determined start_node
            self.extreme_node_indicator = self.canvas.create_oval(
                start_node['x'] - self.circle_radius - 5, start_node['y'] - self.circle_radius - 5,
                start_node['x'] + self.circle_radius + 5, start_node['y'] + self.circle_radius + 5,
                outline="purple", width=2
            )
            # Draw indicator around the extreme midpoint handle, if found
            x, y = extreme_handle_pos
            size = 8
            self.extreme_midpoint_indicator = self.canvas.create_rectangle(
                x - size, y - size, x + size, y + size,
                outline="purple", width=2
            )

        # Initialize boundary tracking
        boundary_nodes = set()
        boundary_nodes.add(start_node['id'])

        # --- Start of Traversal Logic ---
        current_id = start_node['id']
        current_node = start_node

        # Find the initial outgoing edge from the start_node.
        # This is the edge with the smallest angle when measured clockwise from North (0 degrees).
        min_angle = float('inf')
        next_id = None # This will be the ID of the first node to visit *after* start_node

        for neighbor_id in current_node['ordered_connections']:
            # Calculate angle of the connection vector leaving current_node towards neighbor_id
            angle = self._calculate_corrected_angle(current_node, neighbor_id)
            if angle < min_angle:
                min_angle = angle
                next_id = neighbor_id # The neighbor connected by the edge with the minimum angle

        # Traverse the outer boundary clockwise.
        # Start from the 'next_id' found above, keeping track of the node we came from ('previous_id').
        previous_id = start_node['id'] # We start by conceptually moving from start_node to next_id
        while next_id and next_id != start_node['id']:
            # Safety break to prevent infinite loops in case of graph inconsistency
            if len(boundary_nodes) > len(self.circles) + 1: # Allow one extra for safety margin
                 print(f"Warning: Boundary traversal exceeded expected length ({len(boundary_nodes)} > {len(self.circles)}). Breaking loop.")
                 # Mark all as not enclosed as boundary is likely incorrect
                 for circle in self.circle_lookup.values():
                     circle['enclosed'] = False
                 if self.debug_enabled:
                     self.ui_manager.show_debug_info()
                 return # Exit traversal

            # Break if we revisit a node unexpectedly (other than the start node at the end)
            if next_id in boundary_nodes:
                print(f"Warning: Boundary traversal revisited node {next_id} unexpectedly. Breaking loop.")
                # Mark all as not enclosed as boundary is likely incorrect
                for circle in self.circle_lookup.values():
                    circle['enclosed'] = False
                if self.debug_enabled:
                    self.ui_manager.show_debug_info()
                return # Exit traversal

            current_id = next_id
            boundary_nodes.add(current_id) # Mark the current node as part of the boundary

            current_node = self.circle_lookup.get(current_id)
            # If the current node is missing or has no connections, the boundary is broken.
            if not current_node or not current_node.get('ordered_connections'):
                print(f"Warning: Boundary traversal stopped at node {current_id} (missing or no connections).")
                # Mark all as not enclosed as boundary is incomplete
                for circle in self.circle_lookup.values():
                    circle['enclosed'] = False
                if self.debug_enabled:
                    self.ui_manager.show_debug_info()
                return # Exit traversal

            # Find the edge we arrived from (previous_id) in the current node's ordered list.
            try:
                # Ensure ordered_connections is not empty before trying to find index
                if not current_node['ordered_connections']:
                    raise ValueError("Node has no ordered connections")

                prev_idx = current_node['ordered_connections'].index(previous_id)

                # The next edge to follow is the one immediately clockwise from the arrival edge.
                # Use modulo arithmetic to wrap around the list correctly.
                # Corrected: Use +1 for clockwise traversal.
                next_idx = (prev_idx + 1) % len(current_node['ordered_connections'])
                next_id = current_node['ordered_connections'][next_idx]

            except ValueError:
                 # This indicates an inconsistency in the graph data (e.g., previous_id not found).
                 print(f"Warning: Could not find previous node {previous_id} in connections of {current_id}. Boundary traversal incomplete.")
                 # Mark all as not enclosed as boundary is broken
                 for circle in self.circle_lookup.values():
                     circle['enclosed'] = False
                 if self.debug_enabled:
                     self.ui_manager.show_debug_info()
                 return # Exit traversal

            # Update previous_id for the next iteration.
            previous_id = current_id
        # --- End of Traversal Logic ---

        # Update enclosed status for all circles based on whether they were visited during traversal.
        for circle in self.circles:
            # Check if circle ID exists in lookup before accessing
            if circle['id'] in self.circle_lookup:
                 self.circle_lookup[circle['id']]['enclosed'] = circle['id'] not in boundary_nodes
            else:
                 # Handle case where circle might be in self.circles but not lookup (should not happen ideally)
                 print(f"Warning: Circle ID {circle['id']} found in self.circles but not in self.circle_lookup during enclosure update.")


        # Update debug info if enabled.
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