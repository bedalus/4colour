"""
Unit tests for the canvas_app module.

This module contains tests for the CanvasApplication class and its functionality.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import tkinter as tk
import sys
import os

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
        self.root.title.assert_called_with("4colour Canvas")
        self.root.geometry.assert_called_with("800x600")
    
    def test_draw_on_click(self):
        """Test that drawing on click works correctly."""
        # Create a mock event
        event = Mock()
        event.x = 100
        event.y = 100
        
        # Call the method
        self.app._draw_on_click(event)
        
        # Check that create_oval was called on the canvas
        self.app.canvas.create_oval.assert_called_once()
        
        # Check that the coordinates were stored
        self.assertEqual(len(self.app.drawn_items), 1)
        self.assertEqual(self.app.drawn_items[0], (100, 100))
    
    def test_increase_canvas_size(self):
        """Test increasing the canvas size."""
        original_width = self.app.canvas_width
        original_height = self.app.canvas_height
        
        self.app._increase_canvas_size()
        
        self.assertEqual(self.app.canvas_width, original_width + 50)
        self.assertEqual(self.app.canvas_height, original_height + 50)
        self.app.canvas.config.assert_called_once()
        
    def test_decrease_canvas_size(self):
        """Test decreasing the canvas size."""
        # Set a large initial size to ensure we can decrease
        self.app.canvas_width = 200
        self.app.canvas_height = 200
        
        self.app._decrease_canvas_size()
        
        self.assertEqual(self.app.canvas_width, 150)
        self.assertEqual(self.app.canvas_height, 150)
        self.app.canvas.config.assert_called_once()
    
    def test_min_canvas_size(self):
        """Test that canvas doesn't get too small."""
        # Set a small initial size
        self.app.canvas_width = 100
        self.app.canvas_height = 100
        
        self.app._decrease_canvas_size()
        
        # Size should remain the same
        self.assertEqual(self.app.canvas_width, 100)
        self.assertEqual(self.app.canvas_height, 100)
        # Canvas config should not be called
        self.app.canvas.config.assert_not_called()

if __name__ == "__main__":
    unittest.main()