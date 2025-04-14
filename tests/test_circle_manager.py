"""
Unit tests for circle_manager.py.
"""

import sys
import os
# Add the tests directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from unittest.mock import patch, MagicMock  # Add the missing import for patch
from test_utils import MockAppTestCase
from app_enums import ApplicationMode

class TestCircleManager(MockAppTestCase):
    """Test cases for the Circle Manager."""
    
    def test_get_circle_at_coords_not_found(self):
        """Test not finding a circle at given coordinates."""
        # Use the interaction handler to create the circle
        event = self._create_click_event(50, 50)
        with patch.object(self.app, '_assign_color_based_on_connections', return_value=1):
            self.app.interaction_handler.draw_on_click(event)
            
        self.app.circle_radius = 10
        
        result = self.app.get_circle_at_coords(100, 100)  # Outside the circle
        self.assertIsNone(result)
    
    def test_remove_circle_not_in_edit_mode(self):
        """Test that removing a circle does nothing when not in edit mode."""
        self.app._mode = ApplicationMode.CREATE
        
        with patch.object(self.app, 'get_circle_at_coords') as mock_get:
            event = self._create_click_event(50, 50)
            self.app._remove_circle(event)
            
            mock_get.assert_not_called()
    
    def test_remove_circle_by_id(self):
        """Test the centralized circle removal method."""
        first_circle = self._create_test_circle(1, 50, 50, connections=[2])
        second_circle = self._create_test_circle(2, 100, 100, connections=[1])
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Create a connection
        self.app.connections = {"1_2": {"line_id": 200, "from_circle": 1, "to_circle": 2}}
        
        # Mock remove_circle_connections
        with patch.object(self.app, '_remove_circle_connections') as mock_remove_connections:
            result = self.app._remove_circle_by_id(1)
            
            self.assertTrue(result)
            mock_remove_connections.assert_called_once_with(1)
            self.app.canvas.delete.assert_called_once_with(101)
            self.assertEqual(len(self.app.circles), 1)
            self.assertEqual(self.app.circles[0]["id"], 2)
            self.assertNotIn(1, self.app.circle_lookup)
    
    def test_remove_circle_by_id_not_found(self):
        """Test removing a non-existent circle."""
        self.app.circle_lookup = {}
        
        result = self.app._remove_circle_by_id(99)
        self.assertFalse(result)
    
    def test_handle_last_circle_removed(self):
        """Test handling the special case when the last circle is removed."""
        self.app._mode = ApplicationMode.ADJUST
        
        with patch.object(self.app, '_set_application_mode') as mock_set_mode:
            self.app._handle_last_circle_removed()
            
            mock_set_mode.assert_called_with(ApplicationMode.CREATE)
            self.assertEqual(self.app.drawn_items, [])
            self.assertEqual(self.app.connections, {})
            self.assertIsNone(self.app.last_circle_id)
            self.assertEqual(self.app.next_id, 1)
            self.app.canvas.delete.assert_called_with("all")
    
    def test_handle_last_circle_removed_canvas_reset(self):
        """Test that the canvas is reset when the last circle is removed."""
        self.app.circles = []
        self.app.circle_lookup = {}
        self.app.connections = {}

        with patch.object(self.app, '_set_application_mode') as mock_set_mode:
            self.app._handle_last_circle_removed()

            mock_set_mode.assert_called_with(ApplicationMode.CREATE)
            self.app.canvas.delete.assert_called_with("all")
            self.assertEqual(self.app.drawn_items, [])
            self.assertEqual(self.app.connections, {})
            self.assertIsNone(self.app.last_circle_id)
            self.assertEqual(self.app.next_id, 1)

    def test_get_circle_at_coords_no_circles(self):
        """Test get_circle_at_coords when no circles exist."""
        self.app.circles = []
        self.app.circle_lookup = {}
        self.app.circle_radius = 10

        result = self.app.get_circle_at_coords(50, 50)
        self.assertIsNone(result)

    def test_get_circle_at_coords_on_edge(self):
        """Test get_circle_at_coords when coordinates are on the edge of a circle."""
        circle = self._create_test_circle(1, 50, 50)
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}
        self.app.circle_radius = 10

        result = self.app.get_circle_at_coords(60, 50)  # Exactly on the edge
        self.assertEqual(result, 1)

    def test_get_circle_at_coords_negative_coords(self):
        """Test get_circle_at_coords with negative coordinates."""
        circle = self._create_test_circle(1, 50, 50)
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}
        self.app.circle_radius = 10

        result = self.app.get_circle_at_coords(-10, -10)  # Negative coordinates
        self.assertIsNone(result)

    def test_get_circle_at_coords_invalid_radius(self):
        """Test get_circle_at_coords with an invalid circle radius."""
        circle = self._create_test_circle(1, 50, 50)
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}
        self.app.circle_radius = -10  # Invalid radius

        result = self.app.get_circle_at_coords(50, 50)
        self.assertIsNone(result)  # Should not find any circle
