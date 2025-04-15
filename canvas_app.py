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
from boundary_manager import BoundaryManager

class CanvasApplication:
    """Main application class for the drawing canvas."""
    
    # Constants for fixed nodes
    FIXED_NODE_A_ID = -1
    FIXED_NODE_B_ID = -2
    FIXED_NODE_A_POS = (15, 60)  # Increased by 50% from (10, 40)
    FIXED_NODE_B_POS = (60, 15)  # Increased by 50% from (40, 10)
    PROXIMITY_LIMIT = 75  # Increased proximity limit (was 50)
    
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
        self.highlighted_circle_id = None  # ID for the temporary highlight circle
        
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
        self.boundary_manager = BoundaryManager(self)

        # Initialize drag state
        self.interaction_handler.reset_drag_state()  # Moved reset call here
        
        # Bind initial events for CREATE mode
        self.interaction_handler.bind_mode_events(self._mode)
        
        # Create fixed outer nodes
        self._initialize_fixed_nodes()
        
        # Bind to window resize event
        self.root.bind("<Configure>", self._on_window_resize)

    def _on_window_resize(self, event):
        """Update canvas dimensions when window is resized.
        
        Args:
            event: Window resize event
        """
        if event.widget == self.root:
            # Small delay to allow canvas to finish resizing
            self.root.after(100, self._update_canvas_dimensions)
    
    def _update_canvas_dimensions(self):
        """Update stored canvas dimensions to match actual canvas size."""
        # Get the actual canvas dimensions
        new_width = self.canvas.winfo_width()
        new_height = self.canvas.winfo_height()
        
        # Only update if dimensions have actually changed
        if new_width != self.canvas_width or new_height != self.canvas_height:
            self.canvas_width = new_width
            self.canvas_height = new_height
            
            # If debug is enabled, refresh the debug display with new position
            if self.debug_enabled:
                self.ui_manager.show_debug_info()
            
            # Update any other UI elements that depend on canvas dimensions
            if self.hint_text_id:
                self.ui_manager.show_hint_text()
            
            if self.edit_hint_text_id:
                self.ui_manager.show_edit_hint_text()

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
        
        # Remove the "Fix Red" button creation - we'll reuse the mode button instead
        
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
    def _calculate_curve_points(self, from_id, to_id):
        return self.connection_manager.calculate_curve_points(from_id, to_id)
        
    def _show_midpoint_handles(self):
        return self.connection_manager.show_midpoint_handles()
        
    def _hide_midpoint_handles(self):
        return self.connection_manager.hide_midpoint_handles()
        
    def _update_connections(self, circle_id):
        return self.connection_manager.update_connections(circle_id)

    def _update_enclosure_status(self):
        """Delegates the enclosure status update to the boundary manager."""
        return self.boundary_manager.update_enclosure_status()

    def _initialize_fixed_nodes(self):
        """Create and connect the two fixed outer nodes that guarantee a starting point for outer face traversal."""
        # Create fixed node A - Yellow (color_priority 1)
        x_a, y_a = self.FIXED_NODE_A_POS
        node_a_canvas_id = self.canvas.create_oval(
            x_a - self.circle_radius,
            y_a - self.circle_radius,
            x_a + self.circle_radius,
            y_a + self.circle_radius,
            fill="yellow",  # Color priority 1 = yellow
            outline="black",
            tags="fixed_circle"  # Special tag to identify fixed nodes
        )
        
        # Create fixed node B - Green (color_priority 2)
        x_b, y_b = self.FIXED_NODE_B_POS
        node_b_canvas_id = self.canvas.create_oval(
            x_b - self.circle_radius,
            y_b - self.circle_radius,
            x_b + self.circle_radius,
            y_b + self.circle_radius,
            fill="green",  # Color priority 2 = green
            outline="black",
            tags="fixed_circle"
        )
        
        # Add fixed node A to circles data structures
        node_a_data = {
            "id": self.FIXED_NODE_A_ID,
            "canvas_id": node_a_canvas_id,
            "x": x_a,
            "y": y_a,
            "color_priority": 1,  # Yellow by default
            "connected_to": [self.FIXED_NODE_B_ID],  # Will connect to node B
            "ordered_connections": [self.FIXED_NODE_B_ID],
            "enclosed": False,
            "fixed": True  # Mark as a fixed node
        }
        
        # Add fixed node B to circles data structures
        node_b_data = {
            "id": self.FIXED_NODE_B_ID,
            "canvas_id": node_b_canvas_id,
            "x": x_b,
            "y": y_b,
            "color_priority": 2,  # Green by default
            "connected_to": [self.FIXED_NODE_A_ID],  # Will connect to node A
            "ordered_connections": [self.FIXED_NODE_A_ID],
            "enclosed": False,
            "fixed": True  # Mark as a fixed node
        }
        
        # Add to circles list and lookup dictionary
        self.circles.append(node_a_data)
        self.circles.append(node_b_data)
        self.circle_lookup[self.FIXED_NODE_A_ID] = node_a_data
        self.circle_lookup[self.FIXED_NODE_B_ID] = node_b_data
        
        # Create connection between the fixed nodes
        connection_key = f"{self.FIXED_NODE_A_ID}_{self.FIXED_NODE_B_ID}"
        points = self._calculate_curve_points(self.FIXED_NODE_A_ID, self.FIXED_NODE_B_ID)
        
        # Draw the connection line
        line_id = self.canvas.create_line(
            points,
            width=1,
            smooth=True,
            tags=("line", "fixed_connection")  # Special tag for fixed connection
        )
        
        # Ensure the line is below all circles
        self.canvas.lower("line")
        
        # Store connection details
        self.connections[connection_key] = {
            "line_id": line_id,
            "from_circle": self.FIXED_NODE_A_ID,
            "to_circle": self.FIXED_NODE_B_ID,
            "curve_X": 0,
            "curve_Y": 0,
            "fixed": True  # Mark as a fixed connection
        }
        
        # Update ordered connections for both nodes
        self.connection_manager.update_ordered_connections(self.FIXED_NODE_A_ID)
        self.connection_manager.update_ordered_connections(self.FIXED_NODE_B_ID)
        
        # Update enclosure status after creating fixed nodes
        self._update_enclosure_status()

    def handle_red_node_creation(self, circle_id):
        """Delegate to color manager's handle_red_node_creation method."""
        return self.color_manager.handle_red_node_creation(circle_id)

    def handle_red_node_fixed(self):
        """Delegate to color manager's handle_red_node_fixed method."""
        return self.color_manager.handle_red_node_fixed()

    def _fix_red_node(self):
        """Delegate to color manager's handle_fix_red_node_button method."""
        return self.color_manager.handle_fix_red_node_button()

def main():
    """Application entry point."""
    root = tk.Tk()
    app = CanvasApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()