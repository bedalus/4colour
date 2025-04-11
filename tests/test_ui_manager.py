"""
Unit tests for ui_manager.py.
"""

import sys
import os
# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import tkinter as tk
from unittest.mock import patch, MagicMock
from test_utils import MockAppTestCase
from app_enums import ApplicationMode

class TestUIManager(MockAppTestCase):
    """Test cases for the UI Manager."""
    
    def test_focus_after(self):
        """Test that focus is set to debug button after command execution."""
        mock_func = MagicMock()
        self.app._focus_after(mock_func)
        
        mock_func.assert_called_once()
        self.app.debug_button.focus_set.assert_called_once()
    
    def test_toggle_debug_enable(self):
        """Test enabling the debug display."""
        self.app.debug_enabled = False
        self.app.debug_text = None
        
        # Update to patch the ui_manager's show_debug_info method
        with patch.object(self.app.ui_manager, 'show_debug_info') as mock_show_debug:
            self.app._toggle_debug()
            
            self.assertTrue(self.app.debug_enabled)
            mock_show_debug.assert_called_once()
    
    def test_toggle_debug_disable(self):
        """Test disabling the debug display."""
        self.app.debug_enabled = True
        self.app.debug_text = 100  # Mock text ID
        
        self.app._toggle_debug()
        
        self.assertFalse(self.app.debug_enabled)
        self.app.canvas.delete.assert_called_once_with(100)
    
    def test_show_debug_info_with_circle(self):
        """Test showing debug info for a circle."""
        self.app.circles = [{
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color_priority": 3,  # Priority 3 is blue
            "connected_to": [2]
        }]
        self.app.debug_enabled = True
        
        self.app._show_debug_info()
        
        self.app.canvas.create_text.assert_called_once()
        args, kwargs = self.app.canvas.create_text.call_args
        self.assertEqual(kwargs['anchor'], tk.NW)
        self.assertIn("Circle ID: 1", kwargs['text'])
        self.assertIn("Position: (50, 50)", kwargs['text'])
        self.assertIn("Color: blue (priority: 3)", kwargs['text'])
        self.assertIn("Connected to: 2", kwargs['text'])
    
    def test_show_debug_info_no_circles(self):
        """Test showing debug info when no circles are present."""
        self.app.circles = []
        self.app.debug_enabled = True
        
        self.app._show_debug_info()
        
        self.app.canvas.create_text.assert_called_once()
        args, kwargs = self.app.canvas.create_text.call_args
        self.assertEqual(kwargs['anchor'], tk.NW)
        self.assertEqual(kwargs['text'], "No circles drawn yet")
    
    def test_show_hint_text(self):
        """Test displaying the hint text in selection mode."""
        self.app.canvas.create_text.return_value = 300
        self.app.canvas_width = 700
        
        self.app._show_hint_text()
        
        self.app.canvas.create_text.assert_called_once()
        args, kwargs = self.app.canvas.create_text.call_args
        self.assertEqual(args[0], 350)  # Half of canvas_width
        self.assertEqual(args[1], 20)
        self.assertEqual(kwargs['text'], "Please select which circles to connect to then press 'y'")
        self.assertEqual(kwargs['anchor'], tk.N)
        self.assertEqual(self.app.hint_text_id, 300)
    
    def test_show_edit_hint_text(self):
        """Test displaying edit mode hint text."""
        self.app.hint_text_id = 100
        self.app.edit_hint_text_id = None
        self.app.canvas_width = 700
        self.app.canvas.create_text.return_value = 200
        
        self.app._show_edit_hint_text()
        
        # Should delete the hint text
        self.app.canvas.delete.assert_called_once_with(100)
        self.assertIsNone(self.app.hint_text_id)
        
        # Should create edit hint text
        self.app.canvas.create_text.assert_called_once()
        args, kwargs = self.app.canvas.create_text.call_args
        self.assertEqual(args[0], 370)  # (Half of canvas_width) + 20
        self.assertEqual(args[1], 20)
        self.assertEqual(kwargs['text'], "Click-and-drag to move, right click to remove")
        self.assertEqual(self.app.edit_hint_text_id, 200)
        
    def test_clear_canvas(self):
        """Test clearing the canvas."""
        # Test when in ADJUST mode (should not clear)
        self.app._mode = ApplicationMode.ADJUST
        self.app._clear_canvas()
        self.app.canvas.delete.assert_not_called()
        
        # Test when in CREATE mode
        self.app._mode = ApplicationMode.CREATE
        self.app.circles = [{"id": 1}]
        self.app.drawn_items = [(50, 50)]
        self.app.circle_lookup = {1: {"id": 1}}
        self.app.connections = {"1_2": {}}
        self.app.midpoint_handles = {"1_2": 300}
        self.app.last_circle_id = 1
        self.app.next_id = 2
        
        self.app._clear_canvas()
        
        self.app.canvas.delete.assert_called_once_with("all")
        self.assertEqual(len(self.app.drawn_items), 0)
        self.assertEqual(len(self.app.circles), 0)
        self.assertEqual(len(self.app.circle_lookup), 0)
        self.assertEqual(len(self.app.connections), 0)
        self.assertEqual(len(self.app.midpoint_handles), 0)
        self.assertIsNone(self.app.last_circle_id)
        self.assertEqual(self.app.next_id, 1)
