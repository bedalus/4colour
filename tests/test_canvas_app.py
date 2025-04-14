"""
Unit tests for canvas_app.py.
"""

import sys
import os
# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from test_utils import MockAppTestCase
from unittest.mock import patch, MagicMock
from app_enums import ApplicationMode

class TestCanvasApplication(MockAppTestCase):
    """Test cases for the main CanvasApplication class."""
    
    def test_initialization(self):
        """Test that the app initializes with correct values."""
        self.assertEqual(self.app.canvas_width, 800)
        self.assertEqual(self.app.canvas_height, 500)
        self.assertEqual(self.app.circle_radius, 10)
        self.assertEqual(self.app.midpoint_radius, 5)
        
        # Fixed nodes should be present at startup - two nodes plus connection
        self.assertEqual(len(self.app.circles), 2)
        
        # Check for fixed nodes with correct IDs
        node_ids = [circle['id'] for circle in self.app.circles]
        self.assertIn(self.app.FIXED_NODE_A_ID, node_ids)
        self.assertIn(self.app.FIXED_NODE_B_ID, node_ids)
        
        # Fixed nodes should be in circle_lookup
        self.assertIn(self.app.FIXED_NODE_A_ID, self.app.circle_lookup)
        self.assertIn(self.app.FIXED_NODE_B_ID, self.app.circle_lookup)
        
        # One connection should exist between the fixed nodes
        self.assertEqual(len(self.app.connections), 1)
        
        # Other initializations remain the same
        self.assertEqual(self.app.next_id, 1)
        self.assertIsNone(self.app.last_circle_id)
        self.assertFalse(self.app.debug_enabled)
        
        self.root.title.assert_called_with("4colour Canvas")
        self.root.geometry.assert_called_with("800x600")
    
    def test_mode_properties(self):
        """Test mode property getters and setters."""
        # Test edit mode property
        self.app._mode = ApplicationMode.CREATE
        self.assertFalse(self.app.in_edit_mode)
        
        self.app._mode = ApplicationMode.ADJUST
        self.assertTrue(self.app.in_edit_mode)
        
        # Test edit mode setter
        with patch.object(self.app, '_set_application_mode') as mock_set_mode:
            self.app.in_edit_mode = True
            mock_set_mode.assert_called_with(ApplicationMode.ADJUST)
            
            self.app.in_edit_mode = False
            mock_set_mode.assert_called_with(ApplicationMode.CREATE)
        
        # Test selection mode property
        self.app._mode = ApplicationMode.CREATE
        self.assertFalse(self.app.in_selection_mode)
        
        self.app._mode = ApplicationMode.SELECTION
        self.assertTrue(self.app.in_selection_mode)
        
        # Test selection mode setter
        with patch.object(self.app, '_set_application_mode') as mock_set_mode:
            self.app.in_selection_mode = True
            mock_set_mode.assert_called_with(ApplicationMode.SELECTION)
            
            self.app._mode = ApplicationMode.SELECTION
            self.app.in_selection_mode = False
            mock_set_mode.assert_called_with(ApplicationMode.CREATE)
            
    def test_delegation_methods(self):
        """Test that delegate methods call the appropriate manager methods."""
        # Test delegating to UI manager
        with patch.object(self.app.ui_manager, 'toggle_debug') as mock_toggle:
            self.app._toggle_debug()
            mock_toggle.assert_called_once()
        
        # Test delegating to circle manager
        with patch.object(self.app.circle_manager, 'remove_circle') as mock_remove:
            event = self._create_click_event(100, 100)
            self.app._remove_circle(event)
            mock_remove.assert_called_once_with(event)
        
        # Test delegating to connection manager
        with patch.object(self.app.connection_manager, 'update_connections') as mock_update:
            self.app._update_connections(1)
            mock_update.assert_called_once_with(1)
        
        # Test delegating to interaction handler
        with patch.object(self.app.interaction_handler, 'toggle_mode') as mock_toggle:
            self.app._toggle_mode()
            mock_toggle.assert_called_once()
        
        # Test delegating to color manager
        with patch.object(self.app.color_manager, 'assign_color_based_on_connections') as mock_assign:
            self.app._assign_color_based_on_connections(1)
            mock_assign.assert_called_once_with(1)

    def test_on_window_resize(self):
        """Test handling of window resize events."""
        with patch.object(self.app, '_update_canvas_dimensions') as mock_update:
            event = MagicMock(widget=self.root)
            self.app._on_window_resize(event)
            self.root.after.assert_called_with(100, mock_update)

    def test_update_canvas_dimensions(self):
        """Test updating canvas dimensions and related UI updates."""
        self.app.canvas.winfo_width.return_value = 900
        self.app.canvas.winfo_height.return_value = 600
        self.app.debug_enabled = True
        self.app.hint_text_id = 101
        self.app.edit_hint_text_id = 102

        with patch.object(self.app.ui_manager, 'show_debug_info') as mock_debug, \
             patch.object(self.app.ui_manager, 'show_hint_text') as mock_hint, \
             patch.object(self.app.ui_manager, 'show_edit_hint_text') as mock_edit_hint:
            self.app._update_canvas_dimensions()

            self.assertEqual(self.app.canvas_width, 900)
            self.assertEqual(self.app.canvas_height, 600)
            mock_debug.assert_called_once()
            mock_hint.assert_called_once()
            mock_edit_hint.assert_called_once()

    def test_reset_drag_state(self):
        """Test resetting the drag state."""
        self.app.drag_state = {
            "active": True,
            "type": "circle",
            "id": 1,
            "start_x": 50,
            "start_y": 50,
            "last_x": 60,
            "last_y": 60
        }

        self.app._reset_drag_state()

        self.assertEqual(self.app.drag_state, {
            "active": False,
            "type": None,
            "id": None,
            "start_x": 0,
            "start_y": 0,
            "last_x": 0,
            "last_y": 0
        })

    def test_drag_circle_motion(self):
        """Test dragging a circle."""
        with patch.object(self.app.interaction_handler, 'drag_circle_motion') as mock_drag:
            self.app._drag_circle_motion(100, 100, 10, 10)
            mock_drag.assert_called_once_with(100, 100, 10, 10)

    def test_drag_midpoint_motion(self):
        """Test dragging a midpoint."""
        with patch.object(self.app.interaction_handler, 'drag_midpoint_motion') as mock_drag:
            self.app._drag_midpoint_motion(150, 150)
            mock_drag.assert_called_once_with(150, 150)

    def test_main_entry_point(self):
        """Test the main entry point of the application."""
        with patch('canvas_app.tk.Tk') as mock_tk, patch('canvas_app.CanvasApplication') as mock_app:
            from canvas_app import main
            main()
            mock_tk.assert_called_once()
            mock_app.assert_called_once_with(mock_tk.return_value)
            mock_tk.return_value.mainloop.assert_called_once()