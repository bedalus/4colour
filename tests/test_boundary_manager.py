"""
Unit tests for boundary_manager.py.
"""

import sys
import os
# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from unittest.mock import patch, MagicMock
from test_utils import MockAppTestCase
from app_enums import ApplicationMode
from boundary_manager import BoundaryManager

class TestBoundaryManager(MockAppTestCase):
    """Test cases for the BoundaryManager class."""
    
    def setUp(self):
        """Set up test environment with mocked app instance."""
        super().setUp()
        # Ensure BoundaryManager is properly initialized with the mock app
        self.boundary_manager = BoundaryManager(self.app)
        self.app.boundary_manager = self.boundary_manager
        
    def _setup_triangle(self):
        """Sets up a simple triangle graph."""
        c1 = self._create_test_circle(1, 100, 50) # Top
        c2 = self._create_test_circle(2, 50, 150)  # Bottom-left
        c3 = self._create_test_circle(3, 150, 150) # Bottom-right
        self.app.circles = [c1, c2, c3]
        self.app.circle_lookup = {c["id"]: c for c in self.app.circles}
        
        # Add connections (ensures ordered_connections are updated)
        self.app.connection_manager.add_connection(1, 2)
        self.app.connection_manager.add_connection(1, 3)
        self.app.connection_manager.add_connection(2, 3)

    def _setup_square(self):
        """Sets up a simple square graph."""
        c1 = self._create_test_circle(1, 50, 50)   # Top-left
        c2 = self._create_test_circle(2, 150, 50)  # Top-right
        c3 = self._create_test_circle(3, 150, 150) # Bottom-right
        c4 = self._create_test_circle(4, 50, 150)  # Bottom-left
        self.app.circles = [c1, c2, c3, c4]
        self.app.circle_lookup = {c["id"]: c for c in self.app.circles}

        self.app.connection_manager.add_connection(1, 2)
        self.app.connection_manager.add_connection(2, 3)
        self.app.connection_manager.add_connection(3, 4)
        self.app.connection_manager.add_connection(4, 1)

    def _setup_triangle_with_center(self):
        """Sets up a triangle with one circle inside."""
        self._setup_triangle() # Start with the outer triangle
        c4 = self._create_test_circle(4, 100, 100) # Center
        self.app.circles.append(c4)
        self.app.circle_lookup[4] = c4

        # Connect center to all outer points
        self.app.connection_manager.add_connection(4, 1)
        self.app.connection_manager.add_connection(4, 2)
        self.app.connection_manager.add_connection(4, 3)

    def test_enclosure_empty_graph(self):
        """Test enclosure status with no circles."""
        self.app.circles = []
        self.app.circle_lookup = {}
        self.app.boundary_manager.update_enclosure_status()
        # No assertions needed, just ensure it runs without error

    def test_enclosure_single_circle(self):
        """Test enclosure status with one circle."""
        c1 = self._create_test_circle(1, 50, 50)
        self.app.circles = [c1]
        self.app.circle_lookup = {1: c1}
        self.app.boundary_manager.update_enclosure_status()
        self.assertFalse(self.app.circle_lookup[1]['enclosed'])

    def test_enclosure_two_connected_circles(self):
        """Test enclosure status with two connected circles."""
        c1 = self._create_test_circle(1, 50, 50)
        c2 = self._create_test_circle(2, 150, 50)
        self.app.circles = [c1, c2]
        self.app.circle_lookup = {1: c1, 2: c2}
        
        # Mock the add_connection method to update connections properly
        with patch.object(self.app.connection_manager, 'add_connection') as mock_add:
            def side_effect(from_id, to_id):
                # Update connected_to lists
                self.app.circle_lookup[from_id]["connected_to"].append(to_id)
                self.app.circle_lookup[to_id]["connected_to"].append(from_id)
                # Update ordered_connections lists (simplified version for test)
                self.app.circle_lookup[from_id]["ordered_connections"] = [to_id]
                self.app.circle_lookup[to_id]["ordered_connections"] = [from_id]
                return True
            mock_add.side_effect = side_effect
            
            self.app.connection_manager.add_connection(1, 2)

        self.app.boundary_manager.update_enclosure_status()
        self.assertFalse(self.app.circle_lookup[1]['enclosed'])
        self.assertFalse(self.app.circle_lookup[2]['enclosed'])

    def test_enclosure_triangle(self):
        """Test enclosure status for a triangle (all outer)."""
        # Setup triangle
        c1 = self._create_test_circle(1, 100, 50) # Top
        c2 = self._create_test_circle(2, 50, 150)  # Bottom-left
        c3 = self._create_test_circle(3, 150, 150) # Bottom-right
        self.app.circles = [c1, c2, c3]
        self.app.circle_lookup = {c["id"]: c for c in self.app.circles}
        
        # Mock connection methods
        with patch.object(self.app.connection_manager, 'add_connection') as mock_add:
            def side_effect(from_id, to_id):
                # Update connected_to lists
                self.app.circle_lookup[from_id]["connected_to"].append(to_id)
                self.app.circle_lookup[to_id]["connected_to"].append(from_id)
                return True
            mock_add.side_effect = side_effect
            
            # Add connections
            self.app.connection_manager.add_connection(1, 2)
            self.app.connection_manager.add_connection(2, 3)
            self.app.connection_manager.add_connection(3, 1)
            
        # Mock ordered_connections to simulate clockwise ordering
        self.app.circle_lookup[1]["ordered_connections"] = [3, 2]
        self.app.circle_lookup[2]["ordered_connections"] = [1, 3]
        self.app.circle_lookup[3]["ordered_connections"] = [2, 1]
        
        # Mock the get_connection_curve_offset method
        with patch.object(self.app.connection_manager, 'get_connection_curve_offset', return_value=(0, 0)):
            # Test enclosure status update
            self.app.boundary_manager.update_enclosure_status()

        # All nodes should be on boundary (not enclosed)
        self.assertFalse(self.app.circle_lookup[1]['enclosed'], "Circle 1 should not be enclosed")
        self.assertFalse(self.app.circle_lookup[2]['enclosed'], "Circle 2 should not be enclosed")
        self.assertFalse(self.app.circle_lookup[3]['enclosed'], "Circle 3 should not be enclosed")

    def test_enclosure_triangle_with_center(self):
        """Test enclosure status for a triangle with an enclosed center."""
        # Setup triangle
        c1 = self._create_test_circle(1, 100, 50) # Top
        c2 = self._create_test_circle(2, 50, 150)  # Bottom-left
        c3 = self._create_test_circle(3, 150, 150) # Bottom-right
        c4 = self._create_test_circle(4, 100, 100) # Center
        self.app.circles = [c1, c2, c3, c4]
        self.app.circle_lookup = {c["id"]: c for c in self.app.circles}
        
        # Mock connection methods
        with patch.object(self.app.connection_manager, 'add_connection') as mock_add:
            def side_effect(from_id, to_id):
                # Update connected_to lists
                self.app.circle_lookup[from_id]["connected_to"].append(to_id)
                self.app.circle_lookup[to_id]["connected_to"].append(from_id)
                return True
            mock_add.side_effect = side_effect
            
            # Add connections - outer triangle
            self.app.connection_manager.add_connection(1, 2)
            self.app.connection_manager.add_connection(2, 3)
            self.app.connection_manager.add_connection(3, 1)
            
            # Connect center to all points
            self.app.connection_manager.add_connection(4, 1)
            self.app.connection_manager.add_connection(4, 2)
            self.app.connection_manager.add_connection(4, 3)
            
        # Mock ordered_connections to simulate clockwise ordering
        self.app.circle_lookup[1]["ordered_connections"] = [3, 4, 2]
        self.app.circle_lookup[2]["ordered_connections"] = [1, 4, 3]
        self.app.circle_lookup[3]["ordered_connections"] = [2, 4, 1]
        self.app.circle_lookup[4]["ordered_connections"] = [1, 3, 2]
        
        # Mock the get_connection_curve_offset method
        with patch.object(self.app.connection_manager, 'get_connection_curve_offset', return_value=(0, 0)):
            # Test enclosure status update
            self.app.boundary_manager.update_enclosure_status()

        # Outer triangle nodes should not be enclosed
        self.assertFalse(self.app.circle_lookup[1]['enclosed'], "Outer Circle 1 should not be enclosed")
        self.assertFalse(self.app.circle_lookup[2]['enclosed'], "Outer Circle 2 should not be enclosed")
        self.assertFalse(self.app.circle_lookup[3]['enclosed'], "Outer Circle 3 should not be enclosed")
        # Center node should be enclosed
        self.assertTrue(self.app.circle_lookup[4]['enclosed'], "Center Circle 4 should be enclosed")

    def test_boundary_traversal_with_reused_edges(self):
        """Test that boundary traversal correctly handles edges that appear twice in the boundary."""
        # Create a mock setup where the fixed nodes are already defined
        self.app.FIXED_NODE_A_ID = -1
        self.app.FIXED_NODE_B_ID = -2
        
        # Create the fixed nodes
        fixed_node_a = self._create_test_circle(self.app.FIXED_NODE_A_ID, 15, 60)
        fixed_node_b = self._create_test_circle(self.app.FIXED_NODE_B_ID, 60, 15)
        
        # Set them as fixed
        fixed_node_a["fixed"] = True
        fixed_node_b["fixed"] = True
        
        # Add the fixed nodes to the lookup and circles list
        self.app.circles = [fixed_node_a, fixed_node_b]
        self.app.circle_lookup = {
            self.app.FIXED_NODE_A_ID: fixed_node_a,
            self.app.FIXED_NODE_B_ID: fixed_node_b
        }
        
        # Connect the fixed nodes
        fixed_node_a["connected_to"] = [self.app.FIXED_NODE_B_ID]
        fixed_node_b["connected_to"] = [self.app.FIXED_NODE_A_ID]
        fixed_node_a["ordered_connections"] = [self.app.FIXED_NODE_B_ID]
        fixed_node_b["ordered_connections"] = [self.app.FIXED_NODE_A_ID]
        
        # Add node C connected to both fixed nodes
        node_c = self._create_test_circle(1, 100, 100)
        self.app.circles.append(node_c)
        self.app.circle_lookup[1] = node_c
        
        # Connect node C to both fixed nodes
        node_c["connected_to"] = [self.app.FIXED_NODE_A_ID, self.app.FIXED_NODE_B_ID]
        node_c["ordered_connections"] = [self.app.FIXED_NODE_A_ID, self.app.FIXED_NODE_B_ID]
        fixed_node_a["connected_to"].append(1)
        fixed_node_a["ordered_connections"].append(1)
        fixed_node_b["connected_to"].append(1)
        fixed_node_b["ordered_connections"].append(1)
        
        # Add node D connected only to node C
        node_d = self._create_test_circle(2, 150, 150)
        self.app.circles.append(node_d)
        self.app.circle_lookup[2] = node_d
        
        # Connect node D to node C
        node_d["connected_to"] = [1]
        node_d["ordered_connections"] = [1]
        node_c["connected_to"].append(2)
        
        # Update ordered_connections for node C to include node D
        # Order: Fixed A, Fixed B, Node D
        node_c["ordered_connections"] = [self.app.FIXED_NODE_A_ID, self.app.FIXED_NODE_B_ID, 2]
        
        # Mock the get_connection_curve_offset method
        with patch.object(self.app.connection_manager, 'get_connection_curve_offset', return_value=(0, 0)):
            # Need to mock the _calculate_corrected_angle in the BoundaryManager since we can't use it directly
            with patch.object(self.boundary_manager, '_calculate_corrected_angle') as mock_angle:
                # Set up angle returns based on the node sequence we want
                def angle_side_effect(circle, neighbor_id):
                    if circle['id'] == self.app.FIXED_NODE_A_ID:
                        # Fixed A -> Fixed B: 0 degrees, Fixed A -> C: 45 degrees
                        return 0 if neighbor_id == self.app.FIXED_NODE_B_ID else 45
                    elif circle['id'] == self.app.FIXED_NODE_B_ID:
                        # Fixed B -> Fixed A: 180 degrees, Fixed B -> C: 135 degrees
                        return 180 if neighbor_id == self.app.FIXED_NODE_A_ID else 135
                    elif circle['id'] == 1:  # Node C
                        # C -> Fixed A: 225 degrees, C -> Fixed B: 315 degrees, C -> D: 90 degrees
                        if neighbor_id == self.app.FIXED_NODE_A_ID:
                            return 225
                        elif neighbor_id == self.app.FIXED_NODE_B_ID:
                            return 315
                        else:
                            return 90
                    elif circle['id'] == 2:  # Node D
                        # D -> C: 270 degrees
                        return 270
                    return 0
                    
                mock_angle.side_effect = angle_side_effect
                
                # Run the boundary traversal
                with patch('builtins.print') as mock_print:
                    self.boundary_manager.update_enclosure_status()
                    
                    # Verify no "revisited node unexpectedly" warnings were printed
                    unexpected_visit_calls = [
                        call for call in mock_print.call_args_list 
                        if "revisited node" in str(call) and "unexpectedly" in str(call)
                    ]
                    self.assertEqual(len(unexpected_visit_calls), 0, 
                                    "Boundary traversal reported unexpected node revisit")
        
        # All nodes should be correctly identified as boundary nodes (not enclosed)
        for node_id in [self.app.FIXED_NODE_A_ID, self.app.FIXED_NODE_B_ID, 1, 2]:
            node = self.app.circle_lookup[node_id]
            self.assertFalse(node['enclosed'], f"Node {node_id} should be on boundary")

    def test_calculate_corrected_angle(self):
        """Test the angle calculation between two circles."""
        # Create circles at specific positions for predictable angles
        circle1 = self._create_test_circle(1, 100, 100)  # Center
        circle2 = self._create_test_circle(2, 100, 0)    # North (0 degrees)
        circle3 = self._create_test_circle(3, 200, 100)  # East (90 degrees)
        circle4 = self._create_test_circle(4, 100, 200)  # South (180 degrees)
        circle5 = self._create_test_circle(5, 0, 100)    # West (270 degrees)
        
        # Add circles to lookup
        self.app.circle_lookup = {
            1: circle1,
            2: circle2,
            3: circle3,
            4: circle4,
            5: circle5
        }
        
        # Mock the connection manager's get_connection_curve_offset method
        with patch.object(self.app.connection_manager, 'get_connection_curve_offset', return_value=(0, 0)):
            # Test angles from center to each direction
            north_angle = self.boundary_manager._calculate_corrected_angle(circle1, 2)
            east_angle = self.boundary_manager._calculate_corrected_angle(circle1, 3)
            south_angle = self.boundary_manager._calculate_corrected_angle(circle1, 4)
            west_angle = self.boundary_manager._calculate_corrected_angle(circle1, 5)
            
            # Check angles (allow small floating point errors)
            self.assertAlmostEqual(north_angle, 0, places=1)
            self.assertAlmostEqual(east_angle, 90, places=1)
            self.assertAlmostEqual(south_angle, 180, places=1)
            self.assertAlmostEqual(west_angle, 270, places=1)
            
            # Test with curve offsets
            with patch.object(self.app.connection_manager, 'get_connection_curve_offset', return_value=(50, 50)):
                # With offset, the angle should change
                offset_angle = self.boundary_manager._calculate_corrected_angle(circle1, 2)
                # The angle should now be affected by the curve offset
                self.assertNotAlmostEqual(offset_angle, 0, places=1)