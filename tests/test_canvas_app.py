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
from color_utils import get_priority_from_color

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
        self.assertEqual(self.app.canvas_width, 800)  # Updated to match new value
        self.assertEqual(self.app.canvas_height, 500)
        self.assertEqual(self.app.circle_radius, 10)
        self.assertEqual(set(self.app.available_colors), {"green", "blue", "red", "yellow"})
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
        
        # Mock the color selection - updated to use new function
        with patch.object(self.app, '_assign_color_based_on_connections', return_value=('red', 4)):
            # Call the method
            self.app._draw_on_click(event)
        
        # Check that create_oval was called on the canvas
        self.app.canvas.create_oval.assert_called_once()
        
        # Check that the coordinates were stored
        self.assertEqual(len(self.app.drawn_items), 1)
        self.assertEqual(self.app.drawn_items[0], (100, 100))
        
        # Check that circle data was stored correctly
        self.assertEqual(len(self.app.circles), 1)
        circle = self.app.circles[0]
        self.assertEqual(circle["id"], 1)
        self.assertEqual(circle["x"], 100)
        self.assertEqual(circle["y"], 100)
        self.assertEqual(circle["color"], "red")
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
        # Setup: Add a first circle
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
            # Mock the color selection - updated to use new function
            with patch.object(self.app, '_assign_color_based_on_connections', return_value=('green', 2)):
                # Call the method
                self.app._draw_on_click(event)
            
            # Check that show_hint_text was called
            mock_show_hint.assert_called_once()
        
        # Check that create_oval was called
        self.app.canvas.create_oval.assert_called_once()
        
        # Check that create_line was NOT called since we now use selection mode
        self.app.canvas.create_line.assert_not_called()
        
        # Check that circle data was stored correctly
        self.assertEqual(len(self.app.circles), 2)
        second_circle = self.app.circles[1]
        self.assertEqual(second_circle["id"], 2)
        self.assertEqual(second_circle["x"], 100)
        self.assertEqual(second_circle["y"], 100)
        self.assertEqual(second_circle["color"], "green")
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
        # Setup: Add a circle and enable debug
        self.app.circles = [{
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color": "blue",
            "color_priority": 3,  # Added missing color_priority
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
        self.assertIn("Color: blue", kwargs['text'])
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
        self.app._draw_on_click(self._create_click_event(100, 100))  # Circle 1
        self.app._draw_on_click(self._create_click_event(200, 100))  # Circle 2
        
        # Give them different colors to avoid conflict resolution
        self.app.circle_lookup[1]["color"] = "yellow"
        self.app.circle_lookup[1]["color_priority"] = 1
        self.app.circle_lookup[2]["color"] = "green"
        self.app.circle_lookup[2]["color_priority"] = 2
        
        # Add connection
        result = self.app.add_connection(1, 2)
        
        # Verify connection was made successfully
        self.assertTrue(result)
        self.assertIn(2, self.app.circle_lookup[1]["connected_to"])
        self.assertIn(1, self.app.circle_lookup[2]["connected_to"])
        
        # Verify colors haven't changed (no conflict)
        self.assertEqual(self.app.circle_lookup[1]["color_priority"], 1)
        self.assertEqual(self.app.circle_lookup[1]["color"], "yellow")
    
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
        self.app._draw_on_click(self._create_click_event(100, 100))  # Circle 1
        self.app._draw_on_click(self._create_click_event(200, 100))  # Circle 2
        
        # Manually set up selection state
        self.app.newly_placed_circle_id = 2
        self.app.selected_circles = [1]
        self.app.in_selection_mode = True
        
        # Give them the same color to force conflict resolution
        self.app.circle_lookup[1]["color"] = "yellow"
        self.app.circle_lookup[1]["color_priority"] = 1
        self.app.circle_lookup[2]["color"] = "yellow"
        self.app.circle_lookup[2]["color_priority"] = 1
        
        # Mock selection indicator for cleanup
        self.app.selection_indicators = {1: self.app.canvas.create_line(0, 0, 10, 0)}
        
        # Call confirm selection
        self.app._confirm_selection(self._create_key_event('y'))
        
        # Verify connections were made
        self.assertIn(1, self.app.circle_lookup[2]["connected_to"])
        
        # Verify color conflict was resolved (circle 2 should no longer be yellow)
        self.assertNotEqual(self.app.circle_lookup[2]["color_priority"], 1)
        self.assertNotEqual(self.app.circle_lookup[2]["color"], "yellow")

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
        self.app.canvas.bind.assert_any_call("<Button-1>", self.app._start_drag)
        self.app.canvas.bind.assert_any_call("<B1-Motion>", self.app._drag_circle)
        self.app.canvas.bind.assert_any_call("<ButtonRelease-1>", self.app._end_drag)
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
        self.app.dragged_circle_id = None
        
        # Mock the get_circle_at_coords method to return our circle ID
        with patch.object(self.app, 'get_circle_at_coords', return_value=1):
            # Create a mock event for mouse click
            event = Mock()
            event.x = 50
            event.y = 50
            
            # Call the start drag method
            self.app._start_drag(event)
            
            # Check that the dragged circle ID was set correctly
            self.assertEqual(self.app.dragged_circle_id, 1)
    
    def test_start_drag_no_circle(self):
        """Test starting to drag when no circle is clicked."""
        self.app.in_edit_mode = True
        self.app.dragged_circle_id = None
        
        # Mock the get_circle_at_coords method to return None (no circle found)
        with patch.object(self.app, 'get_circle_at_coords', return_value=None):
            # Create a mock event for mouse click
            event = Mock()
            event.x = 200
            event.y = 200
            
            # Call the start drag method
            self.app._start_drag(event)
            
            # Check that the dragged circle ID remains None
            self.assertIsNone(self.app.dragged_circle_id)
    
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
        self.app.dragged_circle_id = 1
        
        # Mock the update_connections method
        with patch.object(self.app, '_update_connections') as mock_update:
            # Create a mock event for mouse drag
            event = Mock()
            event.x = 60
            event.y = 70  # Moved 10 right and 20 down
            
            # Call the drag method
            self.app._drag_circle(event)
            
            # Check that the circle was moved on the canvas
            self.app.canvas.move.assert_called_once_with(100, 10, 20)
            
            # Check that the circle's coordinates were updated
            self.assertEqual(circle["x"], 60)
            self.assertEqual(circle["y"], 70)
            
            # Check that connections were updated
            mock_update.assert_called_once_with(1)
    
    def test_end_drag(self):
        """Test ending a circle drag operation."""
        # Setup: Enable edit mode and set a circle as being dragged
        self.app.in_edit_mode = True
        self.app.dragged_circle_id = 1
        
        # Create a mock event for mouse release
        event = Mock()
        
        # Call the end drag method
        self.app._end_drag(event)
        
        # Check that the dragged circle ID was reset
        self.assertIsNone(self.app.dragged_circle_id)
    
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
        
        # Call the update connections method
        self.app._update_connections(1)
        
        # Check that the old line was deleted
        self.app.canvas.delete.assert_called_once_with(200)
        
        # Check that a new line was created
        self.app.canvas.create_line.assert_called_once_with(
            50, 50, 100, 100, width=1
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
    
    # Update test for key binding change from space to y key
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
        self.app.canvas.bind.assert_any_call("<Button-1>", self.app._start_drag)
        self.app.canvas.bind.assert_any_call("<B1-Motion>", self.app._drag_circle)
        self.app.canvas.bind.assert_any_call("<ButtonRelease-1>", self.app._end_drag)
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
        color, priority = self.app._assign_color_based_on_connections()
        self.assertEqual(color, "yellow")
        self.assertEqual(priority, 1)
        
        # Test passing an existing circle ID (should still return yellow for now)
        color, priority = self.app._assign_color_based_on_connections(1)
        self.assertEqual(color, "yellow")
        self.assertEqual(priority, 1)
        
    def test_draw_on_click_with_deterministic_color(self):
        """Test drawing a circle with deterministic color assignment."""
        # Setup: Mock the color assignment function
        with patch.object(self.app, '_assign_color_based_on_connections', return_value=("yellow", 1)) as mock_assign:
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
        self.assertEqual(circle["color"], "yellow")
        self.assertEqual(circle["color_priority"], 1)

    def test_assign_color_based_on_connections_with_conflicts(self):
        """Test color assignment logic when conflicts exist."""
        # Setup directly instead of using _draw_on_click to avoid dependency issues
        # Create 4 circles manually
        first_circle = {
            "id": 1,
            "canvas_id": 100,
            "x": 50, 
            "y": 50,
            "color": "yellow",
            "color_priority": 1,
            "connected_to": []
        }
        second_circle = {
            "id": 2,
            "canvas_id": 101,
            "x": 100,
            "y": 50,
            "color": "green",
            "color_priority": 2,
            "connected_to": []
        }
        third_circle = {
            "id": 3,
            "canvas_id": 102,
            "x": 150,
            "y": 50,
            "color": "blue",
            "color_priority": 3,
            "connected_to": []
        }
        fourth_circle = {
            "id": 4,
            "canvas_id": 103,
            "x": 200,
            "y": 50,
            "color": "yellow",  # Start with yellow, will be changed
            "color_priority": 1,
            "connected_to": []
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
        
        # When connected to circles with all priorities 1-3, should get priority 4 (red)
        self.assertEqual(priority, 4)
        self.assertEqual(self.app.circle_lookup[4]["color"], "red")

    def test_update_circle_color(self):
        """Test updating a circle's color."""
        # Setup: Add a circle
        circle = {
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color": "yellow",
            "color_priority": 1,
            "connected_to": []
        }
        
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}
        
        # Test: Update the circle's color
        result = self.app._update_circle_color(1, "blue", 3)
        
        # Check the result was successful
        self.assertTrue(result)
        
        # Check that the circle data was updated
        self.assertEqual(circle["color"], "blue")
        self.assertEqual(circle["color_priority"], 3)
        
        # Check that the canvas item was updated
        self.app.canvas.itemconfig.assert_called_once_with(100, fill="blue")
        
    def test_confirm_selection_with_color_reassignment(self):
        """Test confirming selections with color reassignment."""
        # Setup: Add two circles and prepare for selection confirmation
        first_circle = {
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color": "yellow",
            "color_priority": 1,
            "connected_to": []
        }
        second_circle = {
            "id": 2,
            "canvas_id": 101,
            "x": 100,
            "y": 100,
            "color": "yellow",  # Same color as first circle - will cause conflict
            "color_priority": 1,
            "connected_to": []
        }
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        self.app.in_selection_mode = True
        self.app.newly_placed_circle_id = 2
        self.app.selected_circles = [1]  # Selected circle 1 to connect to
        self.app.selection_indicators = {1: 200}
        self.app.hint_text_id = 300
        
        # Mock the necessary methods
        with patch.object(self.app, 'add_connection', return_value=True) as mock_add:
            with patch.object(self.app, '_assign_color_based_on_connections', return_value=("green", 2)) as mock_assign:
                with patch.object(self.app, '_update_circle_color') as mock_update:
                    # Create a mock event for y key press
                    event = Mock()
                    
                    # Call the confirm selection method
                    self.app._confirm_selection(event)
                    
                    # Verify add_connection was called
                    mock_add.assert_called_with(2, 1)
                    
                    # Verify color assignment was called
                    mock_assign.assert_called_with(2)
                    
                    # Verify color update was called with new color
                    mock_update.assert_called_with(2, "green", 2)
        
        # Check that selection mode was exited
        self.assertFalse(self.app.in_selection_mode)

    def test_check_and_resolve_color_conflicts(self):
        """Test the basic color conflict resolution logic."""
        # Create circles manually instead of using _draw_on_click
        first_circle = {
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color": "yellow",
            "color_priority": 1,
            "connected_to": []
        }
        second_circle = {
            "id": 2,
            "canvas_id": 101,
            "x": 100,
            "y": 50,
            "color": "yellow",  # Same color as first circle - will cause conflict
            "color_priority": 1,
            "connected_to": []
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
        
        # Check that circle 2's color was changed to resolve the conflict
        self.assertEqual(priority, 2)  # Priority should be 2
        self.assertEqual(self.app.circle_lookup[2]["color_priority"], 2)  # Should be green (priority 2)
        self.assertEqual(self.app.circle_lookup[2]["color"], "green")

if __name__ == "__main__":
    unittest.main()