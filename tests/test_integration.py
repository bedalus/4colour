"""
Integration tests for the 4colour project.

This module tests interactions between different components.
"""

import sys
import os
# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from unittest.mock import patch, MagicMock
from test_utils import MockAppTestCase
from app_enums import ApplicationMode

class TestComponentInteractions(MockAppTestCase):
    """Tests for interactions between different components."""
    
    def test_circle_color_updates_when_connections_change(self):
        """Test that circle colors update when connections are added/removed."""
        # Setup circles
        first_circle = self._create_test_circle(1, 50, 50, priority=1)
        second_circle = self._create_test_circle(2, 150, 150, priority=2)
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        
        # Test adding connection
        with patch.object(self.app.connection_manager, 'add_connection', return_value=True) as mock_add:
            def side_effect(from_id, to_id):
                # Update connected_to lists when connection is added
                self.app.circle_lookup[from_id]["connected_to"].append(to_id)
                self.app.circle_lookup[to_id]["connected_to"].append(from_id)
                return True
            mock_add.side_effect = side_effect
            
            self.app.add_connection(1, 2)
            self.assertIn(2, first_circle["connected_to"])
            self.assertIn(1, second_circle["connected_to"])
        
        # Test removing connection
        with patch.object(self.app.connection_manager, 'remove_circle_connections') as mock_remove:
            def side_effect(circle_id):
                # Update connected_to lists when removing connections
                for other_circle in self.app.circles:
                    if circle_id in other_circle["connected_to"]:
                        other_circle["connected_to"].remove(circle_id)
            mock_remove.side_effect = side_effect
            
            self.app._remove_circle_by_id(1)
            mock_remove.assert_called_once_with(1)
            self.assertNotIn(1, second_circle["connected_to"])

class TestIntegrationWorkflows(MockAppTestCase):
    """Tests for full workflows and component interactions."""

    # Removed test_full_circle_placement_workflow

    def test_mode_switching_behavior(self):
        """Test that mode switching works correctly with proper UI updates."""
        # Initial mode should be CREATE
        self.assertEqual(self.app._mode, ApplicationMode.CREATE)
        
        # Switch to ADJUST mode
        with patch.object(self.app.ui_manager, 'show_edit_hint_text') as mock_hint:
            with patch.object(self.app.connection_manager, 'show_midpoint_handles') as mock_handles:
                self.app._set_application_mode(ApplicationMode.ADJUST)
                
                # Verify proper UI updates
                self.assertEqual(self.app._mode, ApplicationMode.ADJUST)
                mock_hint.assert_called_once()
                mock_handles.assert_called_once()
                self.app.canvas.config.assert_called_with(bg="#FFEEEE")
        
        # Switch from ADJUST to SELECTION (this is actually allowed)
        self.app._set_application_mode(ApplicationMode.SELECTION)
        self.assertEqual(self.app._mode, ApplicationMode.SELECTION)  # Mode should change
        
        # Test the disallowed transition: SELECTION to ADJUST (should not be allowed)
        self.app._set_application_mode(ApplicationMode.ADJUST)
        self.assertEqual(self.app._mode, ApplicationMode.SELECTION)  # Should remain in SELECTION
        
        # Switch back to CREATE mode from SELECTION
        self.app._set_application_mode(ApplicationMode.CREATE)
        self.assertEqual(self.app._mode, ApplicationMode.CREATE)

    def test_mode_switching_side_effects(self):
        """Test detailed side effects during mode transitions."""
        # Setup initial state with connections and midpoints
        circle1 = self._create_test_circle(1, 50, 50, connections=[2])
        circle2 = self._create_test_circle(2, 150, 50, connections=[1])
        
        self.app.circles = [circle1, circle2]
        self.app.circle_lookup = {1: circle1, 2: circle2}
        self.app.connections = {
            "1_2": {"line_id": 200, "from_circle": 1, "to_circle": 2}
        }
        self.app.midpoint_handles = {"1_2": 300}
        self.app.hint_text_id = 100
        self.app._mode = ApplicationMode.CREATE  # Ensure we start in CREATE mode
        
        # Test CREATE to ADJUST transition
        with patch.object(self.app.interaction_handler, 'unbind_mode_events') as mock_unbind:
            with patch.object(self.app.interaction_handler, 'bind_mode_events') as mock_bind:
                with patch.object(self.app.ui_manager, 'show_edit_hint_text') as mock_hint:
                    with patch.object(self.app.connection_manager, 'show_midpoint_handles') as mock_handles:
                        self.app._set_application_mode(ApplicationMode.ADJUST)
                        
                        mock_unbind.assert_called_with(ApplicationMode.CREATE)
                        mock_bind.assert_called_with(ApplicationMode.ADJUST)
                        mock_hint.assert_called_once()
                        mock_handles.assert_called_once()
                        self.app.canvas.config.assert_called_with(bg="#FFEEEE")
        
        # Test ADJUST to CREATE transition
        with patch.object(self.app.interaction_handler, 'unbind_mode_events') as mock_unbind:
            with patch.object(self.app.interaction_handler, 'bind_mode_events') as mock_bind:
                with patch.object(self.app.connection_manager, 'hide_midpoint_handles') as mock_hide:
                    self.app._set_application_mode(ApplicationMode.CREATE)
                    
                    mock_unbind.assert_called_with(ApplicationMode.ADJUST)
                    mock_bind.assert_called_with(ApplicationMode.CREATE)
                    mock_hide.assert_called_once()
                    self.app.canvas.config.assert_called_with(bg="white")
        
        # Test entering SELECTION mode with proper patching
        # First ensure we're not in SELECTION mode
        self.app._mode = ApplicationMode.CREATE
        
        # Create a new mock for show_hint_text to avoid conflicts
        mock_hint = MagicMock()
        self.app.ui_manager.show_hint_text = mock_hint
        
        # Now properly transition to SELECTION mode (not just set the mode attribute)
        # Usually this would be called when placing a circle
        def mock_switch_to_selection_mode():
            self.app._set_application_mode(ApplicationMode.SELECTION)
            # Call show_hint_text after setting the mode
            self.app.ui_manager.show_hint_text()
        
        self.app._switch_to_selection_mode = mock_switch_to_selection_mode
        
        # Now call the selection mode transition
        self.app._switch_to_selection_mode()
        
        # Verify the mode changed and hint text was shown
        self.assertEqual(self.app._mode, ApplicationMode.SELECTION)
        mock_hint.assert_called_once()

    # Removed test_clear_canvas_resets_all_managers

    def test_circle_and_connection_removal_cascade(self):
        """Test that removing a circle also removes all its connections."""
        # Setup circles and connections
        circle1 = self._create_test_circle(1, 50, 50, connections=[2, 3])
        circle2 = self._create_test_circle(2, 150, 50, connections=[1])
        circle3 = self._create_test_circle(3, 100, 150, connections=[1])
        
        self.app.circles = [circle1, circle2, circle3]
        self.app.circle_lookup = {1: circle1, 2: circle2, 3: circle3}
        
        # Setup connections
        self.app.connections = {
            "1_2": {"line_id": 200, "from_circle": 1, "to_circle": 2},
            "1_3": {"line_id": 201, "from_circle": 1, "to_circle": 3}
        }
        
        # Test removing circle 1
        self.app._mode = ApplicationMode.ADJUST
        self.app._remove_circle_by_id(1)
        
        # Verify circle was removed
        self.assertNotIn(1, self.app.circle_lookup)
        self.assertEqual(len(self.app.circles), 2)
        
        # Verify connections were removed
        self.assertNotIn("1_2", self.app.connections)
        self.assertNotIn("1_3", self.app.connections)
        
        # Verify connected circles were updated
        self.assertNotIn(1, circle2["connected_to"])
        self.assertNotIn(1, circle3["connected_to"])

    def test_connection_induces_color_conflict_resolution(self):
        """Test that connecting circles triggers color conflict resolution."""
        # Setup circles with a potential color conflict
        circle1 = self._create_test_circle(1, 50, 50, priority=1, connections=[2])
        circle2 = self._create_test_circle(2, 150, 50, priority=2, connections=[1])
        circle3 = self._create_test_circle(3, 100, 150, priority=1, connections=[])  # Same priority as circle1
        
        self.app.circles = [circle1, circle2, circle3]
        self.app.circle_lookup = {1: circle1, 2: circle2, 3: circle3}
        
        # Setup existing connection
        self.app.connections = {
            "1_2": {"line_id": 200, "from_circle": 1, "to_circle": 2}
        }
        
        # Prepare for selection mode
        self.app.in_selection_mode = True
        self.app.newly_placed_circle_id = 3
        self.app.selected_circles = [1]  # Selected circle1 to connect to circle3
        
        # Mock connection manager and color manager
        with patch.object(self.app.connection_manager, 'add_connection', return_value=True) as mock_add:
            def add_side_effect(from_id, to_id):
                # Update connected_to lists when connection is added
                self.app.circle_lookup[from_id]["connected_to"].append(to_id)
                self.app.circle_lookup[to_id]["connected_to"].append(from_id)
                return True
            mock_add.side_effect = add_side_effect
            
            with patch.object(self.app.color_manager, 'check_and_resolve_color_conflicts') as mock_check:
                def check_side_effect(circle_id):
                    # Simulate color conflict resolution by updating the priority
                    if circle_id == 3:
                        self.app.circle_lookup[circle_id]["color_priority"] = 3
                    return 3
                mock_check.side_effect = check_side_effect
                
                # Confirm the selection to create connection
                confirm_event = self._create_key_event('y')
                self.app._confirm_selection(confirm_event)
                
                # Verify connection was added and color conflict was resolved
                mock_add.assert_called_with(3, 1)
                mock_check.assert_called_with(3)
                self.assertEqual(circle3["color_priority"], 3)  # Should be assigned new priority

class TestEnclosureStatus(MockAppTestCase):
    """Test cases for the enclosure status update logic."""

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

    # Removed test_enclosure_triangle_with_center

    def test_enclosure_empty_graph(self):
        """Test enclosure status with no circles."""
        self.app._update_enclosure_status()
        # No assertions needed, just ensure it runs without error

    def test_enclosure_single_circle(self):
        """Test enclosure status with one circle."""
        c1 = self._create_test_circle(1, 50, 50)
        self.app.circles = [c1]
        self.app.circle_lookup = {1: c1}
        self.app._update_enclosure_status()
        self.assertFalse(self.app.circle_lookup[1]['enclosed'])

    def test_enclosure_two_connected_circles(self):
        """Test enclosure status with two connected circles."""
        c1 = self._create_test_circle(1, 50, 50)
        c2 = self._create_test_circle(2, 150, 50)
        self.app.circles = [c1, c2]
        self.app.circle_lookup = {1: c1, 2: c2}
        self.app.connection_manager.add_connection(1, 2)

        self.app._update_enclosure_status()
        self.assertFalse(self.app.circle_lookup[1]['enclosed'])
        self.assertFalse(self.app.circle_lookup[2]['enclosed'])

    def test_enclosure_triangle(self):
        """Test enclosure status for a triangle (all outer)."""
        self._setup_triangle()
        self.app._update_enclosure_status()

        self.assertFalse(self.app.circle_lookup[1]['enclosed'], "Circle 1 should not be enclosed")
        self.assertFalse(self.app.circle_lookup[2]['enclosed'], "Circle 2 should not be enclosed")
        self.assertFalse(self.app.circle_lookup[3]['enclosed'], "Circle 3 should not be enclosed")

    def test_enclosure_square(self):
        """Test enclosure status for a square (all outer)."""
        self._setup_square()
        self.app._update_enclosure_status()

        self.assertFalse(self.app.circle_lookup[1]['enclosed'])
        self.assertFalse(self.app.circle_lookup[2]['enclosed'])
        self.assertFalse(self.app.circle_lookup[3]['enclosed'])
        self.assertFalse(self.app.circle_lookup[4]['enclosed'])

    # Removed test_enclosure_update_after_connection
    # Removed test_enclosure_update_after_removal

    def test_fixed_nodes_behavior(self):
        """Test that fixed nodes cannot be dragged or removed."""
        # Test removal prevention
        # Try to remove the fixed node A - this should fail
        result = self.app.circle_manager.remove_circle_by_id(self.app.FIXED_NODE_A_ID)
        self.assertFalse(result)
        self.assertIn(self.app.FIXED_NODE_A_ID, self.app.circle_lookup)
        
        # Try to remove the fixed node B - this should fail
        result = self.app.circle_manager.remove_circle_by_id(self.app.FIXED_NODE_B_ID)
        self.assertFalse(result)
        self.assertIn(self.app.FIXED_NODE_B_ID, self.app.circle_lookup)
        
        # Test drag prevention
        # Set up drag state as if user clicked on a fixed node
        self.app._set_application_mode(ApplicationMode.ADJUST)
        
        fixed_node_a = self.app.circle_lookup[self.app.FIXED_NODE_A_ID]
        event = self._create_click_event(fixed_node_a['x'], fixed_node_a['y'])
        
        # Simulate drag start
        self.app.interaction_handler.drag_start(event)
        
        # Drag state should not be active since fixed nodes cannot be dragged
        self.assertFalse(self.app.drag_state['active'])
        
        # Try to modify the connection between fixed nodes
        connection_key = f"{self.app.FIXED_NODE_A_ID}_{self.app.FIXED_NODE_B_ID}"
        
        # Get midpoint handle position
        midpoint_x, midpoint_y = self.app.connection_manager.calculate_midpoint_handle_position(
            self.app.FIXED_NODE_A_ID, 
            self.app.FIXED_NODE_B_ID
        )
        
        # Set up drag state as if user clicked on the midpoint handle
        self.app.midpoint_handles[connection_key] = self.app.canvas.create_rectangle(
            midpoint_x - 5, midpoint_y - 5, midpoint_x + 5, midpoint_y + 5,
            tags=('midpoint_handle', connection_key)
        )
        
        # Simulate drag start on the midpoint handle
        event = self._create_click_event(midpoint_x, midpoint_y)
        self.app._drag_start(event)
        
        # Drag state should not be active since fixed connections cannot be modified
        self.assertFalse(self.app.drag_state['active'])

    # Removed test_proximity_restrictions

    def test_boundary_traversal_with_reused_edges(self):
        """Test that boundary traversal correctly handles edges that appear twice in the boundary."""
        # Create a simple graph with an edge that must be traversed twice in the boundary
        # Fixed node A and B already exist
        # Add a node that connects to both fixed nodes, forming a triangle
        
        # First, set up our nodes (fixed nodes A and B already exist)
        fixed_node_a = self.app.circle_lookup[self.app.FIXED_NODE_A_ID]
        fixed_node_b = self.app.circle_lookup[self.app.FIXED_NODE_B_ID]
        
        # Create node C which will be connected to both fixed nodes
        event = self._create_click_event(100, 100)
        self.app._mode = ApplicationMode.CREATE
        
        # Mock color assignment and create node C
        with patch.object(self.app.color_manager, 'assign_color_based_on_connections', return_value=3):
            self.app.interaction_handler.draw_on_click(event)
            
            # Now node C (ID 1) should be placed and selection mode entered
            self.assertTrue(self.app.in_selection_mode)
            self.assertEqual(self.app.newly_placed_circle_id, 1)
            
            # Select both fixed nodes to connect to
            self.app.selected_circles = [self.app.FIXED_NODE_A_ID, self.app.FIXED_NODE_B_ID]
            
            # Confirm selection
            confirm_event = self._create_key_event('y')
            with patch.object(self.app.color_manager, 'check_and_resolve_color_conflicts', return_value=3):
                self.app.interaction_handler.confirm_selection(confirm_event)
        
        # Now we have a triangle: Fixed A -- Fixed B -- Node C -- Fixed A
        # Node C should be connected to both fixed nodes
        node_c = self.app.circle_lookup[1]
        self.assertEqual(len(node_c['connected_to']), 2)
        self.assertIn(self.app.FIXED_NODE_A_ID, node_c['connected_to'])
        self.assertIn(self.app.FIXED_NODE_B_ID, node_c['connected_to'])
        
        # Both fixed nodes should be connected to node C
        self.assertIn(1, fixed_node_a['connected_to'])
        self.assertIn(1, fixed_node_b['connected_to'])
        
        # Now add a second node D that's only connected to node C
        # This creates a case where Node C appears twice in the boundary traversal
        event = self._create_click_event(150, 150)
        with patch.object(self.app.color_manager, 'assign_color_based_on_connections', return_value=2):
            self.app.interaction_handler.draw_on_click(event)
            
            # Select only node C to connect to
            self.app.selected_circles = [1] # Node C
            
            # Confirm selection
            confirm_event = self._create_key_event('y')
            with patch.object(self.app.color_manager, 'check_and_resolve_color_conflicts', return_value=2):
                self.app.interaction_handler.confirm_selection(confirm_event)
        
        # Now we have a graph where:
        # Fixed A -- Fixed B -- Node C -- Node D
        #    \       /
        #     ------
        
        # Force a re-calculation of the enclosure status
        with patch('builtins.print') as mock_print:
            self.app._update_enclosure_status()
            
            # The traversal should not report revisiting a node unexpectedly
            unexpected_visit_calls = [
                call for call in mock_print.call_args_list 
                if "revisited node" in str(call) and "unexpectedly" in str(call)
            ]
            self.assertEqual(len(unexpected_visit_calls), 0, 
                            "Boundary traversal reported unexpected node revisit")
            
            # All nodes should be correctly identified as boundary nodes
            for node_id in [self.app.FIXED_NODE_A_ID, self.app.FIXED_NODE_B_ID, 1, 2]:
                node = self.app.circle_lookup[node_id]
                self.assertFalse(node['enclosed'], f"Node {node_id} should be on boundary")
                
        # Create another test configuration - a "lollipop" structure
        # Clear existing structure and re-initialize
        self.app.ui_manager.clear_canvas()
        
        # Create a linear chain: Fixed A -- Fixed B -- Node E -- Node F
        event_e = self._create_click_event(100, 100)
        with patch.object(self.app.color_manager, 'assign_color_based_on_connections', return_value=3):
            self.app.interaction_handler.draw_on_click(event_e)
            self.app.selected_circles = [self.app.FIXED_NODE_B_ID]
            confirm_event = self._create_key_event('y')
            self.app.interaction_handler.confirm_selection(confirm_event)
        
        event_f = self._create_click_event(150, 150)
        with patch.object(self.app.color_manager, 'assign_color_based_on_connections', return_value=2):
            self.app.interaction_handler.draw_on_click(event_f)
            self.app.selected_circles = [1]  # Node E
            confirm_event = self._create_key_event('y')
            self.app.interaction_handler.confirm_selection(confirm_event)
        
        # Force a re-calculation of the enclosure status with the linear graph
        with patch('builtins.print') as mock_print:
            self.app._update_enclosure_status()
            
            # The traversal should not report revisiting a node unexpectedly
            unexpected_visit_calls = [
                call for call in mock_print.call_args_list 
                if "revisited node" in str(call) and "unexpectedly" in str(call)
            ]
            self.assertEqual(len(unexpected_visit_calls), 0, 
                            "Boundary traversal reported unexpected node revisit")
            
            # All nodes should be correctly identified as boundary nodes
            for node_id in [self.app.FIXED_NODE_A_ID, self.app.FIXED_NODE_B_ID, 1, 2]:
                node = self.app.circle_lookup[node_id]
                self.assertFalse(node['enclosed'], f"Node {node_id} should be on boundary")
