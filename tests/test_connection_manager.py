"""
Unit tests for connection_manager.py.
"""

import sys
import os
# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from unittest.mock import patch
from test_utils import MockAppTestCase
from app_enums import ApplicationMode

class TestConnectionManager(MockAppTestCase):
    """Test cases for the Connection Manager."""
    
    def test_add_connection(self):
        """Test adding a connection between two existing circles."""
        first_circle = self._create_test_circle(1, 50, 50)
        second_circle = self._create_test_circle(2, 150, 150)
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        self.app.canvas.create_line.return_value = 200
        
        # Mock calculate_curve_points
        with patch.object(self.app, '_calculate_curve_points', return_value=[50, 50, 100, 100, 150, 150]):
            result = self.app.add_connection(1, 2)
            
            self.assertTrue(result)
            self.assertIn(2, first_circle["connected_to"])
            self.assertIn(1, second_circle["connected_to"])
            
            self.app.canvas.create_line.assert_called_once()
            args, kwargs = self.app.canvas.create_line.call_args
            self.assertEqual(args[0], [50, 50, 100, 100, 150, 150])
            self.assertEqual(kwargs['width'], 1)
            self.assertEqual(kwargs['smooth'], True)
            self.assertEqual(kwargs['tags'], "line")
            
            self.app.canvas.lower.assert_called_once_with("line")
            
            self.assertIn("1_2", self.app.connections)
            connection = self.app.connections["1_2"]
            self.assertEqual(connection["line_id"], 200)
            self.assertEqual(connection["from_circle"], 1)
            self.assertEqual(connection["to_circle"], 2)
            self.assertEqual(connection["curve_X"], 0)
            self.assertEqual(connection["curve_Y"], 0)
    
    def test_add_connection_nonexistent_circle(self):
        """Test adding a connection with nonexistent circle."""
        first_circle = self._create_test_circle(1, 50, 50)
        self.app.circles = [first_circle]
        self.app.circle_lookup = {1: first_circle}
        
        result = self.app.add_connection(1, 99)
        
        self.assertFalse(result)
        self.app.canvas.create_line.assert_not_called()
        self.assertEqual(first_circle["connected_to"], [])
        self.assertEqual(self.app.connections, {})
    
    def test_remove_circle_connections(self):
        """Test removing all connections for a circle."""
        first_circle = self._create_test_circle(1, 50, 50, connections=[2])
        second_circle = self._create_test_circle(2, 150, 150, connections=[1])
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        self.app.connections = {
            "1_2": {
                "line_id": 200,
                "from_circle": 1,
                "to_circle": 2
            }
        }
        
        self.app._remove_circle_connections(1)
        
        self.app.canvas.delete.assert_called_once_with(200)
        self.assertEqual(len(self.app.connections), 0)
        self.assertEqual(second_circle["connected_to"], [])
    
    def test_remove_circle_connections_with_midpoint_handles(self):
        """Test that removing connections also removes midpoint handles."""
        first_circle = self._create_test_circle(1, 50, 50, connections=[2])
        second_circle = self._create_test_circle(2, 150, 150, connections=[1])
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        self.app.connections = {"1_2": {"line_id": 200, "from_circle": 1, "to_circle": 2}}
        self.app.midpoint_handles = {"1_2": 300}
        
        self.app._remove_circle_connections(1)
        
        self.app.canvas.delete.assert_any_call(200)
        self.app.canvas.delete.assert_any_call(300)
        self.assertEqual(len(self.app.connections), 0)
        self.assertEqual(len(self.app.midpoint_handles), 0)
    
    def test_calculate_midpoint(self):
        """Test calculating the midpoint between two circles."""
        circle1 = {"x": 50, "y": 50}
        circle2 = {"x": 150, "y": 150}
        
        mid_x, mid_y = self.app._calculate_midpoint(circle1, circle2)
        
        self.assertEqual(mid_x, 100)
        self.assertEqual(mid_y, 100)
    
    def test_calculate_curve_points(self):
        """Test calculating points for a curved line."""
        first_circle = self._create_test_circle(1, 50, 50, connections=[2])
        second_circle = self._create_test_circle(2, 150, 150, connections=[1])
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Case 1: No curve offset
        self.app.connections = {
            "1_2": {"line_id": 200, "from_circle": 1, "to_circle": 2, "curve_X": 0, "curve_Y": 0}
        }
        
        points = self.app._calculate_curve_points(1, 2)
        expected = [50, 50, 100, 100, 150, 150]
        self.assertEqual(points, expected)
        
        # Case 2: With curve offset
        self.app.connections["1_2"]["curve_X"] = 20
        self.app.connections["1_2"]["curve_Y"] = -15
        
        points = self.app._calculate_curve_points(1, 2)
        expected = [50, 50, 120, 85, 150, 150]
        self.assertEqual(points, expected)
    
    def test_get_connection_curve_offset(self):
        """Test getting curve offset for a connection."""
        self.app.connections = {
            "1_2": {"line_id": 200, "from_circle": 1, "to_circle": 2, "curve_X": 15, "curve_Y": -10}
        }
        
        # Normal order
        curve_x, curve_y = self.app.get_connection_curve_offset(1, 2)
        self.assertEqual(curve_x, 15)
        self.assertEqual(curve_y, -10)
        
        # Reversed order
        curve_x, curve_y = self.app.get_connection_curve_offset(2, 1)
        self.assertEqual(curve_x, 15)
        self.assertEqual(curve_y, -10)
        
        # Non-existent connection
        curve_x, curve_y = self.app.get_connection_curve_offset(3, 4)
        self.assertEqual(curve_x, 0)
        self.assertEqual(curve_y, 0)
    
    def test_update_connection_curve(self):
        """Test updating curve offset for a connection."""
        first_circle = self._create_test_circle(1, 50, 50, connections=[2])
        second_circle = self._create_test_circle(2, 150, 150, connections=[1])
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        self.app.connections = {
            "1_2": {"line_id": 200, "from_circle": 1, "to_circle": 2, "curve_X": 0, "curve_Y": 0}
        }
        
        # Update to account for the actual curve calculation in the implementation
        with patch.object(self.app, '_calculate_curve_points', return_value=[50, 50, 125.0, 85.0, 150, 150]):
            self.app.canvas.create_line.return_value = 201
            
            result = self.app.update_connection_curve(1, 2, 25, -15)
            
            self.assertTrue(result)
            self.assertEqual(self.app.connections["1_2"]["curve_X"], 25)
            self.assertEqual(self.app.connections["1_2"]["curve_Y"], -15)
            self.app.canvas.delete.assert_called_once_with(200)
            
            self.app.canvas.create_line.assert_called_once()
            args, kwargs = self.app.canvas.create_line.call_args
            self.assertEqual(args[0], [50, 50, 125.0, 85.0, 150, 150])
            self.assertEqual(kwargs['smooth'], True)
    
    def test_midpoint_handle_management(self):
        """Test midpoint handle creation and positioning."""
        # Setup
        self.app._mode = ApplicationMode.ADJUST
        self.app.midpoint_radius = 5
        
        first_circle = self._create_test_circle(1, 50, 50, connections=[2])
        second_circle = self._create_test_circle(2, 150, 150, connections=[1])
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        self.app.connections = {
            "1_2": {"line_id": 200, "from_circle": 1, "to_circle": 2, "curve_X": 10, "curve_Y": -5}
        }
        
        # Test drawing a handle
        self.app.canvas.create_rectangle.return_value = 300
        handle_id = self.app._draw_midpoint_handle("1_2", 100, 100)
        
        self.assertEqual(handle_id, 300)
        self.app.canvas.create_rectangle.assert_called_once()
        args, kwargs = self.app.canvas.create_rectangle.call_args
        self.assertEqual(args, (95, 95, 105, 105))
        self.assertEqual(kwargs['fill'], "black")
        self.assertEqual(kwargs['outline'], "white")
        self.assertEqual(kwargs['tags'], ("midpoint_handle", "1_2"))
        
        # Test calculating handle position - updated the expected values
        with patch.object(self.app, 'get_connection_curve_offset', return_value=(10, -5)):
            with patch.object(self.app, '_calculate_midpoint', return_value=(100, 100)):
                x, y = self.app._calculate_midpoint_handle_position(1, 2)
                self.assertEqual(x, 105.0)  # 100 + 10/2
                self.assertEqual(y, 97.5)   # 100 - 5/2
