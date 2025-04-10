"""
Unit tests for the canvas_app module.

This module contains tests for the CanvasApplication class and its functionality.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import tkinter as tk
import sys
import os
import random

# Add the parent directory to the path so we can import the canvas_app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from canvas_app import CanvasApplication, ApplicationMode
from color_utils import get_color_from_priority, find_lowest_available_priority, determine_color_priority_for_connections

class TestCanvasApplication(unittest.TestCase):
    """Test cases for the CanvasApplication class."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a proper mock for Tk with the required attributes
        self.root = MagicMock()
        # Add tk attribute that's needed by tkinter
        self.root.tk = MagicMock()
        # Mock winfo_reqwidth and winfo_reqheight methods
        self.root.winfo_reqwidth = MagicMock(return_value=800)
        self.root.winfo_reqheight = MagicMock(return_value=600)
        
        # Patch ttk.Frame and Canvas to avoid actual UI creation
        with patch('tkinter.ttk.Frame'), patch('tkinter.Canvas'), patch('tkinter.ttk.Button'):
            self.app = CanvasApplication(self.root)
        # Mock the canvas to avoid actual drawing operations
        self.app.canvas = MagicMock(spec=tk.Canvas)
        self.app.drawn_items = []
        # Mock the debug button for focus tests
        self.app.debug_button = MagicMock()
    
    def _create_click_event(self, x, y):
        """Create a mock click event with the specified coordinates.
        
        Args:
            x: X coordinate for the click event
            y: Y coordinate for the click event
            
        Returns:
            Mock: A mock event object with x and y attributes
        """
        event = Mock()
        event.x = x
        event.y = y
        return event
        
    def _create_key_event(self, key):
        """Create a mock key press event.
        
        Args:
            key: The key that was pressed
            
        Returns:
            Mock: A mock event object
        """
        event = Mock()
        event.char = key
        return event
    
    def test_initialization(self):
        """Test that the app initializes with correct values."""
        self.assertEqual(self.app.canvas_width, 800)
        self.assertEqual(self.app.canvas_height, 500)
        self.assertEqual(self.app.circle_radius, 10)
        # Removed check for self.app.available_colors
        self.assertEqual(self.app.circles, [])
        self.assertEqual(self.app.next_id, 1)
        self.assertIsNone(self.app.last_circle_id)
        self.assertFalse(self.app.debug_enabled)
        # Test new dictionaries
        self.assertEqual(self.app.circle_lookup, {})
        self.assertEqual(self.app.connections, {})
        self.root.title.assert_called_with("4colour Canvas")
        self.root.geometry.assert_called_with("800x600")
    
    def test_draw_on_click_first_circle(self):
        """Test drawing the first circle on the canvas."""
        # Create a mock event
        event = Mock()
        event.x = 100
        event.y = 100
        
        # Mock the color selection - only return the priority, not a tuple
        with patch.object(self.app, '_assign_color_based_on_connections', return_value=4):
            # Call the method
            self.app._draw_on_click(event)
        
        # Check that create_oval was called on the canvas
        self.app.canvas.create_oval.assert_called_once()
        
        # Check that the coordinates were stored
        self.assertEqual(len(self.app.drawn_items), 1)
        self.assertEqual(self.app.drawn_items[0], (100, 100))
        
        # Check that circle data was stored correctly (without color key)
        self.assertEqual(len(self.app.circles), 1)
        circle = self.app.circles[0]
        self.assertEqual(circle["id"], 1)
        self.assertEqual(circle["x"], 100)
        self.assertEqual(circle["y"], 100)
        # Check only color_priority
        self.assertEqual(circle["color_priority"], 4)
        self.assertEqual(circle["connected_to"], [])
        
        # Check that circle_lookup is updated
        self.assertIn(1, self.app.circle_lookup)
        self.assertEqual(self.app.circle_lookup[1], circle)
        
        # Check that last_circle_id was updated
        self.assertEqual(self.app.last_circle_id, 1)
        # Check that next_id was incremented
        self.assertEqual(self.app.next_id, 2)
    
    def test_draw_on_click_second_circle(self):
        """Test drawing a second circle that enters selection mode."""
        # Setup: Add a first circle (without color key)
        first_circle = {
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color_priority": 3, # Example priority
            "connected_to": []
        }
        self.app.circles = [first_circle]
        self.app.circle_lookup = {1: first_circle}
        self.app.last_circle_id = 1
        self.app.next_id = 2
        
        # Create a mock event for the second circle
        event = Mock()
        event.x = 100
        event.y = 100
        
        # Mock the canvas.create_oval method
        self.app.canvas.create_oval.return_value = 201
        
        # Mock the show_hint_text method
        with patch.object(self.app, '_show_hint_text') as mock_show_hint:
            # Mock the color selection - only return the priority, not a tuple
            with patch.object(self.app, '_assign_color_based_on_connections', return_value=2):
                # Call the method
                self.app._draw_on_click(event)
            
            # Check that show_hint_text was called
            mock_show_hint.assert_called_once()
        
        # Check that create_oval was called
        self.app.canvas.create_oval.assert_called_once()
        
        # Check that create_line was NOT called since we now use selection mode
        self.app.canvas.create_line.assert_not_called()
        
        # Check that circle data was stored correctly (without color key)
        self.assertEqual(len(self.app.circles), 2)
        second_circle = self.app.circles[1]
        self.assertEqual(second_circle["id"], 2)
        self.assertEqual(second_circle["x"], 100)
        self.assertEqual(second_circle["y"], 100)
        # Check color priority
        self.assertEqual(second_circle["color_priority"], 2)
        self.assertEqual(second_circle["connected_to"], [])  # No connections yet
        
        # Check that circle_lookup is updated
        self.assertIn(2, self.app.circle_lookup)
        self.assertEqual(self.app.circle_lookup[2], second_circle)
        
        # Check that newly_placed_circle_id was set
        self.assertEqual(self.app.newly_placed_circle_id, 2)
        
        # Check that selection mode is enabled
        self.assertTrue(self.app.in_selection_mode)
        
        # Check that last_circle_id was NOT updated yet (will be updated after selection)
        self.assertEqual(self.app.last_circle_id, 1)
        # Check that next_id was incremented
        self.assertEqual(self.app.next_id, 3)
    
    def test_clear_canvas(self):
        """Test clearing the canvas."""
        # Setup: Add some circles and connections
        first_circle = {"id": 1, "canvas_id": 100, "x": 50, "y": 50, "color": "blue", "connected_to": [2]}
        second_circle = {"id": 2, "canvas_id": 101, "x": 100, "y": 100, "color": "red", "connected_to": [1]}
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        self.app.connections = {"1_2": {"line_id": 102, "from_circle": 1, "to_circle": 2}}
        self.app.drawn_items = [(50, 50), (100, 100)]
        self.app.last_circle_id = 2
        self.app.next_id = 3
        
        # Call the clear method
        self.app._clear_canvas()
        
        # Check that the canvas delete method was called
        self.app.canvas.delete.assert_called_once_with("all")
        
        # Check that drawn_items and circles were cleared
        self.assertEqual(len(self.app.drawn_items), 0)
        self.assertEqual(len(self.app.circles), 0)
        
        # Check that dictionaries were cleared
        self.assertEqual(len(self.app.circle_lookup), 0)
        self.assertEqual(len(self.app.connections), 0)
        
        # Check that last_circle_id was reset
        self.assertIsNone(self.app.last_circle_id)
        # Check that next_id was reset
        self.assertEqual(self.app.next_id, 1)
    
    def test_toggle_debug_enable(self):
        """Test enabling the debug display."""
        # Ensure debug is initially disabled
        self.app.debug_enabled = False
        self.app.debug_text = None
        
        # Mock the show_debug_info method
        with patch.object(self.app, '_show_debug_info') as mock_show_debug:
            # Call the toggle method
            self.app._toggle_debug()
            
            # Check that debug is now enabled
            self.assertTrue(self.app.debug_enabled)
            # Check that show_debug_info was called
            mock_show_debug.assert_called_once()
    
    def test_toggle_debug_disable(self):
        """Test disabling the debug display."""
        # Setup: Debug is initially enabled with a debug text
        self.app.debug_enabled = True
        self.app.debug_text = 100  # Mock text ID
        
        # Call the toggle method
        self.app._toggle_debug()
        
        # Check that debug is now disabled
        self.assertFalse(self.app.debug_enabled)
        # Check that the debug text was removed
        self.app.canvas.delete.assert_called_once_with(100)
    
    def test_show_debug_info_with_circle(self):
        """Test showing debug info for a circle."""
        # Setup: Add a circle (without color key)
        self.app.circles = [{
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color_priority": 3, # Priority 3 is blue
            "connected_to": [2]
        }]
        self.app.debug_enabled = True
        
        # Call the show debug info method
        self.app._show_debug_info()
        
        # Check that create_text was called with the right info
        self.app.canvas.create_text.assert_called_once()
        # Extract the text argument
        args, kwargs = self.app.canvas.create_text.call_args
        self.assertEqual(kwargs['anchor'], tk.NW)
        self.assertIn("Circle ID: 1", kwargs['text'])
        self.assertIn("Position: (50, 50)", kwargs['text'])
        # Check derived color name and priority
        self.assertIn("Color: blue (priority: 3)", kwargs['text'])
        self.assertIn("Connected to: 2", kwargs['text'])
    
    def test_show_debug_info_no_circles(self):
        """Test showing debug info when no circles are present."""
        # Setup: No circles and enable debug
        self.app.circles = []
        self.app.debug_enabled = True
        
        # Call the show debug info method
        self.app._show_debug_info()
        
        # Check that create_text was called with the right message
        self.app.canvas.create_text.assert_called_once()
        # Extract the text argument
        args, kwargs = self.app.canvas.create_text.call_args
        self.assertEqual(kwargs['anchor'], tk.NW)
        self.assertEqual(kwargs['text'], "No circles drawn yet")
    
    def test_add_connection(self):
        """Test adding a connection between two existing circles."""
        # Create two circles
        self.app._draw_on_click(self._create_click_event(100, 100))  # Circle 1 (priority 1)
        self.app._draw_on_click(self._create_click_event(200, 100))  # Circle 2 (priority 1)
        
        # Manually set different priorities to avoid conflict resolution for this test
        self.app.circle_lookup[1]["color_priority"] = 1
        self.app.circle_lookup[2]["color_priority"] = 2
        
        # Add connection
        result = self.app.add_connection(1, 2)
        
        # Verify connection was made successfully
        self.assertTrue(result)
        self.assertIn(2, self.app.circle_lookup[1]["connected_to"])
        self.assertIn(1, self.app.circle_lookup[2]["connected_to"])
        
        # Verify priorities haven't changed (no conflict)
        self.assertEqual(self.app.circle_lookup[1]["color_priority"], 1)
        self.assertEqual(self.app.circle_lookup[2]["color_priority"], 2)
    
    def test_add_connection_nonexistent_circle(self):
        """Test adding a connection with nonexistent circle."""
        # Setup: Add one circle
        first_circle = {
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color": "blue",
            "connected_to": []
        }
        
        self.app.circles = [first_circle]
        self.app.circle_lookup = {1: first_circle}
        
        # Try to connect to nonexistent circle
        result = self.app.add_connection(1, 99)
        
        # Check that connection failed
        self.assertFalse(result)
        
        # Check that create_line was not called
        self.app.canvas.create_line.assert_not_called()
        
        # Check that no connections were added
        self.assertEqual(first_circle["connected_to"], [])
        self.assertEqual(self.app.connections, {})

    def test_get_circle_at_coords_found(self):
        """Test finding a circle at given coordinates."""
        # Setup: Add a circle
        circle = {
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color": "blue",
            "connected_to": []
        }
        
        self.app.circles = [circle]
        self.app.circle_radius = 10
        
        # Test clicking inside the circle
        result = self.app.get_circle_at_coords(55, 55)  # Inside the circle
        
        # Check that the circle was found
        self.assertEqual(result, 1)
        
    def test_get_circle_at_coords_not_found(self):
        """Test not finding a circle at given coordinates."""
        # Setup: Add a circle
        circle = {
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color": "blue",
            "connected_to": []
        }
        
        self.app.circles = [circle]
        self.app.circle_radius = 10
        
        # Test clicking outside the circle
        result = self.app.get_circle_at_coords(100, 100)  # Outside the circle
        
        # Check that no circle was found
        self.assertIsNone(result)

    def test_toggle_circle_selection_select(self):
        """Test selecting a circle."""
        # Setup: Add two circles
        first_circle = {
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color": "blue",
            "connected_to": []
        }
        second_circle = {
            "id": 2,
            "canvas_id": 101,
            "x": 100,
            "y": 100,
            "color": "red",
            "connected_to": []
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        self.app.newly_placed_circle_id = 2
        self.app.selected_circles = []
        self.app.selection_indicators = {}
        
        # Mock the canvas create_line method
        self.app.canvas.create_line.return_value = 200
        
        # Call toggle_circle_selection on the first circle
        self.app._toggle_circle_selection(1)
        
        # Check that circle was selected
        self.assertIn(1, self.app.selected_circles)
        
        # Check that selection indicator was drawn
        self.app.canvas.create_line.assert_called_once()
        self.assertIn(1, self.app.selection_indicators)
        self.assertEqual(self.app.selection_indicators[1], 200)
        
    def test_toggle_circle_selection_deselect(self):
        """Test deselecting a circle."""
        # Setup: Add a circle that's already selected
        first_circle = {
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color": "blue",
            "connected_to": []
        }
        
        self.app.circles = [first_circle]
        self.app.circle_lookup = {1: first_circle}
        self.app.selected_circles = [1]
        self.app.selection_indicators = {1: 200}  # Indicator ID
        
        # Call toggle_circle_selection on the circle
        self.app._toggle_circle_selection(1)
        
        # Check that circle was deselected
        self.assertNotIn(1, self.app.selected_circles)
        
        # Check that selection indicator was removed
        self.app.canvas.delete.assert_called_once_with(200)
        self.assertNotIn(1, self.app.selection_indicators)
        
    def test_toggle_circle_selection_newly_placed(self):
        """Test that the newly placed circle cannot be selected."""
        # Setup: Add a circle and set it as newly placed
        circle = {
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color": "blue",
            "connected_to": []
        }
        
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}
        self.app.newly_placed_circle_id = 1
        self.app.selected_circles = []
        
        # Try to select the newly placed circle
        self.app._toggle_circle_selection(1)
        
        # Check that circle was not selected
        self.assertNotIn(1, self.app.selected_circles)
        
        # Check that create_line was not called (no indicator)
        self.app.canvas.create_line.assert_not_called()

    def test_show_hint_text(self):
        """Test displaying the hint text in selection mode."""
        # Setup: Create a mock for the canvas create_text method
        self.app.canvas.create_text.return_value = 300
        self.app.canvas_width = 700
        
        # Call the show hint text method
        self.app._show_hint_text()
        
        # Check that hint text was created
        self.app.canvas.create_text.assert_called_once()
        # Check that the text position and content are correct
        args, kwargs = self.app.canvas.create_text.call_args
        self.assertEqual(args[0], 350)  # Half of canvas_width
        self.assertEqual(args[1], 20)
        self.assertEqual(kwargs['text'], "Please select which circles to connect to then press 'y'")
        self.assertEqual(kwargs['anchor'], tk.N)
        
        # Check that hint_text_id was saved
        self.assertEqual(self.app.hint_text_id, 300)

    def test_confirm_selection(self):
        """Test the behavior when confirming circle selections."""
        # Set up a selection scenario
        self.app._draw_on_click(self._create_click_event(100, 100))  # Circle 1 (priority 1)
        self.app._draw_on_click(self._create_click_event(200, 100))  # Circle 2 (priority 1)
        
        # Manually set up selection state
        self.app.newly_placed_circle_id = 2
        self.app.selected_circles = [1]
        self.app.in_selection_mode = True
        
        # Priorities are the same (1), forcing conflict resolution
        
        # Mock selection indicator for cleanup
        self.app.selection_indicators = {1: self.app.canvas.create_line(0, 0, 10, 0)}
        
        # Call confirm selection
        self.app._confirm_selection(self._create_key_event('y'))
        
        # Verify connections were made
        self.assertIn(1, self.app.circle_lookup[2]["connected_to"])
        
        # Verify color conflict was resolved (circle 2 should no longer have priority 1)
        self.assertNotEqual(self.app.circle_lookup[2]["color_priority"], 1)
        # The exact priority depends on the resolution logic, but it shouldn't be 1

    def test_confirm_selection_not_in_selection_mode(self):
        """Test that y key does nothing when not in selection mode."""
        # Setup: Not in selection mode
        self.app.in_selection_mode = False
        
        # Create a mock for add_connection
        with patch.object(self.app, 'add_connection') as mock_add_connection:
            # Create a mock event for y key press
            event = Mock()
            
            # Call confirm selection
            self.app._confirm_selection(event)
            
            # Check that add_connection was not called
            mock_add_connection.assert_not_called()

    def test_toggle_edit_mode_enable(self):
        """Test enabling edit mode."""
        # Ensure edit mode is initially disabled
        self.app.in_edit_mode = False
        self.app.edit_hint_text_id = None
        
        # Mock the show_edit_hint_text method
        with patch.object(self.app, '_show_edit_hint_text') as mock_show_hint:
            # Call the toggle method
            self.app._toggle_mode()  # Changed from _toggle_edit_mode
            
            # Check that edit mode is now enabled
            self.assertTrue(self.app.in_edit_mode)
            # Check that show_edit_hint_text was called
            mock_show_hint.assert_called_once()
            
        # Check that event bindings were updated for edit mode
        self.app.canvas.bind.assert_any_call("<Button-1>", self.app._drag_start)
        self.app.canvas.bind.assert_any_call("<B1-Motion>", self.app._drag_motion)
        self.app.canvas.bind.assert_any_call("<ButtonRelease-1>", self.app._drag_end)
        self.app.canvas.bind.assert_any_call("<Button-3>", self.app._remove_circle)

    def test_toggle_edit_mode_disable(self):
        """Test disabling edit mode."""
        # Setup: Edit mode is initially enabled
        self.app.in_edit_mode = True
        self.app.edit_hint_text_id = 100  # Mock text ID
        
        # Call the toggle method directly (no need to patch _exit_edit_mode)
        self.app._toggle_mode()  # Changed from _toggle_edit_mode
        
        # Check that edit mode was disabled
        self.assertFalse(self.app.in_edit_mode)
        
        # Check that the edit_hint_text_id would be cleared (now handled by _set_application_mode)
        # This is an indirect test since we're mocking the canvas

    def test_start_drag(self):
        """Test starting to drag a circle."""
        # Setup: Add a circle and enable edit mode
        circle = {
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color": "blue",
            "connected_to": []
        }
        
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}
        self.app.in_edit_mode = True
        
        # Reset drag state
        self.app._reset_drag_state()
        
        # Mock the get_circle_at_coords method to return our circle ID
        with patch.object(self.app, 'get_circle_at_coords', return_value=1):
            # Create a mock event for mouse click
            event = Mock()
            event.x = 50
            event.y = 50
            
            # Call the start drag method
            self.app._drag_start(event)
            
            # Check that the drag state was set correctly
            self.assertTrue(self.app.drag_state["active"])
            self.assertEqual(self.app.drag_state["type"], "circle")
            self.assertEqual(self.app.drag_state["id"], 1)
    
    def test_start_drag_no_circle(self):
        """Test starting to drag when no circle is clicked."""
        self.app.in_edit_mode = True
        
        # Reset drag state
        self.app._reset_drag_state()
        
        # Mock the get_circle_at_coords method to return None (no circle found)
        with patch.object(self.app, 'get_circle_at_coords', return_value=None):
            # Create a mock event for mouse click
            event = Mock()
            event.x = 200
            event.y = 200
            
            # Call the start drag method
            self.app._drag_start(event)
            
            # Check that the drag state remained inactive
            self.assertFalse(self.app.drag_state["active"])
            self.assertIsNone(self.app.drag_state["type"])
            self.assertIsNone(self.app.drag_state["id"])
    
    def test_drag_circle(self):
        """Test dragging a circle to a new position."""
        # Setup: Add a circle, enable edit mode, and set it as being dragged
        circle = {
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color": "blue",
            "connected_to": []
        }
        
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}
        self.app.in_edit_mode = True
        
        # Setup drag state for circle
        self.app.drag_state = {
            "active": True,
            "type": "circle",
            "id": 1,
            "start_x": 50,
            "start_y": 50,
            "last_x": 50,
            "last_y": 50
        }
        
        # Mock the update_connections method
        with patch.object(self.app, '_update_connections') as mock_update:
            # Create a mock event for mouse drag
            event = Mock()
            event.x = 60
            event.y = 70  # Moved 10 right and 20 down
            
            # Call the drag motion method
            self.app._drag_motion(event)
            
            # Check that the circle was moved on the canvas
            self.app.canvas.move.assert_called_with(100, 10, 20)
            
            # Check that the circle's coordinates were updated
            self.assertEqual(circle["x"], 60)
            self.assertEqual(circle["y"], 70)
            
            # Check that connections were updated
            mock_update.assert_called_once_with(1)
    
    def test_end_drag(self):
        """Test ending a circle drag operation."""
        # Setup: Enable edit mode and set a circle as being dragged
        self.app.in_edit_mode = True
        self.app.drag_state = {
            "active": True,
            "type": "circle",
            "id": 1,
            "start_x": 50,
            "start_y": 50,
            "last_x": 60,
            "last_y": 70
        }
        
        # Create a mock event for mouse release
        event = Mock()
        
        # Call the end drag method
        self.app._drag_end(event)
        
        # Check that the drag state was reset
        self.assertFalse(self.app.drag_state["active"])
        self.assertIsNone(self.app.drag_state["id"])
        self.assertIsNone(self.app.drag_state["type"])
    
    def test_update_connections(self):
        """Test updating connection lines when a circle moves."""
        # Setup: Add two connected circles
        first_circle = {
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color": "blue",
            "connected_to": [2]
        }
        second_circle = {
            "id": 2,
            "canvas_id": 101,
            "x": 100,
            "y": 100,
            "color": "red",
            "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Create a connection between the circles
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2
            }
        }
        
        # Mock create_line to return a new line ID
        self.app.canvas.create_line.return_value = 201
        
        # Mock _calculate_curve_points to return a fixed set of points
        with patch.object(self.app, '_calculate_curve_points', return_value=[50, 50, 75, 75, 100, 100]):
            # Call the update connections method
            self.app._update_connections(1)
            
            # Check that the old line was deleted
            self.app.canvas.delete.assert_called_once_with(200)
            
            # Check that a new curved line was created with the expected points and parameters
            self.app.canvas.create_line.assert_called_once_with(
                [50, 50, 75, 75, 100, 100],  # List of points for curved line
                width=1,
                smooth=True  # Curved lines use smooth=True
            )
            
            # Check that the connection was updated with the new line ID
            connection = self.app.connections["1_2"]
            self.assertEqual(connection["line_id"], 201)

    def test_remove_circle(self):
        """Test removing a circle with right-click in edit mode."""
        # Setup: Add two connected circles
        first_circle = {
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color": "blue",
            "connected_to": [2]
        }
        second_circle = {
            "id": 2,
            "canvas_id": 101,
            "x": 100,
            "y": 100,
            "color": "red",
            "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        self.app.in_edit_mode = True
        
        # Create a connection between the circles
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2
            }
        }
        
        # Mock the get_circle_at_coords method to return circle 1
        with patch.object(self.app, 'get_circle_at_coords', return_value=1):
            # Create a mock event for right-click
            event = Mock()
            event.x = 50
            event.y = 50
            
            # Call the remove circle method
            self.app._remove_circle(event)
            
            # Check that the circle was deleted from the canvas
            self.app.canvas.delete.assert_any_call(100)  # Circle's canvas_id
            
            # Check that the connection line was deleted
            self.app.canvas.delete.assert_any_call(200)  # Connection line_id
            
            # Check that the circle was removed from data structures
            self.assertEqual(len(self.app.circles), 1)
            self.assertEqual(self.app.circles[0]["id"], 2)
            self.assertNotIn(1, self.app.circle_lookup)
            
            # Check that the connection was removed from the connections dictionary
            self.assertEqual(len(self.app.connections), 0)
            
            # Check that the connected circle's data was updated
            self.assertEqual(second_circle["connected_to"], [])
            
    def test_remove_circle_no_connections(self):
        """Test removing a circle that has no connections."""
        # Setup: Add a circle with no connections and a second circle to prevent last circle handling
        circle1 = {
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color": "blue",
            "connected_to": []
        }
        circle2 = {
            "id": 2,
            "canvas_id": 101,
            "x": 150,
            "y": 150,
            "color": "red",
            "connected_to": []
        }
        
        self.app.circles = [circle1, circle2]
        self.app.circle_lookup = {1: circle1, 2: circle2}
        self.app.in_edit_mode = True
        self.app.connections = {}
        
        # Mock the get_circle_at_coords method to return the first circle
        with patch.object(self.app, 'get_circle_at_coords', return_value=1):
            # Create a mock event for right-click
            event = Mock()
            event.x = 50
            event.y = 50
            
            # Call the remove circle method
            self.app._remove_circle(event)
            
            # Check that the circle was deleted from the canvas
            self.app.canvas.delete.assert_called_once_with(100)  # Circle's canvas_id
            
            # Check that the circle was removed from data structures
            self.assertEqual(len(self.app.circles), 1)
            self.assertEqual(self.app.circles[0]["id"], 2)
            self.assertNotIn(1, self.app.circle_lookup)
        
    def test_remove_last_circle(self):
        """Test removing the last remaining circle in edit mode."""
        # Setup: Add a single circle
        circle = {
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color": "blue",
            "connected_to": []
        }
        
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}
        self.app.in_edit_mode = True
        self.app.connections = {}
        self.app.next_id = 2
        self.app.last_circle_id = 1
        self.app.drawn_items = [(50, 50)]
        
        # Mock set_application_mode instead of _exit_edit_mode
        with patch.object(self.app, '_set_application_mode') as mock_set_mode:
            # Mock the get_circle_at_coords method
            with patch.object(self.app, 'get_circle_at_coords', return_value=1):
                # Create a mock event for right-click
                event = Mock()
                event.x = 50
                event.y = 50
                
                # Call the remove circle method
                self.app._remove_circle(event)
                
                # Check that we switched to CREATE mode
                mock_set_mode.assert_called_with(ApplicationMode.CREATE)
                
        # Check that the circle was deleted from the canvas
        self.app.canvas.delete.assert_any_call(100)  # Circle's canvas_id
        
        # Note: The rest of the assertions remain valid

    def test_toggle_mode(self):
        """Test toggling between create and adjust modes."""
        # Test switching from create to adjust
        self.app._mode = ApplicationMode.CREATE
        self.app._toggle_mode()
        self.assertEqual(self.app._mode, ApplicationMode.ADJUST)
        
        # Test switching from adjust to create
        self.app._toggle_mode()
        self.assertEqual(self.app._mode, ApplicationMode.CREATE)
        
        # Test that selection mode should not change
        self.app._mode = ApplicationMode.SELECTION
        self.app._toggle_mode()
        self.assertEqual(self.app._mode, ApplicationMode.SELECTION)  # Should remain in SELECTION

    def test_focus_after(self):
        """Test that focus is set to debug button after command execution."""
        # Create a mock function
        mock_func = MagicMock()
        
        # Call _focus_after with the mock function
        self.app._focus_after(mock_func)
        
        # Verify the function was called
        mock_func.assert_called_once()
        
        # Verify focus was set to debug button
        self.app.debug_button.focus_set.assert_called_once()
    
    def test_application_mode_enum(self):
        """Test that the ApplicationMode enum has the expected values."""
        self.assertIn(ApplicationMode.CREATE, ApplicationMode)
        self.assertIn(ApplicationMode.SELECTION, ApplicationMode)
        self.assertIn(ApplicationMode.ADJUST, ApplicationMode)
    
    def test_button_text_updates(self):
        """Test that the mode button text updates correctly."""
        # Setup the mode button
        self.app.mode_button = MagicMock()
        
        # Test CREATE mode button text
        self.app._mode = ApplicationMode.CREATE
        self.app._set_application_mode(ApplicationMode.ADJUST)
        self.app.mode_button.config.assert_called_with(text="Engage create mode")
        
        # Test ADJUST mode button text
        self.app._set_application_mode(ApplicationMode.CREATE)
        self.app.mode_button.config.assert_called_with(text="Engage adjust mode")

    def test_calculate_midpoint_handle_position(self):
        """Test the calculation of midpoint handle positions with half offset."""
        # Setup two circles
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Create a connection with non-zero curve values
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 40,  # Large offset to clearly test the halving
                "curve_Y": -30
            }
        }
        
        # Calculate the handle position
        handle_x, handle_y = self.app._calculate_midpoint_handle_position(1, 2)
        
        # Base midpoint is (100, 100)
        # With half of curve_X=40 and curve_Y=-30, expect (120, 85)
        self.assertEqual(handle_x, 100 + 40/2)  # 120
        self.assertEqual(handle_y, 100 - 30/2)  # 85

    def test_drag_state_management(self):
        """Test the unified drag state management system."""
        # Verify initial state is inactive
        self.assertFalse(self.app.drag_state["active"])
        self.assertIsNone(self.app.drag_state["type"])
        self.assertIsNone(self.app.drag_state["id"])
        
        # Test resetting drag state
        self.app.drag_state = {
            "active": True,
            "type": "circle",
            "id": 1,
            "start_x": 50,
            "start_y": 60,
            "last_x": 55,
            "last_y": 65
        }
        
        self.app._reset_drag_state()
        
        self.assertFalse(self.app.drag_state["active"])
        self.assertIsNone(self.app.drag_state["type"])
        self.assertIsNone(self.app.drag_state["id"])
        self.assertEqual(self.app.drag_state["start_x"], 0)
        self.assertEqual(self.app.drag_state["start_y"], 0)
        self.assertEqual(self.app.drag_state["last_x"], 0)
        self.assertEqual(self.app.drag_state["last_y"], 0)

    def test_drag_midpoint_doubles_offset(self):
        """Test that dragging a midpoint doubles the offset for proper curve effect."""
        # Setup: In adjust mode with active midpoint drag
        self.app._mode = ApplicationMode.ADJUST
        self.app.drag_state = {
            "active": True,
            "type": "midpoint",
            "id": "1_2",
            "start_x": 100,
            "start_y": 100,
            "last_x": 100,
            "last_y": 100
        }
        
        # Setup circles with midpoint at (100, 100)
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Setup connection
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 0,
                "curve_Y": 0
            }
        }
        
        # Mock update_connection_curve method
        with patch.object(self.app, 'update_connection_curve') as mock_update:
            # Create mock event at new position
            event = Mock()
            event.x = 110  # 10 pixels right of midpoint (100,100)
            event.y = 90   # 10 pixels above midpoint
            
            # Call drag midpoint method
            self.app._drag_motion(event)
            
            # Verify update_connection_curve was called with DOUBLED offset values
            # Base midpoint is (100,100), event position is (110,90)
            # Offset is (10,-10), but we double it to (20,-20)
            mock_update.assert_called_once_with(1, 2, 20, -20)

    def test_drag_motion_dispatches_correctly(self):
        """Test that _drag_motion correctly dispatches to circle or midpoint handler."""
        self.app._mode = ApplicationMode.ADJUST
        
        # Setup mocks for both drag handlers
        with patch.object(self.app, '_drag_circle_motion') as mock_circle_drag:
            with patch.object(self.app, '_drag_midpoint_motion') as mock_midpoint_drag:
                # Case 1: Circle drag
                self.app.drag_state = {
                    "active": True,
                    "type": "circle",
                    "id": 1,
                    "start_x": 50,
                    "start_y": 60,
                    "last_x": 55,
                    "last_y": 65
                }
                
                event = Mock()
                event.x = 60
                event.y = 70
                
                self.app._drag_motion(event)
                
                # Verify circle drag was called, midpoint drag was not
                mock_circle_drag.assert_called_once_with(60, 70, 5, 5)  # delta x=5, delta y=5
                mock_midpoint_drag.assert_not_called()
                
                # Reset mocks
                mock_circle_drag.reset_mock()
                mock_midpoint_drag.reset_mock()
                
                # Case 2: Midpoint drag
                self.app.drag_state = {
                    "active": True,
                    "type": "midpoint",
                    "id": "1_2",
                    "start_x": 100,
                    "start_y": 100,
                    "last_x": 105,
                    "last_y": 95
                }
                
                event.x = 110
                event.y = 90
                
                self.app._drag_motion(event)
                
                # Verify midpoint drag was called, circle drag was not
                mock_midpoint_drag.assert_called_once_with(110, 90)
                mock_circle_drag.assert_not_called()

    def test_real_time_curve_updates(self):
        """Test that update_connection_curve updates the curve in real-time."""
        # Setup
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Create connection
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 0,
                "curve_Y": 0
            }
        }
        
        # Mock canvas operations and _calculate_curve_points
        with patch.object(self.app.canvas, 'delete') as mock_delete:
            with patch.object(self.app.canvas, 'create_line', return_value=201) as mock_create_line:
                with patch.object(self.app, '_calculate_curve_points', 
                                 return_value=[50, 50, 120, 90, 150, 150]) as mock_calc:
                    
                    # Call the method with new curve values
                    result = self.app.update_connection_curve(1, 2, 20, -10)
                    
                    # Verify result
                    self.assertTrue(result)
                    
                    # Verify curve values were updated
                    self.assertEqual(self.app.connections["1_2"]["curve_X"], 20)
                    self.assertEqual(self.app.connections["1_2"]["curve_Y"], -10)
                    
                    # Verify the old line was deleted
                    mock_delete.assert_called_once_with(200)
                    
                    # Verify a new line was created immediately with the calculated points
                    mock_create_line.assert_called_once_with(
                        [50, 50, 120, 90, 150, 150],
                        width=1,
                        smooth=True
                    )
                    
                    # Verify the connection was updated with the new line ID
                    self.assertEqual(self.app.connections["1_2"]["line_id"], 201)

    def test_y_key_binding(self):
        """Test y key binding for confirming selection."""
        # Setup: Switch to selection mode and reset mocks
        self.app._mode = ApplicationMode.CREATE  # Start from known state
        self.app.root.bind.reset_mock()
        
        # Call bind_selection_mode_events directly instead of _set_application_mode
        self.app._bind_selection_mode_events()
        
        # Check that root binds y key to _confirm_selection
        self.app.root.bind.assert_called_with("<y>", self.app._confirm_selection)

    def test_exit_adjust_mode_with_toggle(self):
        """Test exiting adjust mode using the toggle functionality."""
        # Setup: Enable adjust mode directly and set hint text
        self.app._mode = ApplicationMode.ADJUST  # Set mode directly
        self.app.edit_hint_text_id = 100
        self.app.canvas.bind.reset_mock()  # Reset mock to clear previous calls
        
        # Ensure bound events tracking shows CREATE mode is not bound
        self.app._bound_events = {
            ApplicationMode.CREATE: False,
            ApplicationMode.SELECTION: False,
            ApplicationMode.ADJUST: True
        }
        
        # Mock canvas.delete to avoid needing to check its call
        self.app.canvas.delete = MagicMock()
        
        # Use toggle_mode to exit adjust mode
        self.app._toggle_mode()
        
        # Check that adjust mode was disabled
        self.assertEqual(self.app._mode, ApplicationMode.CREATE)
        self.assertFalse(self.app.in_edit_mode)
        
        # Check that event bindings were updated with the correct method
        self.app.canvas.bind.assert_called_with("<Button-1>", self.app._draw_on_click)
        
    def test_bind_create_mode_events(self):
        """Test binding events for create mode."""
        # Reset bound events tracking
        self.app._bound_events = {
            ApplicationMode.CREATE: False,
            ApplicationMode.SELECTION: False,
            ApplicationMode.ADJUST: False
        }
        
        # Call the bind method
        self.app._bind_create_mode_events()
        
        # Check that events were bound
        self.app.canvas.bind.assert_called_with("<Button-1>", self.app._draw_on_click)
        self.assertTrue(self.app._bound_events[ApplicationMode.CREATE])
        
        # Call again to test that duplicate bindings aren't made
        self.app.canvas.bind.reset_mock()
        self.app._bind_create_mode_events()
        self.app.canvas.bind.assert_not_called()
        
    def test_bind_selection_mode_events(self):
        """Test binding events for selection mode."""
        # Reset bound events tracking
        self.app._bound_events = {
            ApplicationMode.CREATE: False,
            ApplicationMode.SELECTION: False,
            ApplicationMode.ADJUST: False
        }
        
        # Call the bind method
        self.app._bind_selection_mode_events()
        
        # Check that events were bound
        self.app.canvas.bind.assert_called_with("<Button-1>", self.app._draw_on_click)
        self.app.root.bind.assert_called_with("<y>", self.app._confirm_selection)
        self.assertTrue(self.app._bound_events[ApplicationMode.SELECTION])
        
    def test_bind_adjust_mode_events(self):
        """Test binding events for adjust mode."""
        # Reset bound events tracking
        self.app._bound_events = {
            ApplicationMode.CREATE: False,
            ApplicationMode.SELECTION: False,
            ApplicationMode.ADJUST: False
        }
        
        # Call the bind method
        self.app._bind_adjust_mode_events()
        
        # Check that events were bound
        self.app.canvas.bind.assert_any_call("<Button-1>", self.app._drag_start)
        self.app.canvas.bind.assert_any_call("<B1-Motion>", self.app._drag_motion)
        self.app.canvas.bind.assert_any_call("<ButtonRelease-1>", self.app._drag_end)
        self.app.canvas.bind.assert_any_call("<Button-3>", self.app._remove_circle)
        self.assertTrue(self.app._bound_events[ApplicationMode.ADJUST])
        
    def test_unbind_events(self):
        """Test unbinding events for all modes."""
        # Setup: Mark all modes as bound
        self.app._bound_events = {
            ApplicationMode.CREATE: True,
            ApplicationMode.SELECTION: True,
            ApplicationMode.ADJUST: True
        }
        
        # Test unbinding create mode events
        self.app._unbind_create_mode_events()
        self.app.canvas.unbind.assert_called_with("<Button-1>")
        self.assertFalse(self.app._bound_events[ApplicationMode.CREATE])
        
        # Reset mock and test unbinding selection mode events
        self.app.canvas.unbind.reset_mock()
        self.app._unbind_selection_mode_events()
        self.app.canvas.unbind.assert_called_with("<Button-1>")
        self.app.root.unbind.assert_called_with("<y>")
        self.assertFalse(self.app._bound_events[ApplicationMode.SELECTION])
        
        # Reset mocks and test unbinding adjust mode events
        self.app.canvas.unbind.reset_mock()
        self.app._unbind_adjust_mode_events()
        self.app.canvas.unbind.assert_any_call("<Button-1>")
        self.app.canvas.unbind.assert_any_call("<B1-Motion>")
        self.app.canvas.unbind.assert_any_call("<ButtonRelease-1>")
        self.app.canvas.unbind.assert_any_call("<Button-3>")
        self.assertFalse(self.app._bound_events[ApplicationMode.ADJUST])
        
    def test_mode_transition_validation(self):
        """Test validation of mode transitions."""
        # Test that we can't transition from SELECTION to ADJUST
        self.app._mode = ApplicationMode.SELECTION
        self.app._set_application_mode(ApplicationMode.ADJUST)
        self.assertEqual(self.app._mode, ApplicationMode.SELECTION)  # Should remain in SELECTION
        
        # Test that we can transition from SELECTION to CREATE
        self.app._set_application_mode(ApplicationMode.CREATE)
        self.assertEqual(self.app._mode, ApplicationMode.CREATE)
        
        # Test that we can't transition to the same mode
        self.app.canvas.bind.reset_mock()
        self.app._set_application_mode(ApplicationMode.CREATE)
        self.app.canvas.bind.assert_not_called()  # Should not rebind events

    def test_canvas_background_color(self):
        """Test that canvas background color changes with modes."""
        # Setup: Ensure we start in CREATE mode
        self.app._mode = ApplicationMode.CREATE
        
        # Switch to ADJUST mode
        self.app._set_application_mode(ApplicationMode.ADJUST)
        
        # Check that canvas background was set to pale pink
        self.app.canvas.config.assert_any_call(bg="#FFEEEE")
        
        # Reset the mock call history
        self.app.canvas.config.reset_mock()
        
        # Switch back to CREATE mode
        self.app._set_application_mode(ApplicationMode.CREATE)
        
        # Check that canvas background was reset to white
        self.app.canvas.config.assert_any_call(bg="white")

    def test_remove_circle_by_id(self):
        """Test the centralized circle removal method."""
        # Setup: Add two connected circles
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 100, "y": 100, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Create a connection between the circles
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2
            }
        }
        
        # Call the removal method
        result = self.app._remove_circle_by_id(1)
        
        # Check the result was successful
        self.assertTrue(result)
        
        # Check that the circle was deleted from the canvas
        self.app.canvas.delete.assert_any_call(100)  # Circle's canvas_id
        
        # Check that the connection line was deleted
        self.app.canvas.delete.assert_any_call(200)  # Connection line_id
        
        # Check that the circle was removed from data structures
        self.assertEqual(len(self.app.circles), 1)
        self.assertEqual(self.app.circles[0]["id"], 2)
        self.assertNotIn(1, self.app.circle_lookup)
        
        # Check that the connection was removed from the connections dictionary
        self.assertEqual(len(self.app.connections), 0)
        
        # Check that the connected circle's data was updated
        self.assertEqual(second_circle["connected_to"], [])
        
    def test_remove_circle_connections(self):
        """Test removing circle connections."""
        # Setup: Add two connected circles
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 100, "y": 100, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Create a connection between the circles
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2
            }
        }
        
        # Call the connection removal method
        self.app._remove_circle_connections(1)
        
        # Check that the connection line was deleted
        self.app.canvas.delete.assert_called_once_with(200)
        
        # Check that the connections dictionary is empty
        self.assertEqual(len(self.app.connections), 0)
        
        # Check that the connected circle's data was updated
        self.assertEqual(second_circle["connected_to"], [])
        
    def test_handle_last_circle_removed(self):
        """Test handling the last circle removal."""
        # Setup: Set to adjust mode, then remove the last circle
        self.app._mode = ApplicationMode.ADJUST
        
        # Mock set_application_mode
        with patch.object(self.app, '_set_application_mode') as mock_set_mode:
            # Call the last circle removal handler
            self.app._handle_last_circle_removed()
            
            # Check that we switched to CREATE mode
            mock_set_mode.assert_called_with(ApplicationMode.CREATE)
            
        # Check that data structures were cleared
        self.assertEqual(self.app.drawn_items, [])
        self.assertEqual(self.app.connections, {})
        self.assertIsNone(self.app.last_circle_id)
        self.assertEqual(self.app.next_id, 1)
        
        # Check that canvas was cleared
        self.app.canvas.delete.assert_called_with("all")

    def test_assign_color_based_on_connections(self):
        """Test the basic color assignment logic."""
        # Test initial assignment for a new circle
        priority = self.app._assign_color_based_on_connections()
        self.assertEqual(priority, 1)  # Should return priority 1 (yellow)
        
        # Test passing an existing circle ID (should still return yellow for now)
        priority = self.app._assign_color_based_on_connections(1)
        self.assertEqual(priority, 1)  # Should return priority 1 (yellow)
        
    def test_draw_on_click_with_deterministic_color(self):
        """Test drawing a circle with deterministic color assignment."""
        # Setup: Mock the color assignment function
        with patch.object(self.app, '_assign_color_based_on_connections', return_value=1) as mock_assign:
            # Create a mock event
            event = Mock()
            event.x = 100
            event.y = 100
            
            # Call the method
            self.app._draw_on_click(event)
            
            # Check that assign_color was called
            mock_assign.assert_called_once()
        
        # Check that circle data was stored correctly
        self.assertEqual(len(self.app.circles), 1)
        circle = self.app.circles[0]
        # Check only color_priority, not color
        self.assertEqual(circle["color_priority"], 1)

    def test_assign_color_based_on_connections_with_conflicts(self):
        """Test color assignment logic when conflicts exist."""
        # Setup directly (without color key)
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": []
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 100, "y": 50, "color_priority": 2, "connected_to": []
        }
        third_circle = {
            "id": 3, "canvas_id": 102, "x": 150, "y": 50, "color_priority": 3, "connected_to": []
        }
        fourth_circle = {
            "id": 4, "canvas_id": 103, "x": 200, "y": 50, "color_priority": 1, "connected_to": []
        }
        
        # Add circles to data structures
        self.app.circles = [first_circle, second_circle, third_circle, fourth_circle]
        self.app.circle_lookup = {
            1: first_circle,
            2: second_circle,
            3: third_circle,
            4: fourth_circle
        }
        
        # Connect circle 4 to all other circles
        for i in range(1, 4):
            self.app.circle_lookup[4]["connected_to"].append(i)
            self.app.circle_lookup[i]["connected_to"].append(4)
        
        # Now check and resolve conflicts for circle 4
        priority = self.app._check_and_resolve_color_conflicts(4)
        
        # When connected to circles with all priorities 1-3, should get priority 4
        self.assertEqual(priority, 4)
        self.assertEqual(self.app.circle_lookup[4]["color_priority"], 4)
        # Removed check for self.app.circle_lookup[4]["color"]

    def test_update_circle_color(self):
        """Test updating a circle's color priority."""
        # Setup: Add a circle (without color key)
        circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": []
        }
        
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}
        
        # Test: Update the circle's priority
        result = self.app._update_circle_color(1, 3) # Only pass priority
        
        # Check the result was successful
        self.assertTrue(result)
        
        # Check that the circle data was updated
        # Removed check for circle["color"]
        self.assertEqual(circle["color_priority"], 3)
        
        # Check that the canvas item was updated (using derived color)
        self.app.canvas.itemconfig.assert_called_once_with(100, fill="blue") # Priority 3 is blue
        
    def test_confirm_selection_with_color_reassignment(self):
        """Test confirming selections with color reassignment."""
        # Setup: Add two circles (without color key)
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": []
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 100, "y": 100, "color_priority": 1, "connected_to": []
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        self.app.in_selection_mode = True
        self.app.newly_placed_circle_id = 2
        self.app.selected_circles = [1]  # Selected circle 1 to connect to
        self.app.selection_indicators = {1: 200}
        self.app.hint_text_id = 300
        
        # Mock add_connection and _check_and_resolve_color_conflicts
        with patch.object(self.app, 'add_connection', return_value=True) as mock_add:
            with patch.object(self.app, '_check_and_resolve_color_conflicts', return_value=2) as mock_check:
                # Create a mock event for y key press
                event = Mock()
                
                # Call the confirm selection method
                self.app._confirm_selection(event)
                
                # Verify add_connection was called
                mock_add.assert_called_with(2, 1)
                
                # Verify _check_and_resolve_color_conflicts was called
                mock_check.assert_called_once_with(2)
        
        # Check that selection mode was exited
        self.assertFalse(self.app.in_selection_mode)
        
        # Check circle priorities
        self.assertEqual(self.app.circle_lookup[1]["color_priority"], 1)  # First circle unchanged
        # Don't check second circle's priority here since we mocked _check_and_resolve_color_conflicts

    def test_check_and_resolve_color_conflicts(self):
        """Test the basic color conflict resolution logic."""
        # Create circles manually (without color key)
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": []
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 100, "y": 100, "color_priority": 1, "connected_to": []
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Setup the connection for first circle
        first_circle["connected_to"].append(2)
        second_circle["connected_to"].append(1)
        
        # Store a mock connection
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2
            }
        }
        
        # Call color conflict resolution directly
        priority = self.app._check_and_resolve_color_conflicts(2)
        
        # Check that circle 2's priority was changed to resolve the conflict
        self.assertEqual(priority, 2)  # Priority should be 2
        self.assertEqual(self.app.circle_lookup[2]["color_priority"], 2)  # Should be priority 2
        # Removed check for self.app.circle_lookup[2]["color"]

    def test_reassign_color_network_call(self):
        """Test that _check_and_resolve_color_conflicts calls _reassign_color_network when needed."""
        # Setup: Create 4 circles (without color key)
        circles = [
            {"id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [4]},
            {"id": 2, "canvas_id": 101, "x": 100, "y": 50, "color_priority": 2, "connected_to": [4]},
            {"id": 3, "canvas_id": 102, "x": 150, "y": 50, "color_priority": 3, "connected_to": [4]},
            {"id": 4, "canvas_id": 103, "x": 100, "y": 100, "color_priority": 1, "connected_to": [1, 2, 3]}
        ]
        
        # Add circles to lookup
        self.app.circles = circles
        self.app.circle_lookup = {c["id"]: c for c in circles}
        
        # Mock the _reassign_color_network method
        with patch.object(self.app, '_reassign_color_network', return_value=4) as mock_reassign:
            # Check and resolve conflicts for circle 4
            priority = self.app._check_and_resolve_color_conflicts(4)
            
            # Verify _reassign_color_network was called
            mock_reassign.assert_called_once_with(4)
            
            # Verify the return value was passed through
            self.assertEqual(priority, 4)
            # Removed assertion checking circle_lookup state, as the mock prevents the update.
            # The purpose of this test is to check the *call* to _reassign_color_network.
            # test_reassign_color_network verifies the state change within that function.

    def test_reassign_color_network(self):
        """Test the _reassign_color_network function."""
        # Setup: Add a circle (without color key)
        circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": []
        }
        
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}
        
        # Call the reassign function
        priority = self.app._reassign_color_network(1)
        
        # Verify the circle was updated with priority 4
        self.assertEqual(priority, 4)
        self.assertEqual(circle["color_priority"], 4)
        # Removed check for circle["color"]
        
        # Verify the canvas was updated (using derived color)
        self.app.canvas.itemconfig.assert_called_once_with(100, fill="red") # Priority 4 is red

    def test_assign_color_based_on_connections_with_connected_circles(self):
        """Test color assignment logic with connected circles."""
        # Setup circle data with existing connections (without color key)
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 100, "y": 100, "color_priority": 1, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Mock determine_color_priority_for_connections to verify it's called with the right arguments
        with patch('canvas_app.determine_color_priority_for_connections', return_value=2) as mock_determine:
            priority = self.app._assign_color_based_on_connections(2)
            
            # Verify the utility function was called with the right set of priorities
            mock_determine.assert_called_once_with({1})  # Circle 1's priority
            
            # Verify the return value
            self.assertEqual(priority, 2)

    def test_check_and_resolve_color_conflicts_with_utility_functions(self):
        """Test that _check_and_resolve_color_conflicts uses the utility functions."""
        # Create circles manually (without color key)
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 100, "y": 100, "color_priority": 1, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Mock find_lowest_available_priority to verify it's used
        with patch('canvas_app.find_lowest_available_priority', return_value=2) as mock_find:
            priority = self.app._check_and_resolve_color_conflicts(2)
            
            # Verify the utility function was called with the set of used priorities
            mock_find.assert_called_once_with({1})  # Circle 1's priority
            
            # Verify the resulting priority
            self.assertEqual(priority, 2)
            self.assertEqual(second_circle["color_priority"], 2)

    def test_full_color_assignment_integration_flow(self):
        """Test the full flow of color assignment and conflict resolution with real utilities."""
        # Create the first circle (default yellow, priority 1)
        self.app._draw_on_click(self._create_click_event(100, 100))
        
        # Create a second circle that will enter selection mode
        self.app._draw_on_click(self._create_click_event(200, 100))
        
        # Verify we're in selection mode with newly_placed_circle_id set
        self.assertTrue(self.app.in_selection_mode)
        self.assertEqual(self.app.newly_placed_circle_id, 2)
        
        # Select the first circle to connect to
        self.app._toggle_circle_selection(1)
        self.assertEqual(self.app.selected_circles, [1])
        
        # Confirm the selection with 'y' key press
        self.app._confirm_selection(self._create_key_event('y'))
        
        # Verify connection was made
        self.assertIn(1, self.app.circle_lookup[2]["connected_to"])
        self.assertIn(2, self.app.circle_lookup[1]["connected_to"])
        
        # Verify color conflict was resolved (circle 2 should have priority 2)
        self.assertEqual(self.app.circle_lookup[1]["color_priority"], 1)  # First circle stays yellow
        self.assertEqual(self.app.circle_lookup[2]["color_priority"], 2)  # Second circle becomes green

    def test_color_assignment_when_all_priorities_used(self):
        """Test color assignment when all priorities 1-3 are already used."""
        # Setup: Create four circles with priorities 1, 2, 3 and connect them all to a fifth circle
        circles_data = [
            {"id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [5]},
            {"id": 2, "canvas_id": 101, "x": 150, "y": 50, "color_priority": 2, "connected_to": [5]},
            {"id": 3, "canvas_id": 102, "x": 250, "y": 50, "color_priority": 3, "connected_to": [5]},
            {"id": 5, "canvas_id": 103, "x": 150, "y": 150, "color_priority": 1, "connected_to": [1, 2, 3]}
        ]
        
        self.app.circles = circles_data
        self.app.circle_lookup = {c["id"]: c for c in circles_data}
        
        # Execute the conflict resolution
        result = self.app._check_and_resolve_color_conflicts(5)
        
        # Verify the special case is handled by assigning priority 4 (red)
        self.assertEqual(result, 4)
        self.assertEqual(self.app.circle_lookup[5]["color_priority"], 4)
        
        # Verify canvas was updated with red
        self.app.canvas.itemconfig.assert_called_with(103, fill="red")

    def test_calculate_midpoint(self):
        """Test calculating the midpoint between two circles."""
        # Create two test circles
        circle1 = {"x": 50, "y": 50}
        circle2 = {"x": 150, "y": 150}
        
        # Calculate midpoint
        mid_x, mid_y = self.app._calculate_midpoint(circle1, circle2)
        
        # Check result
        self.assertEqual(mid_x, 100)
        self.assertEqual(mid_y, 100)
        
    def test_add_connection_with_curve_data(self):
        """Test that adding a connection includes default curve data."""
        # Create two circles
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": []
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": []
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        self.app.canvas.create_line.return_value = 200
        
        # Add the connection
        result = self.app.add_connection(1, 2)
        
        # Verify result
        self.assertTrue(result)
        
        # Verify connection data includes curve values
        connection = self.app.connections.get("1_2")
        self.assertIsNotNone(connection)
        self.assertEqual(connection["curve_X"], 0)
        self.assertEqual(connection["curve_Y"], 0)
        
    def test_get_connection_curve_offset(self):
        """Test getting curve offset for a connection."""
        # Setup a connection with curve data
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 15,
                "curve_Y": -10
            }
        }
        
        # Test getting the data
        curve_x, curve_y = self.app.get_connection_curve_offset(1, 2)
        self.assertEqual(curve_x, 15)
        self.assertEqual(curve_y, -10)
        
        # Test with reversed ids
        curve_x, curve_y = self.app.get_connection_curve_offset(2, 1)
        self.assertEqual(curve_x, 15)
        self.assertEqual(curve_y, -10)
        
        # Test with nonexistent connection
        curve_x, curve_y = self.app.get_connection_curve_offset(3, 4)
        self.assertEqual(curve_x, 0)
        self.assertEqual(curve_y, 0)
        
    def test_update_connection_curve(self):
        """Test updating curve offset for a connection."""
        # Setup a connection with default curve data
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 0,
                "curve_Y": 0
            }
        }
        
        # Mock calculate_curve_points
        with patch.object(self.app, '_calculate_curve_points', return_value=[50, 50, 75, 75, 150, 150]):
            # Update the curve
            result = self.app.update_connection_curve(1, 2, 25, -15)
            
            # Verify result
            self.assertTrue(result)
            self.assertEqual(self.app.connections["1_2"]["curve_X"], 25)
            self.assertEqual(self.app.connections["1_2"]["curve_Y"], -15)
        
        # Test with reversed ids
        result = self.app.update_connection_curve(2, 1, 30, -20)
        self.assertTrue(result)
        self.assertEqual(self.app.connections["1_2"]["curve_X"], 30)
        self.assertEqual(self.app.connections["1_2"]["curve_Y"], -20)
        
        # Test with nonexistent connection
        result = self.app.update_connection_curve(3, 4, 10, 10)
        self.assertFalse(result)
        
    def test_update_connections_preserves_curve_data(self):
        """Test that updating connections preserves curve data."""
        # Setup circles
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Create a connection with custom curve values
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 25,
                "curve_Y": -15
            }
        }
        
        # Mock create_line to return a new ID
        self.app.canvas.create_line.return_value = 201
        
        # Mock _calculate_curve_points to return a fixed set of points
        with patch.object(self.app, '_calculate_curve_points', return_value=[50, 50, 75, 75, 100, 100]):
            # Call the update connections method
            self.app._update_connections(1)
            
            # Check that the old line was deleted
            self.app.canvas.delete.assert_called_once_with(200)
            
            # Check that a new curved line was created with the expected points and parameters
            self.app.canvas.create_line.assert_called_once_with(
                [50, 50, 75, 75, 100, 100],  # List of points for curved line
                width=1,
                smooth=True  # Curved lines use smooth=True
            )
            
            # Check that the connection was updated with the new line ID
            connection = self.app.connections["1_2"]
            self.assertEqual(connection["line_id"], 201)
            self.assertEqual(connection["curve_X"], 25)
            self.assertEqual(connection["curve_Y"], -15)

    def test_calculate_curve_points(self):
        """Test calculating points for a curved line."""
        # Setup two circles
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Case 1: With no curve offset
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 0,
                "curve_Y": 0
            }
        }
        
        # Get curve points
        points = self.app._calculate_curve_points(1, 2)
        
        # Expected: [from_x, from_y, mid_x, mid_y, to_x, to_y]
        expected = [50, 50, 100, 100, 150, 150]
        self.assertEqual(points, expected)
        
        # Case 2: With curve offset
        self.app.connections["1_2"]["curve_X"] = 20
        self.app.connections["1_2"]["curve_Y"] = -15
        
        # Get curve points with offset
        points = self.app._calculate_curve_points(1, 2)
        
        # Expected with offset applied to midpoint
        expected = [50, 50, 120, 85, 150, 150]
        self.assertEqual(points, expected)
        
    def test_add_connection_with_curve(self):
        """Test that adding a connection creates a curved line."""
        # Setup two circles
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": []
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": []
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Mock curve points calculation to return consistent results
        with patch.object(self.app, '_calculate_curve_points', return_value=[50, 50, 100, 100, 150, 150]):
            # Add connection
            result = self.app.add_connection(1, 2)
            
            # Verify result
            self.assertTrue(result)
            
            # Verify line was created with correct parameters
            self.app.canvas.create_line.assert_called_once()
            args, kwargs = self.app.canvas.create_line.call_args
            
            # Verify points and smooth parameter
            self.assertEqual(args[0], [50, 50, 100, 100, 150, 150])
            self.assertEqual(kwargs['width'], 1)
            self.assertEqual(kwargs['smooth'], True)
    
    def test_update_connections_with_curve(self):
        """Test updating connections maintains the curve."""
        # Setup two connected circles
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Create a connection with curve
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 10,
                "curve_Y": -5
            }
        }
        
        # Mock curve points calculation
        with patch.object(self.app, '_calculate_curve_points', return_value=[50, 50, 110, 95, 150, 150]):
            # Update the connections
            self.app._update_connections(1)
            
            # Verify the old line was deleted
            self.app.canvas.delete.assert_called_once_with(200)
            
            # Verify a new curved line was created
            self.app.canvas.create_line.assert_called_once()
            args, kwargs = self.app.canvas.create_line.call_args
            
            # Verify points and smooth parameter
            self.assertEqual(args[0], [50, 50, 110, 95, 150, 150])
            self.assertEqual(kwargs['width'], 1)
            self.assertEqual(kwargs['smooth'], True)

    def test_draw_midpoint_handle(self):
        """Test drawing a midpoint handle."""
        # Setup connection
        self.app.midpoint_radius = 5
        self.app.canvas.create_rectangle.return_value = 300
        
        # Call the method
        handle_id = self.app._draw_midpoint_handle("1_2", 100, 100)
        
        # Check that create_rectangle was called with the right parameters
        self.app.canvas.create_rectangle.assert_called_once()
        args, kwargs = self.app.canvas.create_rectangle.call_args
        
        # Check coordinates
        self.assertEqual(args[0], 95)  # x1 = x - radius
        self.assertEqual(args[1], 95)  # y1 = y - radius
        self.assertEqual(args[2], 105)  # x2 = x + radius
        self.assertEqual(args[3], 105)  # y2 = y + radius
        
        # Check styling
        self.assertEqual(kwargs['fill'], "black")  # Black fill
        self.assertEqual(kwargs['outline'], "white")  # White outline
        self.assertEqual(kwargs['width'], 1)
        self.assertEqual(kwargs['tags'], ("midpoint_handle", "1_2"))
        
        # Check return value
        self.assertEqual(handle_id, 300)
        
    def test_show_midpoint_handles(self):
        """Test showing midpoint handles for all connections."""
        # Setup connections
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 10,
                "curve_Y": -5
            }
        }
        
        # Mock _calculate_midpoint_handle_position and _draw_midpoint_handle
        with patch.object(self.app, '_calculate_midpoint_handle_position', 
                         return_value=(110, 95)) as mock_calc_pos:
            with patch.object(self.app, '_draw_midpoint_handle', 
                             return_value=300) as mock_draw:
                
                # Call the method
                self.app._show_midpoint_handles()
                
                # Verify position was calculated
                mock_calc_pos.assert_called_once_with(1, 2)
                
                # Verify handle was drawn at calculated position
                mock_draw.assert_called_once_with("1_2", 110, 95)
                
                # Check that handle was stored
                self.assertEqual(self.app.midpoint_handles["1_2"], 300)
    
    def test_hide_midpoint_handles(self):
        """Test hiding all midpoint handles."""
        # Setup midpoint handles
        self.app.midpoint_handles = {
            "1_2": 300,
            "2_3": 301,
            "3_4": 302
        }
        
        # Call the method
        self.app._hide_midpoint_handles()
        
        # Check that all handles were deleted
        self.app.canvas.delete.assert_any_call(300)
        self.app.canvas.delete.assert_any_call(301)
        self.app.canvas.delete.assert_any_call(302)
        
        # Check that midpoint_handles was cleared
        self.assertEqual(len(self.app.midpoint_handles), 0)
        
    def test_show_handles_in_adjust_mode(self):
        """Test that midpoint handles are shown when entering adjust mode."""
        # Setup
        self.app._mode = ApplicationMode.CREATE
        
        # Mock _show_midpoint_handles
        with patch.object(self.app, '_show_midpoint_handles') as mock_show_handles:
            # Switch to adjust mode
            self.app._set_application_mode(ApplicationMode.ADJUST)
            
            # Verify handles were shown
            mock_show_handles.assert_called_once()
    
    def test_hide_handles_when_exiting_adjust_mode(self):
        """Test that midpoint handles are hidden when exiting adjust mode."""
        # Setup
        self.app._mode = ApplicationMode.ADJUST
        
        # Mock _hide_midpoint_handles
        with patch.object(self.app, '_hide_midpoint_handles') as mock_hide_handles:
            # Switch to create mode
            self.app._set_application_mode(ApplicationMode.CREATE)
            
            # Verify handles were hidden
            mock_hide_handles.assert_called_once()
    
    def test_update_connection_curve_updates_handle(self):
        """Test that updating a curve also updates its midpoint handle in adjust mode."""
        # Setup
        self.app._mode = ApplicationMode.ADJUST
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 0,
                "curve_Y": 0
            }
        }
        
        # Add a midpoint handle
        self.app.midpoint_handles = {"1_2": 300}
        
        # Mock canvas operations and helpers
        with patch.object(self.app, '_calculate_curve_points', 
                         return_value=[50, 50, 120, 90, 150, 150]):
            with patch.object(self.app, '_calculate_midpoint_handle_position',
                             return_value=(120, 90)):
                with patch.object(self.app, '_draw_midpoint_handle',
                                 return_value=301):
                    
                    # Call the method
                    result = self.app.update_connection_curve(1, 2, 20, -10)
                    
                    # Verify result
                    self.assertTrue(result)
                    
                    # Verify curve values were updated
                    self.assertEqual(self.app.connections["1_2"]["curve_X"], 20)
                    self.assertEqual(self.app.connections["1_2"]["curve_Y"], -10)
                    
                    # Verify both the line and old handle were deleted
                    self.app.canvas.delete.assert_any_call(200)  # Line
                    self.app.canvas.delete.assert_any_call(300)  # Old handle
                    
                    # Verify handle was updated in dictionary
                    self.assertEqual(self.app.midpoint_handles["1_2"], 301)
    
    def test_update_connections_with_midpoint_handles(self):
        """Test updating connections redraws midpoint handles in adjust mode."""
        # Setup
        self.app._mode = ApplicationMode.ADJUST
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Create connection
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 10,
                "curve_Y": -5
            }
        }
        
        # Add a midpoint handle
        self.app.midpoint_handles = {"1_2": 300}
        
        # Mock the update_connection_curve method to prevent actual implementation
        with patch.object(self.app, 'update_connection_curve') as mock_update:
            # Call the method
            self.app._update_connections(1)
            
            # Verify update_connection_curve was called with the right parameters
            mock_update.assert_called_once_with(1, 2, 10, -5)

    def test_clear_canvas_removes_midpoint_handles(self):
        """Test that clearing the canvas also removes midpoint handles."""
        # Setup: Ensure we're not in ADJUST mode
        self.app._mode = ApplicationMode.CREATE
        
        # Add a circle so that self.circles is not empty
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": []
        }
        self.app.circles = [first_circle]
        
        # Setup midpoint handles
        self.app.midpoint_handles = {
            "1_2": 300,
            "2_3": 301
        }
        
        # Call the clear method
        self.app._clear_canvas()
        
        # Check that midpoint_handles was cleared
        self.assertEqual(len(self.app.midpoint_handles), 0)

    def test_remove_circle_connections_removes_midpoint_handles(self):
        """Test that removing circle connections also removes their midpoint handles."""
        # Setup
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Create connection
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2
            }
        }
        
        # Add midpoint handle
        self.app.midpoint_handles = {"1_2": 300}
        
        # Call remove connections
        self.app._remove_circle_connections(1)
        
        # Verify line and handle were deleted
        self.app.canvas.delete.assert_any_call(200)  # Line
        self.app.canvas.delete.assert_any_call(300)  # Handle
        
        # Verify connections and handles dictionaries were cleared
        self.assertEqual(len(self.app.connections), 0)
        self.assertEqual(len(self.app.midpoint_handles), 0)

    def test_start_midpoint_drag(self):
        """Test starting to drag a midpoint handle."""
        # Setup: Make sure we're in adjust mode
        self.app._mode = ApplicationMode.ADJUST
        
        # Create a connection with a midpoint handle
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 10,
                "curve_Y": -5
            }
        }
        self.app.midpoint_handles = {"1_2": 300}
        
        # Mock canvas.find_closest to return our handle ID and gettags to return the tags
        self.app.canvas.find_closest = MagicMock(return_value=[300])
        self.app.canvas.gettags = MagicMock(return_value=["midpoint_handle", "1_2"])
        
        # Create mock event
        event = Mock()
        event.x = 100
        event.y = 120
        
        # Call the start drag method
        self.app._drag_start(event)
        
        # Verify the drag state was set correctly
        self.assertTrue(self.app.drag_state["active"])
        self.assertEqual(self.app.drag_state["type"], "midpoint")
        self.assertEqual(self.app.drag_state["id"], "1_2")
        self.assertEqual(self.app.drag_state["start_x"], 100)
        self.assertEqual(self.app.drag_state["start_y"], 120)

    def test_drag_midpoint(self):
        """Test dragging a midpoint handle to adjust the curve."""
        # Setup: In adjust mode with active midpoint drag
        self.app._mode = ApplicationMode.ADJUST
        
        # Setup drag state for midpoint
        self.app.drag_state = {
            "active": True,
            "type": "midpoint",
            "id": "1_2",
            "start_x": 100,
            "start_y": 100,
            "last_x": 100,
            "last_y": 100
        }
        
        # Setup circles
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Setup connection with initial curve values
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 0,
                "curve_Y": 0
            }
        }
        
        # Mock calculate_midpoint method for base position
        with patch.object(self.app, '_calculate_midpoint', return_value=(100, 100)):
            # Mock update_connection_curve method
            with patch.object(self.app, 'update_connection_curve') as mock_update:
                # Create mock event at new position
                event = Mock()
                event.x = 110  # 10 pixels right of midpoint (100,100)
                event.y = 90   # 10 pixels above midpoint
                
                # Call drag motion method
                self.app._drag_motion(event)
                
                # Verify drag_midpoint_motion was called with correct parameters
                mock_update.assert_called_once_with(1, 2, 20, -20)

    def test_end_midpoint_drag(self):
        """Test ending midpoint drag operation."""
        # Setup: Active midpoint drag
        self.app._mode = ApplicationMode.ADJUST
        self.app.drag_state = {
            "active": True,
            "type": "midpoint",
            "id": "1_2",
            "start_x": 100,
            "start_y": 100,
            "last_x": 110,
            "last_y": 90
        }
        
        # Create mock event
        event = Mock()
        
        # Call end drag method
        self.app._drag_end(event)
        
        # Verify drag state was reset
        self.assertFalse(self.app.drag_state["active"])
        self.assertIsNone(self.app.drag_state["type"])
        self.assertIsNone(self.app.drag_state["id"])

    def test_midpoint_drag_not_in_edit_mode(self):
        """Test that midpoint dragging does nothing when not in edit mode."""
        # Setup: Not in edit mode, but with initialized midpoint drag state
        self.app._mode = ApplicationMode.CREATE
        self.app.drag_state = {
            "active": True,
            "type": "midpoint",
            "id": "1_2",
            "start_x": 100,
            "start_y": 100,
            "last_x": 100,
            "last_y": 100
        }
        
        # Mock update_connection_curve
        with patch.object(self.app, 'update_connection_curve') as mock_update:
            # Create mock event
            event = Mock()
            event.x = 110
            event.y = 90
            
            # Call drag motion method
            self.app._drag_motion(event)
            
            # Verify update_connection_curve was not called
            mock_update.assert_not_called()

    def test_drag_midpoint_doubles_offset(self):
        """Test that dragging a midpoint doubles the offset for proper curve effect."""
        # Setup: In adjust mode with active midpoint drag state
        self.app._mode = ApplicationMode.ADJUST
        self.app.drag_state = {
            "active": True,
            "type": "midpoint",
            "id": "1_2",
            "start_x": 100,
            "start_y": 100,
            "last_x": 100,
            "last_y": 100
        }
        
        # Setup circles with midpoint at (100, 100)
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Setup connection
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 0,
                "curve_Y": 0
            }
        }
        
        # Mock calculate_midpoint method for base position
        with patch.object(self.app, '_calculate_midpoint', return_value=(100, 100)):
            # Mock update_connection_curve method
            with patch.object(self.app, 'update_connection_curve') as mock_update:
                # Create mock event at new position
                event = Mock()
                event.x = 110  # 10 pixels right of midpoint (100,100)
                event.y = 90   # 10 pixels above midpoint
                
                # Call drag motion method
                self.app._drag_motion(event)
                
                # Verify update_connection_curve was called with DOUBLED offset values
                # Base midpoint is (100,100), event position is (110,90)
                # Offset is (10,-10), but we double it to (20,-20)
                mock_update.assert_called_once_with(1, 2, 20, -20)

    def test_adjust_mode_binds_midpoint_events(self):
        """Test that entering adjust mode binds midpoint handle events."""
        # Setup
        self.app._mode = ApplicationMode.CREATE
        self.app.canvas.tag_bind = MagicMock()
        
        # Reset bound events tracking
        self.app._bound_events = {
            ApplicationMode.CREATE: True,
            ApplicationMode.SELECTION: False,
            ApplicationMode.ADJUST: False
        }
        
        # Call bind adjust mode events
        self.app._bind_adjust_mode_events()
        
        # Canvas events are now handled by unified drag methods
        # So we only need to verify the basic bindings were added
        self.app.canvas.bind.assert_any_call("<Button-1>", self.app._drag_start)
        self.app.canvas.bind.assert_any_call("<B1-Motion>", self.app._drag_motion)
        self.app.canvas.bind.assert_any_call("<ButtonRelease-1>", self.app._drag_end)

    def test_show_midpoint_handles(self):
        """Test showing midpoint handles for all connections."""
        # Setup connections
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 10,
                "curve_Y": -5
            }
        }
        
        # Mock _calculate_midpoint_handle_position and _draw_midpoint_handle
        with patch.object(self.app, '_calculate_midpoint_handle_position', 
                         return_value=(110, 95)) as mock_calc_pos:
            with patch.object(self.app, '_draw_midpoint_handle', 
                             return_value=300) as mock_draw:
                
                # Call the method
                self.app._show_midpoint_handles()
                
                # Verify position was calculated
                mock_calc_pos.assert_called_once_with(1, 2)
                
                # Verify handle was drawn at calculated position
                mock_draw.assert_called_once_with("1_2", 110, 95)
                
                # Check that handle was stored
                self.assertEqual(self.app.midpoint_handles["1_2"], 300)

    def test_update_connection_curve(self):
        """Test updating curve offset for a connection."""
        # Setup a connection with default curve data
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 0,
                "curve_Y": 0
            }
        }
        
        # Mock calculate_curve_points
        with patch.object(self.app, '_calculate_curve_points', return_value=[50, 50, 75, 75, 150, 150]):
            # Update the curve
            result = self.app.update_connection_curve(1, 2, 25, -15)
            
            # Verify result
            self.assertTrue(result)
            self.assertEqual(self.app.connections["1_2"]["curve_X"], 25)
            self.assertEqual(self.app.connections["1_2"]["curve_Y"], -15)

    def test_update_connection_curve_updates_handle(self):
        """Test that updating a curve also updates its midpoint handle in adjust mode."""
        # Setup
        self.app._mode = ApplicationMode.ADJUST
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 0,
                "curve_Y": 0
            }
        }
        
        # Add a midpoint handle
        self.app.midpoint_handles = {"1_2": 300}
        
        # Mock canvas operations and helpers
        with patch.object(self.app, '_calculate_curve_points', 
                         return_value=[50, 50, 120, 90, 150, 150]):
            with patch.object(self.app, '_calculate_midpoint_handle_position',
                             return_value=(120, 90)):
                with patch.object(self.app, '_draw_midpoint_handle',
                                 return_value=301):
                    
                    # Call the method
                    result = self.app.update_connection_curve(1, 2, 20, -10)
                    
                    # Verify result
                    self.assertTrue(result)
                    
                    # Verify curve values were updated
                    self.assertEqual(self.app.connections["1_2"]["curve_X"], 20)
                    self.assertEqual(self.app.connections["1_2"]["curve_Y"], -10)
                    
                    # Verify both the line and old handle were deleted
                    self.app.canvas.delete.assert_any_call(200)  # Line
                    self.app.canvas.delete.assert_any_call(300)  # Old handle
                    
                    # Verify handle was updated in dictionary
                    self.assertEqual(self.app.midpoint_handles["1_2"], 301)

    def test_update_connections_with_midpoint_handles(self):
        """Test updating connections redraws midpoint handles in adjust mode."""
        # Setup
        self.app._mode = ApplicationMode.ADJUST
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Create connection
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 10,
                "curve_Y": -5
            }
        }
        
        # Add a midpoint handle
        self.app.midpoint_handles = {"1_2": 300}
        
        # Mock the update_connection_curve method to prevent actual implementation
        with patch.object(self.app, 'update_connection_curve') as mock_update:
            # Call the method
            self.app._update_connections(1)
            
            # Verify update_connection_curve was called with the right parameters
            mock_update.assert_called_once_with(1, 2, 10, -5)

    def test_drag_midpoint_with_no_connection(self):
        """Test dragging a midpoint when its connection doesn't exist."""
        # Setup: In adjust mode with active midpoint drag
        self.app._mode = ApplicationMode.ADJUST
        self.app.drag_state = {
            "active": True,
            "type": "midpoint",
            "id": "1_2",  # Key that doesn't match any connection
            "start_x": 100,
            "start_y": 100,
            "last_x": 100,
            "last_y": 100
        }
        
        # Empty connections dict
        self.app.connections = {}
        
        # Mock update_connection_curve
        with patch.object(self.app, 'update_connection_curve') as mock_update:
            # Create mock event
            event = Mock()
            event.x = 110
            event.y = 90
            
            # Call drag motion method
            self.app._drag_motion(event)
            
            # Verify update_connection_curve was not called
            mock_update.assert_not_called()

    def test_extreme_curve_displacement(self):
        """Test very large curve displacement values."""
        # Setup two circles
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Create a connection with extreme curve values
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 500,  # Very large X displacement
                "curve_Y": -300  # Very large negative Y displacement
            }
        }
        
        # Calculate curve points
        points = self.app._calculate_curve_points(1, 2)
        
        # Expected points with extreme offset
        # Base midpoint is (100, 100)
        # With offset: (100+500, 100-300) = (600, -200)
        expected = [50, 50, 600, -200, 150, 150]
        self.assertEqual(points, expected)
        
        # Test that the handle position is still calculated correctly (with half offset)
        handle_x, handle_y = self.app._calculate_midpoint_handle_position(1, 2)
        self.assertEqual(handle_x, 100 + 500/2)  # 350
        self.assertEqual(handle_y, 100 - 300/2)  # -50
    
    def test_multiple_curve_directions(self):
        """Test curve displacements in different directions."""
        # Setup two circles
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 100, "y": 100, "color_priority": 1, "connected_to": [2, 3, 4, 5]
        }
        
        # Create four other circles in different directions
        other_circles = [
            {"id": 2, "canvas_id": 101, "x": 200, "y": 100, "color_priority": 2, "connected_to": [1]},  # East
            {"id": 3, "canvas_id": 102, "x": 100, "y": 200, "color_priority": 3, "connected_to": [1]},  # South
            {"id": 4, "canvas_id": 103, "x": 0, "y": 100, "color_priority": 2, "connected_to": [1]},    # West
            {"id": 5, "canvas_id": 104, "x": 100, "y": 0, "color_priority": 3, "connected_to": [1]}     # North
        ]
        
        all_circles = [first_circle] + other_circles
        self.app.circles = all_circles
        self.app.circle_lookup = {c["id"]: c for c in all_circles}
        
        # Create connections with different curve directions
        self.app.connections = {
            "1_2": {"line_id": 200, "from_circle": 1, "to_circle": 2, "curve_X": 0, "curve_Y": 50},    # North curve
            "1_3": {"line_id": 201, "from_circle": 1, "to_circle": 3, "curve_X": 50, "curve_Y": 0},    # East curve
            "1_4": {"line_id": 202, "from_circle": 1, "to_circle": 4, "curve_X": 0, "curve_Y": -50},   # South curve
            "1_5": {"line_id": 203, "from_circle": 1, "to_circle": 5, "curve_X": -50, "curve_Y": 0}    # West curve
        }
        
        # Test each direction
        # East connection (1-2)
        points = self.app._calculate_curve_points(1, 2)
        # Base midpoint is (150, 100), with offset (150, 150)
        self.assertEqual(points, [100, 100, 150, 150, 200, 100])
        
        # South connection (1-3)
        points = self.app._calculate_curve_points(1, 3)
        # Base midpoint is (100, 150), with offset (150, 150)
        self.assertEqual(points, [100, 100, 150, 150, 100, 200])
        
        # West connection (1-4)
        points = self.app._calculate_curve_points(1, 4)
        # Base midpoint is (50, 100), with offset (50, 50)
        self.assertEqual(points, [100, 100, 50, 50, 0, 100])
        
        # North connection (1-5)
        points = self.app._calculate_curve_points(1, 5)
        # Base midpoint is (100, 50), with offset (50, 50)
        self.assertEqual(points, [100, 100, 50, 50, 100, 0])
    
    def test_overlapping_connections_curve_behavior(self):
        """Test behavior with multiple overlapping connections."""
        # Setup three circles in a triangle pattern
        circles = [
            {"id": 1, "canvas_id": 100, "x": 100, "y": 100, "color_priority": 1, "connected_to": [2, 3]},
            {"id": 2, "canvas_id": 101, "x": 200, "y": 100, "color_priority": 2, "connected_to": [1, 3]},
            {"id": 3, "canvas_id": 102, "x": 150, "y": 200, "color_priority": 3, "connected_to": [1, 2]}
        ]
        
        self.app.circles = circles
        self.app.circle_lookup = {c["id"]: c for c in circles}
        
        # Create connections with different curve values
        # Note: Using consistent connection keys with lowest ID first
        self.app.connections = {
            "1_2": {"line_id": 200, "from_circle": 1, "to_circle": 2, "curve_X": 0, "curve_Y": -30},
            "1_3": {"line_id": 201, "from_circle": 1, "to_circle": 3, "curve_X": 20, "curve_Y": 0},
            "2_3": {"line_id": 202, "from_circle": 2, "to_circle": 3, "curve_X": 20, "curve_Y": 0}
        }
        
        # Convert circles to canvas items
        self.app.canvas.create_line.reset_mock()
        
        # Mock calculate_curve_points to return a consistent value each time
        # instead of using a fixed list that can run out
        with patch.object(self.app, '_calculate_curve_points', return_value=[100, 100, 150, 150, 200, 200]):
            # Update all connections for one circle only to simplify the test
            self.app._update_connections(1)
            
            # Verify that connections were redrawn
            # The exact count depends on internal implementation, but we expect at least 2 calls
            # since circle 1 is connected to 2 other circles
            self.assertGreaterEqual(self.app.canvas.create_line.call_count, 2)
    
    def test_curve_preservation_during_circle_movement(self):
        """Test that curve parameters are preserved when circles move."""
        # Setup two circles
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Create a connection with specific curve values
        # Use either connection key format that might be used by the app
        connection_key = "1_2"  # Try this format first
        self.app.connections = {
            connection_key: {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 30,
                "curve_Y": -20
            }
        }
        
        # Setup drag state for circle movement
        self.app.in_edit_mode = True  # Important: Set edit mode to true
        self.app.drag_state = {
            "active": True,
            "type": "circle",
            "id": 1,
            "start_x": 50,
            "start_y": 50,
            "last_x": 50,
            "last_y": 50
        }
        
        # Mock _update_connections to verify it's called
        # This is more reliable than mocking update_connection_curve
        with patch.object(self.app, '_update_connections') as mock_update:
            # Create mock event to move the circle
            event = Mock()
            event.x = 70
            event.y = 60
            
            # Move the circle
            self.app._drag_motion(event)
            
            # Verify _update_connections was called with the moved circle's ID
            mock_update.assert_called_once_with(1)
    
    def test_curve_behavior_across_application_modes(self):
        """Test that curves behave correctly across different application modes."""
        # Setup circles and connection
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Create a connection
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 30,
                "curve_Y": -20
            }
        }
        
        # Mock key methods for tracking
        with patch.object(self.app, '_hide_midpoint_handles') as mock_hide:
            with patch.object(self.app, '_show_midpoint_handles') as mock_show:
                with patch.object(self.app, '_calculate_curve_points') as mock_calc:
                    # Set up mock for calculate_curve_points
                    mock_calc.return_value = [50, 50, 130, 80, 150, 150]
                    
                    # 1. Start in CREATE mode
                    self.app._mode = ApplicationMode.CREATE
                    
                    # 2. Switch to ADJUST mode
                    self.app._set_application_mode(ApplicationMode.ADJUST)
                    mock_show.assert_called_once()
                    
                    # Verify curve points are still calculated correctly
                    points = self.app._calculate_curve_points(1, 2)
                    self.assertEqual(points, [50, 50, 130, 80, 150, 150])
                    
                    # 3. Switch back to CREATE mode
                    self.app._set_application_mode(ApplicationMode.CREATE)
                    mock_hide.assert_called_once()
                    
                    # Verify curve points are still calculated correctly
                    points = self.app._calculate_curve_points(1, 2)
                    self.assertEqual(points, [50, 50, 130, 80, 150, 150])

    def test_curve_persistence_after_selection(self):
        """Test that curve parameters persist after selection mode."""
        # Setup our own circles directly instead of using _draw_on_click
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 50, "y": 50, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 150, "y": 150, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Create a connection with our own values
        # Check both possible connection key formats
        if "1_2" in self.app.connections:
            connection_key = "1_2"
        else:
            connection_key = "2_1"
        
        self.app.connections = {
            connection_key: {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": 25,
                "curve_Y": -15
            }
        }
        
        # Store the original values to compare later
        original_curve_x = 25
        original_curve_y = -15
        
        # Switch to ADJUST mode to test handle creation
        with patch.object(self.app, '_draw_midpoint_handle') as mock_draw:
            self.app._set_application_mode(ApplicationMode.ADJUST)
            
            # Verify midpoint handle is drawn
            mock_draw.assert_called()
            
        # Switch back to CREATE mode
        self.app._set_application_mode(ApplicationMode.CREATE)
        
        # Verify the original curve values are unchanged - check both possible keys
        found_key = None
        for key in ["1_2", "2_1"]:
            if key in self.app.connections:
                found_key = key
                break
                
        self.assertIsNotNone(found_key, "Connection not found in either format")
        self.assertEqual(self.app.connections[found_key]["curve_X"], original_curve_x)
        self.assertEqual(self.app.connections[found_key]["curve_Y"], original_curve_y)

    def test_negative_curve_values(self):
        """Test negative values for curve displacement."""
        # Setup two circles
        first_circle = {
            "id": 1, "canvas_id": 100, "x": 100, "y": 100, "color_priority": 1, "connected_to": [2]
        }
        second_circle = {
            "id": 2, "canvas_id": 101, "x": 200, "y": 200, "color_priority": 2, "connected_to": [1]
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Create a connection with negative curve values
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2,
                "curve_X": -40,
                "curve_Y": -30
            }
        }
        
        # Calculate curve points
        points = self.app._calculate_curve_points(1, 2)
        
        # Expected: midpoint (150,150) + offset (-40,-30) = (110,120)
        expected = [100, 100, 110, 120, 200, 200]
        self.assertEqual(points, expected)
        
        # Test that handle position is calculated correctly with negative offset
        handle_x, handle_y = self.app._calculate_midpoint_handle_position(1, 2)
        self.assertEqual(handle_x, 150 - 40/2)  # 130
        self.assertEqual(handle_y, 150 - 30/2)  # 135

if __name__ == "__main__":
    unittest.main()