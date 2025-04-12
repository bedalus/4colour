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
    
    def test_get_circle_at_coords_found(self):
        """Test finding a circle at given coordinates."""
        # Use the interaction handler to create the circle to ensure 'enclosed' is present
        event = self._create_click_event(50, 50)
        with patch.object(self.app, '_assign_color_based_on_connections', return_value=1):
            self.app.interaction_handler.draw_on_click(event)
            
        self.app.circle_radius = 10
        
        result = self.app.get_circle_at_coords(55, 55)  # Inside the circle
        self.assertEqual(result, 1) # Assumes first circle has ID 1
        
    def test_get_circle_at_coords_not_found(self):
        """Test not finding a circle at given coordinates."""
        # Use the interaction handler to create the circle
        event = self._create_click_event(50, 50)
        with patch.object(self.app, '_assign_color_based_on_connections', return_value=1):
            self.app.interaction_handler.draw_on_click(event)
            
        self.app.circle_radius = 10
        
        result = self.app.get_circle_at_coords(100, 100)  # Outside the circle
        self.assertIsNone(result)
    
    def test_remove_circle(self):
        """Test removing a circle with right-click in edit mode."""
        first_circle = self._create_test_circle(1, 50, 50, connections=[2])
        second_circle = self._create_test_circle(2, 100, 100, connections=[1])
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        self.app._mode = ApplicationMode.ADJUST
        
        # Create a connection
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2
            }
        }
        
        # Mock get_circle_at_coords
        with patch.object(self.app.circle_manager, 'get_circle_at_coords', return_value=1):
            # Mock circle_manager.remove_circle_by_id directly instead of app._remove_circle_by_id
            with patch.object(self.app.circle_manager, 'remove_circle_by_id', return_value=True) as mock_remove_by_id:
                event = self._create_click_event(50, 50)
                self.app._remove_circle(event)
                
                mock_remove_by_id.assert_called_once_with(1)
    
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
    
    def test_create_circle_attributes(self):
        """Test that a newly created circle has the expected default attributes."""
        # Simulate clicking to create a circle using the interaction handler's method
        # We need to mock dependencies of draw_on_click if necessary
        event = self._create_click_event(75, 75)
        
        # Mock color assignment as it's called during creation
        with patch.object(self.app, '_assign_color_based_on_connections', return_value=1):
            self.app.interaction_handler.draw_on_click(event)
            
        # Verify the circle was created and added
        self.assertEqual(len(self.app.circles), 1)
        self.assertEqual(len(self.app.circle_lookup), 1)
        
        # Get the created circle data
        created_circle = self.app.circle_lookup[1] # Assuming next_id starts at 1
        
        # Check for the presence and default value of the 'enclosed' attribute
        self.assertIn("enclosed", created_circle)
        self.assertFalse(created_circle["enclosed"])
        
        # Check other essential attributes for completeness
        self.assertEqual(created_circle["id"], 1)
        self.assertEqual(created_circle["x"], 75)
        self.assertEqual(created_circle["y"], 75)
        self.assertEqual(created_circle["color_priority"], 1)
        self.assertEqual(created_circle["connected_to"], [])
        self.assertEqual(created_circle["ordered_connections"], [])
        self.assertIsNotNone(created_circle["canvas_id"])
