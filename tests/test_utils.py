"""
Test utilities for the 4colour project tests.

This module contains common utilities and setup code for tests.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import tkinter as tk
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app_enums import ApplicationMode

class BaseTestCase(unittest.TestCase):
    """Base test case with common utilities but no application dependencies."""
    
    def _create_click_event(self, x, y):
        """Create a mock click event with the specified coordinates."""
        event = Mock()
        event.x = x
        event.y = y
        return event
        
    def _create_key_event(self, key):
        """Create a mock key press event."""
        event = Mock()
        event.char = key
        return event
    
    def _create_test_circle(self, circle_id, x, y, priority=1, connections=None):
        """Helper to create a test circle with specified parameters."""
        if connections is None:
            connections = []
            
        canvas_id = 100 + circle_id
        
        circle = {
            "id": circle_id,
            "canvas_id": canvas_id,
            "x": x,
            "y": y,
            "color_priority": priority,
            "connected_to": connections,
            "ordered_connections": connections.copy(),  # Initialize with same values as connections
            "enclosed": False  # Default to not enclosed
        }
        
        return circle

class MockAppTestCase(BaseTestCase):
    """Test case with a pre-configured mock app instance."""
    
    def setUp(self):
        """Set up common test environment with mocked app."""
        # Create a mock root window
        self.root = MagicMock()
        self.root.tk = MagicMock()
        self.root.winfo_reqwidth = MagicMock(return_value=800)
        self.root.winfo_reqheight = MagicMock(return_value=600)
        
        # Apply mock patches - store original Canvas for reference
        self.patch_frame = patch('tkinter.ttk.Frame')
        self.patch_canvas = patch('tkinter.Canvas')
        self.patch_button = patch('tkinter.ttk.Button')
        
        self.mock_frame = self.patch_frame.start()
        self.mock_canvas = self.patch_canvas.start()
        self.mock_button = self.patch_button.start()
        
        # Import here to avoid circular imports during module loading
        from canvas_app import CanvasApplication
        
        # Create the app with mocked components
        self.app = CanvasApplication(self.root)
        
        # Mock the canvas for testing WITHOUT spec - this is the key fix
        self.app.canvas = MagicMock()  # Removed spec=tk.Canvas which causes the error
        
        # Mock the debug button
        self.app.debug_button = MagicMock()
        
    def tearDown(self):
        """Clean up resources after tests."""
        self.patch_frame.stop()
        self.patch_canvas.stop()
        self.patch_button.stop()

# Add a simple test to verify the test_utils.py file itself
class TestUtilsTests(unittest.TestCase):
    """Simple tests for the test_utils.py file."""
    
    def test_create_click_event(self):
        """Test that we can create a mock click event."""
        base_test = BaseTestCase()
        event = base_test._create_click_event(10, 20)
        self.assertEqual(event.x, 10)
        self.assertEqual(event.y, 20)

if __name__ == "__main__":
    unittest.main()
