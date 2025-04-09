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
from canvas_app import CanvasApplication

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
        with patch('tkinter.ttk.Frame'), patch('tkinter.Canvas'):
            self.app = CanvasApplication(self.root)
        # Mock the canvas to avoid actual drawing operations
        self.app.canvas = MagicMock(spec=tk.Canvas)
        self.app.drawn_items = []
    
    def test_initialization(self):
        """Test that the app initializes with correct values."""
        self.assertEqual(self.app.canvas_width, 700)
        self.assertEqual(self.app.canvas_height, 500)
        self.assertEqual(self.app.circle_radius, 5)
        self.assertEqual(self.app.available_colors, ["green", "blue", "red", "yellow"])
        self.assertEqual(self.app.circles, [])
        self.assertEqual(self.app.next_id, 1)
        self.assertIsNone(self.app.last_circle_id)
        self.assertFalse(self.app.debug_enabled)
        self.root.title.assert_called_with("4colour Canvas")
        self.root.geometry.assert_called_with("800x600")
    
    def test_get_random_color(self):
        """Test that the random color function works correctly."""
        # Set a seed to make the test predictable
        random.seed(42)
        expected_color = random.choice(self.app.available_colors)
        
        # Reset the seed for the app to use
        random.seed(42)
        actual_color = self.app._get_random_color()
        
        self.assertEqual(actual_color, expected_color)
        self.assertIn(actual_color, self.app.available_colors)
    
    def test_draw_on_click_first_circle(self):
        """Test drawing the first circle on the canvas."""
        # Create a mock event
        event = Mock()
        event.x = 100
        event.y = 100
        
        # Mock the color selection
        with patch.object(self.app, '_get_random_color', return_value='red'):
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
        self.assertEqual(circle["connected_to"], [])
        
        # Check that last_circle_id was updated
        self.assertEqual(self.app.last_circle_id, 1)
        # Check that next_id was incremented
        self.assertEqual(self.app.next_id, 2)
    
    def test_draw_on_click_second_circle(self):
        """Test drawing a second circle that connects to the first."""
        # Setup: Add a first circle
        self.app.circles = [{
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color": "blue",
            "connected_to": []
        }]
        self.app.last_circle_id = 1
        self.app.next_id = 2
        
        # Create a mock event for the second circle
        event = Mock()
        event.x = 100
        event.y = 100
        
        # Mock the canvas.create_line and create_oval methods
        self.app.canvas.create_line.return_value = 200
        self.app.canvas.create_oval.return_value = 201
        
        # Mock the color selection
        with patch.object(self.app, '_get_random_color', return_value='green'):
            # Call the method
            self.app._draw_on_click(event)
        
        # Check that create_oval was called
        self.app.canvas.create_oval.assert_called_once()
        
        # Check that create_line was called to connect the circles
        self.app.canvas.create_line.assert_called_once_with(
            50, 50, 100, 100, width=1
        )
        
        # Check that circle data was stored correctly
        self.assertEqual(len(self.app.circles), 2)
        second_circle = self.app.circles[1]
        self.assertEqual(second_circle["id"], 2)
        self.assertEqual(second_circle["x"], 100)
        self.assertEqual(second_circle["y"], 100)
        self.assertEqual(second_circle["color"], "green")
        self.assertEqual(second_circle["connected_to"], [1])
        
        # Check that first circle's connections were updated
        first_circle = self.app.circles[0]
        self.assertEqual(first_circle["connected_to"], [2])
        
        # Check that last_circle_id was updated
        self.assertEqual(self.app.last_circle_id, 2)
        # Check that next_id was incremented
        self.assertEqual(self.app.next_id, 3)
    
    def test_clear_canvas(self):
        """Test clearing the canvas."""
        # Setup: Add some circles and connections
        self.app.circles = [
            {"id": 1, "canvas_id": 100, "x": 50, "y": 50, "color": "blue", "connected_to": [2]},
            {"id": 2, "canvas_id": 101, "x": 100, "y": 100, "color": "red", "connected_to": [1]},
        ]
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

if __name__ == "__main__":
    unittest.main()