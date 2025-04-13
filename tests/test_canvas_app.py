"""
Unit tests for canvas_app.py.
"""

import sys
import os
# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from test_utils import MockAppTestCase
from unittest.mock import patch
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