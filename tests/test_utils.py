"""
Test utilities for the 4colour project tests.

This module contains common utilities and setup code for tests.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import tkinter as tk
import sys
import os
import math

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app_enums import ApplicationMode

class BaseTestCase(unittest.TestCase):
    """Base test case with common utilities but no application dependencies."""
    
    def _create_click_event(self, x, y, button=1, release=False):
        """Create a mock click event with the specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button (1=left, 3=right)
            release: Whether this is a button release event
            
        Returns:
            Mock event object
        """
        event = Mock()
        event.x = x
        event.y = y
        event.num = button
        return event
        
    def _create_key_event(self, key):
        """Create a mock key press event.
        
        Args:
            key: Key character
            
        Returns:
            Mock event object
        """
        event = Mock()
        event.char = key
        return event
    
    def _create_test_circle(self, circle_id, x, y, priority=1, connections=None):
        """Helper to create a test circle with specified parameters.
        
        Args:
            circle_id: ID for the circle
            x: X coordinate
            y: Y coordinate
            priority: Color priority (1-4)
            connections: List of connected circle IDs
            
        Returns:
            Dictionary with circle data
        """
        if connections is None:
            connections = []
            
        canvas_id = 100 + circle_id
        
        circle = {
            "id": circle_id,
            "canvas_id": canvas_id,
            "x": x,
            "y": y,
            "color_priority": priority,
            "connected_to": connections.copy(),
            "ordered_connections": connections.copy(),  # Initialize with same values as connections
            "enclosed": False,  # Default to not enclosed
            "fixed": False      # Default to not a fixed node
        }
        
        return circle
    
    def _create_fixed_test_circle(self, circle_id, x, y, priority=1, connections=None):
        """Helper to create a fixed test circle.
        
        Args:
            circle_id: ID for the circle (typically a negative value)
            x: X coordinate
            y: Y coordinate
            priority: Color priority (1-4)
            connections: List of connected circle IDs
            
        Returns:
            Dictionary with circle data marked as fixed
        """
        circle = self._create_test_circle(circle_id, x, y, priority, connections)
        circle["fixed"] = True
        return circle
    
    def _calculate_angle_between_points(self, x1, y1, x2, y2):
        """Calculate the angle between two points (clockwise from North).
        
        Args:
            x1: X coordinate of first point
            y1: Y coordinate of first point
            x2: X coordinate of second point
            y2: Y coordinate of second point
            
        Returns:
            float: Angle in degrees (0-360, clockwise from North)
        """
        dx = x2 - x1
        dy = y2 - y1
        
        # Calculate angle with correction for inverted y-axis
        angle_rad = math.atan2(dx, -dy)
        angle_deg = math.degrees(angle_rad)
        
        # Normalize to 0-360 range
        return (angle_deg) % 360

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
        
        # Mock the canvas for testing WITHOUT spec
        self.app.canvas = MagicMock()  # Removed spec=tk.Canvas which causes the error
        
        # Mock the debug button
        self.app.debug_button = MagicMock()
        
        # Initialize custom fields for tracking fixed nodes
        self._setup_fixed_node_constants()
    
    def _setup_fixed_node_constants(self):
        """Set up fixed node constants to match the main application."""
        self.app.FIXED_NODE_A_ID = -1
        self.app.FIXED_NODE_B_ID = -2
        self.app.FIXED_NODE_A_POS = (15, 60)
        self.app.FIXED_NODE_B_POS = (60, 15)
        self.app.PROXIMITY_LIMIT = 75
    
    def _setup_fixed_nodes(self):
        """Setup the fixed nodes A and B required by the boundary manager."""
        # Create fixed node A (yellow)
        fixed_node_a = self._create_fixed_test_circle(
            self.app.FIXED_NODE_A_ID, 
            self.app.FIXED_NODE_A_POS[0], 
            self.app.FIXED_NODE_A_POS[1],
            priority=1
        )
        
        # Create fixed node B (green)
        fixed_node_b = self._create_fixed_test_circle(
            self.app.FIXED_NODE_B_ID, 
            self.app.FIXED_NODE_B_POS[0], 
            self.app.FIXED_NODE_B_POS[1],
            priority=2
        )
        
        # Connect the fixed nodes to each other
        fixed_node_a["connected_to"] = [self.app.FIXED_NODE_B_ID]
        fixed_node_b["connected_to"] = [self.app.FIXED_NODE_A_ID]
        fixed_node_a["ordered_connections"] = [self.app.FIXED_NODE_B_ID]
        fixed_node_b["ordered_connections"] = [self.app.FIXED_NODE_A_ID]
        
        # Add to app structures
        self.app.circles = [fixed_node_a, fixed_node_b]
        self.app.circle_lookup = {
            self.app.FIXED_NODE_A_ID: fixed_node_a,
            self.app.FIXED_NODE_B_ID: fixed_node_b
        }
        
        # Create connection between fixed nodes
        connection_key = f"{self.app.FIXED_NODE_A_ID}_{self.app.FIXED_NODE_B_ID}"
        self.app.connections[connection_key] = {
            "line_id": 999,  # Mock line ID
            "from_circle": self.app.FIXED_NODE_A_ID,
            "to_circle": self.app.FIXED_NODE_B_ID,
            "curve_X": 0,
            "curve_Y": 0,
            "fixed": True
        }
    
    def _setup_graph_with_enclosure(self, center_enclosed=True):
        """Setup a graph with potentially enclosed nodes.
        
        Creates a triangular outer boundary with a center node that can
        be configured as enclosed or not.
        
        Args:
            center_enclosed: Whether the center node should be enclosed
                            (True = connected to all outer nodes, False = linear chain)
        """
        # Ensure fixed nodes exist
        self._setup_fixed_nodes()
        
        # Create triangle corners
        c1 = self._create_test_circle(1, 200, 50)   # Top
        c2 = self._create_test_circle(2, 150, 200)  # Bottom-left
        c3 = self._create_test_circle(3, 250, 200)  # Bottom-right
        
        # Add to lookup
        self.app.circles.extend([c1, c2, c3])
        self.app.circle_lookup.update({
            1: c1,
            2: c2,
            3: c3
        })
        
        # Connect outer triangle edges
        self._add_test_connection(1, 2)
        self._add_test_connection(2, 3)
        self._add_test_connection(3, 1)
        
        # Create center node
        center = self._create_test_circle(4, 200, 120)
        self.app.circles.append(center)
        self.app.circle_lookup[4] = center
        
        if center_enclosed:
            # Connect center to all corners for enclosure
            self._add_test_connection(4, 1)
            self._add_test_connection(4, 2)
            self._add_test_connection(4, 3)
        else:
            # Just connect center to one corner for a linear chain
            self._add_test_connection(4, 1)
        
        # Establish ordered_connections based on angles
        self._update_test_ordered_connections()
    
    def _add_test_connection(self, from_id, to_id):
        """Add a test connection between two circles.
        
        Args:
            from_id: ID of the source circle
            to_id: ID of the target circle
        """
        # Update connected_to lists
        from_circle = self.app.circle_lookup[from_id]
        to_circle = self.app.circle_lookup[to_id]
        
        from_circle["connected_to"].append(to_id)
        to_circle["connected_to"].append(from_id)
        
        # Add to connections dictionary
        connection_key = f"{min(from_id, to_id)}_{max(from_id, to_id)}"
        self.app.connections[connection_key] = {
            "line_id": 1000 + len(self.app.connections),
            "from_circle": min(from_id, to_id),
            "to_circle": max(from_id, to_id),
            "curve_X": 0,
            "curve_Y": 0
        }
    
    def _update_test_ordered_connections(self):
        """Update ordered_connections lists for all circles based on angles."""
        # For each circle, sort its connections by angle clockwise
        for circle_id, circle in self.app.circle_lookup.items():
            angles = {}
            for neighbor_id in circle["connected_to"]:
                neighbor = self.app.circle_lookup[neighbor_id]
                angle = self._calculate_angle_between_points(
                    circle["x"], circle["y"],
                    neighbor["x"], neighbor["y"]
                )
                angles[neighbor_id] = angle
            
            # Sort connected nodes by ascending angle
            circle["ordered_connections"] = sorted(
                circle["connected_to"],
                key=lambda n: angles[n]
            )
    
    def _simulate_boundary_traversal(self):
        """Simulate the boundary traversal algorithm to update enclosure status."""
        # Import here to avoid circular imports
        from boundary_manager import BoundaryManager
        
        # Create a temporary boundary manager
        boundary_manager = BoundaryManager(self.app)
        
        # Update enclosure status
        with patch.object(boundary_manager, '_calculate_corrected_angle') as mock_angle:
            # Use a side effect to return angles based on our angles dictionary
            def angle_side_effect(circle, neighbor_id):
                return self._calculate_angle_between_points(
                    circle["x"], circle["y"],
                    self.app.circle_lookup[neighbor_id]["x"], 
                    self.app.circle_lookup[neighbor_id]["y"]
                )
            
            mock_angle.side_effect = angle_side_effect
            
            # Run the boundary traversal
            boundary_manager.update_enclosure_status()
        
        # Return a dictionary of circle IDs to enclosed status for verification
        return {cid: circle["enclosed"] for cid, circle in self.app.circle_lookup.items()}
        
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
    
    def test_create_fixed_test_circle(self):
        """Test creation of fixed test circles."""
        base_test = BaseTestCase()
        fixed_circle = base_test._create_fixed_test_circle(-1, 15, 60)
        self.assertTrue(fixed_circle["fixed"])
        self.assertEqual(fixed_circle["id"], -1)
        self.assertEqual(fixed_circle["x"], 15)
        self.assertEqual(fixed_circle["y"], 60)
    
    def test_calculate_angle_between_points(self):
        """Test angle calculation between points."""
        base_test = BaseTestCase()
        # North
        self.assertAlmostEqual(base_test._calculate_angle_between_points(
            100, 100, 100, 0), 0.0, places=1)
        # East
        self.assertAlmostEqual(base_test._calculate_angle_between_points(
            100, 100, 200, 100), 90.0, places=1)
        # South
        self.assertAlmostEqual(base_test._calculate_angle_between_points(
            100, 100, 100, 200), 180.0, places=1)
        # West
        self.assertAlmostEqual(base_test._calculate_angle_between_points(
            100, 100, 0, 100), 270.0, places=1)

if __name__ == "__main__":
    unittest.main()
