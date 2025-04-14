"""
Unit tests for boundary_manager.py.
"""

import sys
import os
# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from unittest.mock import patch, MagicMock, call
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
        
    def _setup_disconnected_components(self):
        """Sets up a graph with two disconnected components."""
        # Component 1: A simple triangle
        c1 = self._create_test_circle(1, 50, 50)
        c2 = self._create_test_circle(2, 100, 50)
        c3 = self._create_test_circle(3, 75, 100)
        
        # Component 2: A separate pair
        c4 = self._create_test_circle(4, 200, 50)
        c5 = self._create_test_circle(5, 250, 50)
        
        self.app.circles = [c1, c2, c3, c4, c5]
        self.app.circle_lookup = {c["id"]: c for c in self.app.circles}
        
        # Connect triangle
        self.app.connection_manager.add_connection(1, 2)
        self.app.connection_manager.add_connection(2, 3)
        self.app.connection_manager.add_connection(3, 1)
        
        # Connect pair
        self.app.connection_manager.add_connection(4, 5)
        
    def _setup_linear_chain(self):
        """Sets up a linear chain of circles (no enclosure)."""
        c1 = self._create_test_circle(1, 50, 100)
        c2 = self._create_test_circle(2, 100, 100)
        c3 = self._create_test_circle(3, 150, 100)
        c4 = self._create_test_circle(4, 200, 100)
        
        self.app.circles = [c1, c2, c3, c4]
        self.app.circle_lookup = {c["id"]: c for c in self.app.circles}
        
        # Connect in a chain
        self.app.connection_manager.add_connection(1, 2)
        self.app.connection_manager.add_connection(2, 3)
        self.app.connection_manager.add_connection(3, 4)

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

    def test_boundary_traversal_with_disconnected_components(self):
        """Test boundary traversal with disconnected graph components."""
        self._setup_disconnected_components()
        
        # Mock the connection angle calculation for predictable traversal
        with patch.object(self.app.boundary_manager, '_calculate_corrected_angle') as mock_angle:
            # Define angles for component 1 (triangle)
            def angle_side_effect(circle, neighbor_id):
                # Just ensure we have predictable clockwise ordering
                source_id = circle['id']
                if source_id == 1:
                    return 0 if neighbor_id == 2 else 180
                elif source_id == 2:
                    return 90 if neighbor_id == 3 else 270
                elif source_id == 3:
                    return 45 if neighbor_id == 1 else 225
                elif source_id == 4:
                    return 0 if neighbor_id == 5 else 180
                elif source_id == 5:
                    return 0 if neighbor_id == 4 else 180
                return 0
                
            mock_angle.side_effect = angle_side_effect
            
            # Execute update with print mocking to catch warnings
            with patch('builtins.print') as mock_print:
                self.app.boundary_manager.update_enclosure_status()
        
        # All nodes should be correctly marked as not enclosed
        for node_id in range(1, 6):
            node = self.app.circle_lookup[node_id]
            self.assertFalse(node['enclosed'], f"Node {node_id} should be on boundary")
            
    def test_boundary_traversal_with_linear_chain(self):
        """Test boundary traversal with a linear chain graph (no enclosure)."""
        self._setup_linear_chain()
        
        # Mock angle calculations for consistent ordering
        with patch.object(self.app.boundary_manager, '_calculate_corrected_angle') as mock_angle:
            mock_angle.return_value = 0  # Any consistent value is fine for a chain
            
            # Update enclosure status
            self.app.boundary_manager.update_enclosure_status()
            
        # All nodes should be on boundary
        for node_id in range(1, 5):
            node = self.app.circle_lookup[node_id]
            self.assertFalse(node['enclosed'], f"Node {node_id} in chain should be on boundary")
            
    def test_ordered_connections_impact_on_traversal(self):
        """Test how ordered connections impact the boundary traversal."""
        # Create a simple square
        c1 = self._create_test_circle(1, 0, 0)   # Top-left
        c2 = self._create_test_circle(2, 100, 0)  # Top-right
        c3 = self._create_test_circle(3, 100, 100) # Bottom-right
        c4 = self._create_test_circle(4, 0, 100)  # Bottom-left
        c5 = self._create_test_circle(5, 50, 50)   # Center
        
        self.app.circles = [c1, c2, c3, c4, c5]
        self.app.circle_lookup = {c["id"]: c for c in self.app.circles}
        
        # Setup connections for a square with center connected to all corners
        for i in range(1, 5):
            # Connect to adjacent corners in the square
            next_id = i + 1 if i < 4 else 1
            self.app.circle_lookup[i]["connected_to"] = [next_id, 5]
            self.app.circle_lookup[5]["connected_to"].append(i)
            
            # Connect to previous corner (to close the square)
            if i == 1:
                self.app.circle_lookup[i]["connected_to"].append(4)
                
        # Set ordered connections in a way that would affect traversal
        # Clockwise ordering
        self.app.circle_lookup[1]["ordered_connections"] = [4, 5, 2]
        self.app.circle_lookup[2]["ordered_connections"] = [1, 5, 3]
        self.app.circle_lookup[3]["ordered_connections"] = [2, 5, 4]
        self.app.circle_lookup[4]["ordered_connections"] = [3, 5, 1]
        
        # Center connects to all corners in clockwise order
        self.app.circle_lookup[5]["ordered_connections"] = [1, 2, 3, 4]
        
        # Mock the connection curve offset method
        with patch.object(self.app.connection_manager, 'get_connection_curve_offset', return_value=(0, 0)):
            # Update enclosure status
            self.app.boundary_manager.update_enclosure_status()
        
        # All corners should be on boundary
        for i in range(1, 5):
            self.assertFalse(self.app.circle_lookup[i]['enclosed'])
            
        # Center should be enclosed
        self.assertTrue(self.app.circle_lookup[5]['enclosed'])
        
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
                
    def test_fixed_nodes_in_boundary_traversal(self):
        """Test that fixed nodes are properly handled during boundary traversal."""
        # Create a triangle with one fixed node
        self.app.FIXED_NODE_A_ID = -1
        self.app.FIXED_NODE_B_ID = -2
        
        # Create the fixed nodes
        fixed_node_a = self._create_test_circle(self.app.FIXED_NODE_A_ID, 15, 60)
        fixed_node_b = self._create_test_circle(self.app.FIXED_NODE_B_ID, 60, 15)
        
        # Set them as fixed
        fixed_node_a["fixed"] = True
        fixed_node_b["fixed"] = True
        
        # Create a third, regular node
        regular_node = self._create_test_circle(1, 100, 100)
        
        self.app.circles = [fixed_node_a, fixed_node_b, regular_node]
        self.app.circle_lookup = {
            self.app.FIXED_NODE_A_ID: fixed_node_a,
            self.app.FIXED_NODE_B_ID: fixed_node_b,
            1: regular_node
        }
        
        # Connect nodes to form a triangle
        fixed_node_a["connected_to"] = [self.app.FIXED_NODE_B_ID, 1]
        fixed_node_a["ordered_connections"] = [self.app.FIXED_NODE_B_ID, 1]
        
        fixed_node_b["connected_to"] = [self.app.FIXED_NODE_A_ID, 1]
        fixed_node_b["ordered_connections"] = [self.app.FIXED_NODE_A_ID, 1]
        
        regular_node["connected_to"] = [self.app.FIXED_NODE_A_ID, self.app.FIXED_NODE_B_ID]
        regular_node["ordered_connections"] = [self.app.FIXED_NODE_A_ID, self.app.FIXED_NODE_B_ID]
        
        # Mock angle calculations for consistent traversal
        with patch.object(self.app.boundary_manager, '_calculate_corrected_angle') as mock_angle:
            # Define angles to ensure clockwise traversal
            def angle_side_effect(circle, neighbor_id):
                if circle['id'] == self.app.FIXED_NODE_A_ID:
                    return 0 if neighbor_id == self.app.FIXED_NODE_B_ID else 45  # B then 1
                elif circle['id'] == self.app.FIXED_NODE_B_ID:
                    return 135 if neighbor_id == 1 else 180  # 1 then A
                else:  # Regular node
                    return 225 if neighbor_id == self.app.FIXED_NODE_A_ID else 315  # A then B
                
            mock_angle.side_effect = angle_side_effect
            
            # Run boundary traversal
            self.app.boundary_manager.update_enclosure_status()
            
        # All nodes should be on boundary (not enclosed)
        self.assertFalse(fixed_node_a['enclosed'], "Fixed node A should be on boundary")
        self.assertFalse(fixed_node_b['enclosed'], "Fixed node B should be on boundary") 
        self.assertFalse(regular_node['enclosed'], "Regular node should be on boundary")
        
    def test_enclosure_with_curved_connections(self):
        """Test enclosure detection with curved connection lines."""
        # Create a square with curved connections
        c1 = self._create_test_circle(1, 50, 50)   # Top-left
        c2 = self._create_test_circle(2, 150, 50)  # Top-right
        c3 = self._create_test_circle(3, 150, 150) # Bottom-right
        c4 = self._create_test_circle(4, 50, 150)  # Bottom-left
        c5 = self._create_test_circle(5, 100, 100) # Center
        
        self.app.circles = [c1, c2, c3, c4, c5]
        self.app.circle_lookup = {c["id"]: c for c in self.app.circles}
        
        # Set up connections for square with center
        # Each corner connected to adjacent corners and center
        for i in range(1, 5):
            next_id = i + 1 if i < 4 else 1
            c = self.app.circle_lookup[i]
            c["connected_to"] = [next_id, 5]
            c["ordered_connections"] = [next_id, 5]
            
            # Connect back to previous (close the square)
            if i == 1:
                c["connected_to"].append(4)
                c["ordered_connections"].append(4)
            
        # Center connected to all corners
        c5["connected_to"] = [1, 2, 3, 4]
        c5["ordered_connections"] = [1, 2, 3, 4]
        
        # Mock connection curve offsets - simulating curves
        def curve_offset_side_effect(from_id, to_id):
            # Add significant curve offsets to connections
            if (from_id == 1 and to_id == 2) or (from_id == 2 and to_id == 1):
                return (0, 30)  # Curve the top edge down
            elif (from_id == 3 and to_id == 4) or (from_id == 4 and to_id == 3):
                return (0, -30)  # Curve the bottom edge up
            return (0, 0)  # No curve for other connections
            
        with patch.object(self.app.connection_manager, 'get_connection_curve_offset') as mock_offset:
            mock_offset.side_effect = curve_offset_side_effect
            
            # Also mock the angle calculation to return values affected by curves
            with patch.object(self.boundary_manager, '_calculate_corrected_angle') as mock_angle:
                def angle_side_effect(circle, neighbor_id):
                    # Simplified angle mapping that accounts for curves
                    circle_id = circle['id']
                    if circle_id == 1:  # Top-left
                        if neighbor_id == 2: return 70  # Curved to right
                        elif neighbor_id == 4: return 180  # Straight down
                        else: return 135  # Diagonal to center
                    elif circle_id == 2:  # Top-right
                        if neighbor_id == 1: return 250  # Curved to left
                        elif neighbor_id == 3: return 180  # Straight down
                        else: return 225  # Diagonal to center
                    elif circle_id == 3:  # Bottom-right
                        if neighbor_id == 2: return 0  # Straight up
                        elif neighbor_id == 4: return 290  # Curved to left
                        else: return 315  # Diagonal to center
                    elif circle_id == 4:  # Bottom-left
                        if neighbor_id == 3: return 110  # Curved to right
                        elif neighbor_id == 1: return 0  # Straight up
                        else: return 45  # Diagonal to center
                    else:  # Center
                        # Return angles to corners
                        angles = {1: 315, 2: 45, 3: 135, 4: 225}
                        return angles.get(neighbor_id, 0)
                
                mock_angle.side_effect = angle_side_effect
                
                # Run boundary traversal
                self.app.boundary_manager.update_enclosure_status()
        
        # Verify boundary nodes
        for i in range(1, 5):
            self.assertFalse(self.app.circle_lookup[i]['enclosed'], f"Corner {i} should be on boundary")
            
        # Center should be enclosed
        self.assertTrue(self.app.circle_lookup[5]['enclosed'], "Center should be enclosed")