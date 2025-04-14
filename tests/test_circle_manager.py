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
    
    def test_get_circle_at_coords_multiple_overlapping(self):
        """Test finding the topmost circle when multiple circles overlap."""
        circle1 = self._create_test_circle(1, 50, 50)
        circle2 = self._create_test_circle(2, 55, 55)  # Overlapping circle
        self.app.circles = [circle1, circle2]
        self.app.circle_lookup = {1: circle1, 2: circle2}
        self.app.circle_radius = 10

        result = self.app.get_circle_at_coords(55, 55)  # Inside both circles
        self.assertEqual(result, 2)  # Topmost circle should be returned

    def test_remove_circle_by_id_with_multiple_connections(self):
        """Test removing a circle with multiple connections."""
        circle1 = self._create_test_circle(1, 50, 50, connections=[2, 3])
        circle2 = self._create_test_circle(2, 100, 50, connections=[1])
        circle3 = self._create_test_circle(3, 50, 100, connections=[1])

        self.app.circles = [circle1, circle2, circle3]
        self.app.circle_lookup = {1: circle1, 2: circle2, 3: circle3}

        # Create connections
        self.app.connections = {
            "1_2": {"line_id": 201, "from_circle": 1, "to_circle": 2},
            "1_3": {"line_id": 202, "from_circle": 1, "to_circle": 3}
        }

        # Mock remove_circle_connections
        with patch.object(self.app, '_remove_circle_connections') as mock_remove_connections:
            result = self.app._remove_circle_by_id(1)

            self.assertTrue(result)
            mock_remove_connections.assert_called_once_with(1)
            self.app.canvas.delete.assert_any_call(201)
            self.app.canvas.delete.assert_any_call(202)
            self.assertEqual(len(self.app.circles), 2)
            self.assertNotIn(1, self.app.circle_lookup)

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

    def test_remove_circle_by_id_complex_graph(self):
        """Test removing a circle that is part of a complex graph."""
        circle1 = self._create_test_circle(1, 50, 50, connections=[2, 3, 4])
        circle2 = self._create_test_circle(2, 100, 50, connections=[1])
        circle3 = self._create_test_circle(3, 50, 100, connections=[1])
        circle4 = self._create_test_circle(4, 100, 100, connections=[1])

        self.app.circles = [circle1, circle2, circle3, circle4]
        self.app.circle_lookup = {1: circle1, 2: circle2, 3: circle3, 4: circle4}

        # Create connections
        self.app.connections = {
            "1_2": {"line_id": 201, "from_circle": 1, "to_circle": 2},
            "1_3": {"line_id": 202, "from_circle": 1, "to_circle": 3},
            "1_4": {"line_id": 203, "from_circle": 1, "to_circle": 4}
        }

        # Mock remove_circle_connections
        with patch.object(self.app, '_remove_circle_connections') as mock_remove_connections:
            result = self.app._remove_circle_by_id(1)

            self.assertTrue(result)
            mock_remove_connections.assert_called_once_with(1)
            self.app.canvas.delete.assert_any_call(201)
            self.app.canvas.delete.assert_any_call(202)
            self.app.canvas.delete.assert_any_call(203)
            self.assertEqual(len(self.app.circles), 3)
            self.assertNotIn(1, self.app.circle_lookup)

    def test_get_circle_at_coords_boundary_overlap(self):
        """Test get_circle_at_coords with coordinates on the boundary of overlapping circles."""
        circle1 = self._create_test_circle(1, 50, 50)
        circle2 = self._create_test_circle(2, 60, 50)  # Overlapping boundary
        self.app.circles = [circle1, circle2]
        self.app.circle_lookup = {1: circle1, 2: circle2}
        self.app.circle_radius = 10

        result = self.app.get_circle_at_coords(60, 50)  # On the boundary of both circles
        self.assertEqual(result, 2)  # Topmost circle should be returned

    def test_get_circle_at_coords_negative_coords(self):
        """Test get_circle_at_coords with negative coordinates."""
        circle = self._create_test_circle(1, 50, 50)
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}
        self.app.circle_radius = 10

        result = self.app.get_circle_at_coords(-10, -10)  # Negative coordinates
        self.assertIsNone(result)

    def test_remove_circle_by_id_no_connections(self):
        """Test removing a circle that has no connections."""
        circle = self._create_test_circle(1, 50, 50)
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}

        # Mock remove_circle_connections
        with patch.object(self.app, '_remove_circle_connections') as mock_remove_connections:
            result = self.app._remove_circle_by_id(1)

            self.assertTrue(result)
            mock_remove_connections.assert_not_called()  # No connections to remove
            self.app.canvas.delete.assert_called_once_with(101)
            self.assertEqual(len(self.app.circles), 0)
            self.assertNotIn(1, self.app.circle_lookup)

    def test_get_circle_at_coords_invalid_radius(self):
        """Test get_circle_at_coords with an invalid circle radius."""
        circle = self._create_test_circle(1, 50, 50)
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}
        self.app.circle_radius = -10  # Invalid radius

        result = self.app.get_circle_at_coords(50, 50)
        self.assertIsNone(result)  # Should not find any circle

    def test_remove_circle_by_id_dynamic_removal(self):
        """Test removing circles dynamically in a complex graph."""
        # Create a graph with multiple circles and connections
        circles = [
            self._create_test_circle(1, 50, 50, connections=[2, 3]),
            self._create_test_circle(2, 100, 50, connections=[1, 3]),
            self._create_test_circle(3, 150, 50, connections=[1, 2])
        ]

        self.app.circles = circles
        self.app.circle_lookup = {c["id"]: c for c in circles}

        # Add connections
        self.app.connections = {
            "1_2": {"line_id": 1012, "from_circle": 1, "to_circle": 2},
            "1_3": {"line_id": 1013, "from_circle": 1, "to_circle": 3},
            "2_3": {"line_id": 1023, "from_circle": 2, "to_circle": 3}
        }

        # Remove circle 1 dynamically
        with patch.object(self.app, '_remove_circle_connections') as mock_remove_connections:
            result = self.app._remove_circle_by_id(1)

            self.assertTrue(result)
            mock_remove_connections.assert_called_once_with(1)
            self.app.canvas.delete.assert_any_call(1012)
            self.app.canvas.delete.assert_any_call(1013)
            self.assertEqual(len(self.app.circles), 2)
            self.assertNotIn(1, self.app.circle_lookup)

        # Verify remaining connections
        self.assertNotIn("1_2", self.app.connections)
        self.assertNotIn("1_3", self.app.connections)
        self.assertIn("2_3", self.app.connections)
