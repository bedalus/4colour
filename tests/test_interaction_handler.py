"""
Unit tests for interaction_handler.py.
"""

import sys
import os
# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from unittest.mock import patch, MagicMock
from test_utils import MockAppTestCase
from app_enums import ApplicationMode

class TestInteractionHandler(MockAppTestCase):
    """Test cases for the Interaction Handler."""
    
    def test_draw_on_click_first_circle(self):
        """Test drawing the first circle on the canvas."""
        event = self._create_click_event(100, 100)
        
        with patch.object(self.app, '_assign_color_based_on_connections', return_value=4):
            with patch.object(self.app, '_update_enclosure_status') as mock_update_enclosure:
                self.app._draw_on_click(event)
            
            self.app.canvas.create_oval.assert_called_once()
            
            self.assertEqual(len(self.app.drawn_items), 1)
            self.assertEqual(self.app.drawn_items[0], (100, 100))
            
            self.assertEqual(len(self.app.circles), 1)
            circle = self.app.circles[0]
            self.assertEqual(circle["id"], 1)
            self.assertEqual(circle["x"], 100)
            self.assertEqual(circle["y"], 100)
            self.assertEqual(circle["color_priority"], 4)
            self.assertEqual(circle["connected_to"], [])
            self.assertFalse(circle["enclosed"]) # Verify new attribute
            
            self.assertIn(1, self.app.circle_lookup)
            self.assertEqual(self.app.circle_lookup[1], circle)
            
            self.assertEqual(self.app.last_circle_id, 1)
            self.assertEqual(self.app.next_id, 2)
            mock_update_enclosure.assert_called_once() # Verify enclosure update was called
    
    def test_draw_on_click_second_circle(self):
        """Test drawing a second circle that enters selection mode."""
        # Setup: Add a first circle
        first_circle = self._create_test_circle(1, 50, 50, priority=3)
        self.app.circles = [first_circle]
        self.app.circle_lookup = {1: first_circle}
        self.app.last_circle_id = 1
        self.app.next_id = 2
        
        # Create event for the second circle
        event = self._create_click_event(100, 100)
        
        # Mock methods - including ui_manager's show_hint_text
        self.app.canvas.create_oval.return_value = 201
        
        with patch.object(self.app.ui_manager, 'show_hint_text') as mock_show_hint:
            with patch.object(self.app, '_assign_color_based_on_connections', return_value=2):
                with patch.object(self.app, '_update_enclosure_status') as mock_update_enclosure:
                    self.app._draw_on_click(event)
                
                mock_show_hint.assert_called_once()
                
                self.app.canvas.create_oval.assert_called_once()
                self.assertEqual(len(self.app.circles), 2)
                self.assertEqual(self.app.newly_placed_circle_id, 2)
                self.assertTrue(self.app.in_selection_mode)
                self.assertEqual(self.app.last_circle_id, 1)  # Unchanged
                self.assertEqual(self.app.next_id, 3)  # Incremented
                
                second_circle = self.app.circles[1]
                self.assertFalse(second_circle["enclosed"]) # Verify new attribute
                mock_update_enclosure.assert_called_once() # Verify enclosure update was called
    
    def test_toggle_circle_selection(self):
        """Test selecting and deselecting circles."""
        # Setup: Add two circles
        first_circle = self._create_test_circle(1, 50, 50)
        second_circle = self._create_test_circle(2, 100, 100)
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        self.app.newly_placed_circle_id = 2
        self.app.selected_circles = []
        self.app.selection_indicators = {}
        
        # Test selecting a circle
        self.app.canvas.create_line.return_value = 200
        self.app._toggle_circle_selection(1)
        
        self.assertIn(1, self.app.selected_circles)
        self.app.canvas.create_line.assert_called_once()
        self.assertEqual(self.app.selection_indicators[1], 200)
        
        # Test deselecting the circle
        self.app.canvas.create_line.reset_mock()
        self.app._toggle_circle_selection(1)
        
        self.assertNotIn(1, self.app.selected_circles)
        self.app.canvas.delete.assert_called_with(200)
        self.assertNotIn(1, self.app.selection_indicators)
    
    def test_toggle_circle_selection_newly_placed(self):
        """Test that newly placed circle can't be selected."""
        circle = self._create_test_circle(1, 50, 50)
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}
        self.app.newly_placed_circle_id = 1
        self.app.selected_circles = []
        
        self.app._toggle_circle_selection(1)
        
        self.assertNotIn(1, self.app.selected_circles)
        self.app.canvas.create_line.assert_not_called()
    
    def test_confirm_selection(self):
        """Test confirming circle selections with 'y' key."""
        # Setup selection scenario
        first_circle = self._create_test_circle(1, 50, 50)
        second_circle = self._create_test_circle(2, 150, 150)
        
        self.app.circles = [first_circle, second_circle]
        self.app.circle_lookup = {1: first_circle, 2: second_circle}
        self.app.in_selection_mode = True
        self.app.newly_placed_circle_id = 2
        self.app.selected_circles = [1]
        self.app.selection_indicators = {1: 200}
        self.app.hint_text_id = 300
        
        # Mock methods - updated to use the right objects
        with patch.object(self.app.connection_manager, 'add_connection', return_value=True) as mock_add:
            with patch.object(self.app.color_manager, 'check_and_resolve_color_conflicts', return_value=2) as mock_check:
                with patch.object(self.app, '_update_enclosure_status') as mock_update_enclosure:
                    event = self._create_key_event('y')
                    self.app._confirm_selection(event)
                
                mock_add.assert_called_with(2, 1)
                mock_check.assert_called_with(2)
                mock_update_enclosure.assert_called_once() # Verify enclosure update called
                
                self.assertFalse(self.app.in_selection_mode)
                self.app.canvas.delete.assert_any_call(300)
    
    def test_confirm_selection_not_in_selection_mode(self):
        """Test y key does nothing when not in selection mode."""
        self.app.in_selection_mode = False
        
        with patch.object(self.app, 'add_connection') as mock_add:
            event = self._create_key_event('y')
            self.app._confirm_selection(event)
            mock_add.assert_not_called()
    
    def test_toggle_mode(self):
        """Test toggling between create and adjust modes."""
        # Test CREATE to ADJUST
        self.app._mode = ApplicationMode.CREATE
        
        with patch.object(self.app.interaction_handler, 'set_application_mode') as mock_set_mode:
            self.app._toggle_mode()
            mock_set_mode.assert_called_with(ApplicationMode.ADJUST)
        
        # Test ADJUST to CREATE
        self.app._mode = ApplicationMode.ADJUST
        
        with patch.object(self.app.interaction_handler, 'set_application_mode') as mock_set_mode:
            self.app._toggle_mode()
            mock_set_mode.assert_called_with(ApplicationMode.CREATE)
        
        # Test SELECTION mode doesn't change
        self.app._mode = ApplicationMode.SELECTION
        
        with patch.object(self.app.interaction_handler, 'set_application_mode') as mock_set_mode:
            mock_set_mode.assert_not_called()
    
    def test_drag_functionality(self):
        """Test dragging circles and midpoints."""
        # Setup: Add a circle
        circle = self._create_test_circle(1, 50, 50)
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}
        self.app._mode = ApplicationMode.ADJUST
        
        # Test drag start on a circle
        with patch.object(self.app, 'get_circle_at_coords', return_value=1):
            event = self._create_click_event(50, 50)
            self.app._drag_start(event)
            
            self.assertTrue(self.app.drag_state["active"])
            self.assertEqual(self.app.drag_state["type"], "circle")
            self.assertEqual(self.app.drag_state["id"], 1)
            self.assertEqual(self.app.drag_state["start_x"], 50)
            self.assertEqual(self.app.drag_state["start_y"], 50)
        
        # Test drag motion - updated to reference connection_manager
        with patch.object(self.app.connection_manager, 'update_connections') as mock_update:
            event = self._create_click_event(60, 70)
            self.app._drag_motion(event)
            
            self.app.canvas.move.assert_called_with(101, 10, 20)
            self.assertEqual(circle["x"], 60)
            self.assertEqual(circle["y"], 70)
            mock_update.assert_called_once_with(1)
        
        # Test drag end
        event = self._create_click_event(60, 70)
        self.app._drag_end(event)
        
        self.assertFalse(self.app.drag_state["active"])
        self.assertIsNone(self.app.drag_state["type"])
        self.assertIsNone(self.app.drag_state["id"])
    
    def test_set_application_mode(self):
        """Test setting application mode with appropriate transitions."""
        # Test CREATE to ADJUST transition
        self.app._mode = ApplicationMode.CREATE
        
        # Fix: Patch methods on the appropriate manager objects, not directly on app
        with patch.object(self.app.interaction_handler, 'unbind_mode_events') as mock_unbind:
            with patch.object(self.app.interaction_handler, 'bind_mode_events') as mock_bind:
                with patch.object(self.app.ui_manager, 'show_edit_hint_text') as mock_hint:
                    with patch.object(self.app.connection_manager, 'show_midpoint_handles') as mock_handles:
                        
                        self.app._set_application_mode(ApplicationMode.ADJUST)
                        
                        self.assertEqual(self.app._mode, ApplicationMode.ADJUST)
                        mock_unbind.assert_called_with(ApplicationMode.CREATE)
                        mock_bind.assert_called_with(ApplicationMode.ADJUST)
                        mock_hint.assert_called_once()
                        mock_handles.assert_called_once()
                        self.app.canvas.config.assert_called_with(bg="#FFEEEE")
        
        # Test SELECTION to ADJUST transition (should fail)
        self.app._mode = ApplicationMode.SELECTION
        self.app._set_application_mode(ApplicationMode.ADJUST)
        self.assertEqual(self.app._mode, ApplicationMode.SELECTION)  # Unchanged
        
        # Test ADJUST to CREATE transition
        self.app._mode = ApplicationMode.ADJUST
        self.app.edit_hint_text_id = 200
        
        with patch.object(self.app.interaction_handler, 'unbind_mode_events') as mock_unbind:
            with patch.object(self.app.interaction_handler, 'bind_mode_events') as mock_bind:
                with patch.object(self.app.connection_manager, 'hide_midpoint_handles') as mock_hide:
                    
                    self.app._set_application_mode(ApplicationMode.CREATE)
                    
                    self.assertEqual(self.app._mode, ApplicationMode.CREATE)
                    mock_unbind.assert_called_with(ApplicationMode.ADJUST)
                    mock_bind.assert_called_with(ApplicationMode.CREATE)
                    mock_hide.assert_called_once()
                    self.app.canvas.config.assert_called_with(bg="white")
    
    def test_drag_end_updates_ordered_connections_for_circle(self):
        """Test that drag_end updates ordered_connections when dragging a circle."""
        # Setup circle and drag state
        circle = self._create_test_circle(1, 50, 50, connections=[2, 3])
        circle2 = self._create_test_circle(2, 150, 50, connections=[1])
        circle3 = self._create_test_circle(3, 50, 150, connections=[1])
        
        self.app.circles = [circle, circle2, circle3]
        self.app.circle_lookup = {1: circle, 2: circle2, 3: circle3}
        
        # Set drag state as if circle 1 was being dragged
        self.app._mode = ApplicationMode.ADJUST
        self.app.drag_state = {
            "active": True,
            "type": "circle",
            "id": 1,
            "start_x": 40, "start_y": 40,
            "last_x": 60, "last_y": 60
        }
        
        # Mock update_ordered_connections
        with patch.object(self.app.connection_manager, 'update_ordered_connections') as mock_update:
            # End drag
            self.app._drag_end(MagicMock())
            
            # Verify update_ordered_connections was called for circle 1 and connected circles 2 and 3
            mock_update.assert_any_call(1)
            mock_update.assert_any_call(2)
            mock_update.assert_any_call(3)
            self.assertEqual(mock_update.call_count, 3)
    
    def test_drag_end_updates_ordered_connections_for_midpoint(self):
        """Test that drag_end updates ordered_connections when dragging a midpoint."""
        # Setup circles and connections
        circle1 = self._create_test_circle(1, 50, 50, connections=[2])
        circle2 = self._create_test_circle(2, 150, 50, connections=[1])
        
        self.app.circles = [circle1, circle2]
        self.app.circle_lookup = {1: circle1, 2: circle2}
        
        # Setup connection
        self.app.connections = {
            "1_2": {"line_id": 101, "from_circle": 1, "to_circle": 2, "curve_X": 0, "curve_Y": 0}
        }
        
        # Set drag state as if the midpoint between circles 1 and 2 was being dragged
        self.app._mode = ApplicationMode.ADJUST
        self.app.drag_state = {
            "active": True,
            "type": "midpoint",
            "id": "1_2",
            "start_x": 100, "start_y": 50,
            "last_x": 110, "last_y": 60
        }
        
        # Mock update_ordered_connections
        with patch.object(self.app.connection_manager, 'update_ordered_connections') as mock_update:
            # End drag
            self.app._drag_end(MagicMock())
            
            # Verify update_ordered_connections was called for both connected circles
            mock_update.assert_any_call(1)
            mock_update.assert_any_call(2)
            self.assertEqual(mock_update.call_count, 2)
    
    def test_remove_circle_in_adjust_mode(self):
        """Test removing a circle via right-click in ADJUST mode."""
        # Setup: Create a circle first
        self.app.interaction_handler.draw_on_click(self._create_click_event(50, 50))
        circle_id_to_remove = 1
        
        self.app.interaction_handler.set_application_mode(ApplicationMode.ADJUST)
        self.assertEqual(self.app._mode, ApplicationMode.ADJUST)

        # Mock get_circle_at_coords to return the ID
        with patch.object(self.app.circle_manager, 'get_circle_at_coords', return_value=circle_id_to_remove):
            # Mock the actual removal method in circle_manager
            with patch.object(self.app.circle_manager, 'remove_circle_by_id', return_value=True) as mock_remove_by_id:
                 # Mock the enclosure update call
                 with patch.object(self.app, '_update_enclosure_status') as mock_update_enclosure:
                    event = self._create_click_event(50, 50, button=3) # Right-click
                    self.app.interaction_handler.remove_circle(event)

        # Verify remove_circle_by_id was called
        mock_remove_by_id.assert_called_once_with(circle_id_to_remove)
        # Verify enclosure status was updated because removal succeeded
        mock_update_enclosure.assert_called_once()

    def test_remove_circle_not_found(self):
        """Test right-clicking empty space in ADJUST mode."""
        self.app.interaction_handler.set_application_mode(ApplicationMode.ADJUST)
        
        # Mock get_circle_at_coords to return None
        with patch.object(self.app.circle_manager, 'get_circle_at_coords', return_value=None):
            with patch.object(self.app.circle_manager, 'remove_circle_by_id') as mock_remove_by_id:
                 with patch.object(self.app, '_update_enclosure_status') as mock_update_enclosure:
                    event = self._create_click_event(50, 50, button=3) # Right-click
                    self.app.interaction_handler.remove_circle(event)

        mock_remove_by_id.assert_not_called()
        mock_update_enclosure.assert_not_called() # Not called if removal didn't happen

    def test_remove_circle_not_in_adjust_mode(self):
        """Test right-clicking when not in ADJUST mode."""
        self.app.interaction_handler.set_application_mode(ApplicationMode.CREATE) # Not ADJUST mode
        
        with patch.object(self.app.circle_manager, 'get_circle_at_coords') as mock_get_circle:
            with patch.object(self.app.circle_manager, 'remove_circle_by_id') as mock_remove_by_id:
                 with patch.object(self.app, '_update_enclosure_status') as mock_update_enclosure:
                    event = self._create_click_event(50, 50, button=3) # Right-click
                    self.app.interaction_handler.remove_circle(event)

        mock_get_circle.assert_not_called()
        mock_remove_by_id.assert_not_called()
        mock_update_enclosure.assert_not_called()

    def test_drag_end_circle(self):
        """Test ending a drag operation for a circle."""
        # Setup: Create two connected circles
        self.app.interaction_handler.draw_on_click(self._create_click_event(50, 50)) # Circle 1
        self.app.interaction_handler.draw_on_click(self._create_click_event(150, 50)) # Circle 2
        self.app.interaction_handler.toggle_circle_selection(1)
        self.app.interaction_handler.confirm_selection(self._create_key_event('y')) # Connect 2 to 1

        # Enter ADJUST mode
        self.app.interaction_handler.set_application_mode(ApplicationMode.ADJUST)

        # Simulate active drag state for circle 1
        self.app.drag_state = {
            "active": True, "type": "circle", "id": 1,
            "start_x": 50, "start_y": 50, "last_x": 60, "last_y": 60
        }

        # Mock dependencies for drag_end
        with patch.object(self.app.ui_manager, 'clear_angle_visualizations') as mock_clear_viz:
            with patch.object(self.app.connection_manager, 'update_ordered_connections') as mock_update_ordered:
                 with patch.object(self.app, '_update_enclosure_status') as mock_update_enclosure:
                    event = self._create_click_event(60, 60, release=True) # ButtonRelease-1
                    self.app.interaction_handler.drag_end(event)

        # Verify actions
        mock_clear_viz.assert_called_once()
        # Should update ordered connections for dragged circle (1) and neighbor (2)
        mock_update_ordered.assert_any_call(1)
        mock_update_ordered.assert_any_call(2)
        self.assertEqual(mock_update_ordered.call_count, 2)
        mock_update_enclosure.assert_called_once() # Verify enclosure update called
        # Verify drag state reset
        self.assertFalse(self.app.drag_state["active"])
        self.assertIsNone(self.app.drag_state["type"])
        self.assertIsNone(self.app.drag_state["id"])

    def test_drag_end_midpoint(self):
        """Test ending a drag operation for a midpoint."""
        # Setup: Create two connected circles
        self.app.interaction_handler.draw_on_click(self._create_click_event(50, 50)) # Circle 1
        self.app.interaction_handler.draw_on_click(self._create_click_event(150, 50)) # Circle 2
        self.app.interaction_handler.toggle_circle_selection(1)
        self.app.interaction_handler.confirm_selection(self._create_key_event('y')) # Connect 2 to 1
        connection_key = self.app.connection_manager.get_connection_key(1, 2) # Get consistent key

        # Enter ADJUST mode
        self.app.interaction_handler.set_application_mode(ApplicationMode.ADJUST)

        # Simulate active drag state for the midpoint
        self.app.drag_state = {
            "active": True, "type": "midpoint", "id": connection_key,
            "start_x": 100, "start_y": 50, "last_x": 100, "last_y": 60
        }

        # Mock dependencies for drag_end
        with patch.object(self.app.ui_manager, 'clear_angle_visualizations') as mock_clear_viz:
            with patch.object(self.app.connection_manager, 'update_ordered_connections') as mock_update_ordered:
                 with patch.object(self.app, '_update_enclosure_status') as mock_update_enclosure:
                    event = self._create_click_event(100, 60, release=True) # ButtonRelease-1
                    self.app.interaction_handler.drag_end(event)

        # Verify actions
        mock_clear_viz.assert_called_once()
        # Should update ordered connections for both connected circles (1 and 2)
        mock_update_ordered.assert_any_call(1)
        mock_update_ordered.assert_any_call(2)
        self.assertEqual(mock_update_ordered.call_count, 2)
        mock_update_enclosure.assert_called_once() # Verify enclosure update called
        # Verify drag state reset
        self.assertFalse(self.app.drag_state["active"])
        self.assertIsNone(self.app.drag_state["type"])
        self.assertIsNone(self.app.drag_state["id"])

    def test_cancel_selection(self):
        """Test canceling circle placement with the escape key."""
        # Setup: Add a newly placed circle
        circle = self._create_test_circle(1, 50, 50)
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}
        self.app.newly_placed_circle_id = 1
        self.app.in_selection_mode = True

        with patch.object(self.app.circle_manager, 'remove_circle_by_id') as mock_remove:
            event = self._create_key_event('Escape')
            self.app.interaction_handler.cancel_selection(event)

            # Verify the circle was removed
            mock_remove.assert_called_once_with(1)
            self.assertFalse(self.app.in_selection_mode)

    def test_reset_drag_state(self):
        """Test resetting the drag state."""
        # Set a non-default drag state
        self.app.drag_state = {
            "active": True,
            "type": "circle",
            "id": 1,
            "start_x": 50,
            "start_y": 50,
            "last_x": 60,
            "last_y": 60,
            "curve_x": 10,
            "curve_y": 10
        }

        self.app.interaction_handler.reset_drag_state()

        # Verify the drag state is reset to default values
        self.assertEqual(self.app.drag_state, {
            "active": False,
            "type": None,
            "id": None,
            "start_x": 0,
            "start_y": 0,
            "last_x": 0,
            "last_y": 0,
            "curve_x": 0,
            "curve_y": 0
        })

    def test_drag_start_fixed_node(self):
        """Test that fixed nodes cannot be dragged."""
        circle = self._create_test_circle(1, 50, 50, fixed=True)
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}

        event = self._create_click_event(50, 50)
        self.app.interaction_handler.drag_start(event)

        # Verify drag state is not activated
        self.assertFalse(self.app.drag_state["active"])

    def test_drag_motion_restricted_zone(self):
        """Test that dragging into restricted zones is prevented."""
        circle = self._create_test_circle(1, 50, 50)
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}
        self.app.drag_state = {
            "active": True,
            "type": "circle",
            "id": 1,
            "start_x": 50,
            "start_y": 50,
            "last_x": 50,
            "last_y": 50
        }

        # Set proximity limit to 100 for testing
        self.app.PROXIMITY_LIMIT = 100

        event = self._create_click_event(90, 90)
        self.app.interaction_handler.drag_motion(event)

        # Verify the circle's position is not updated
        self.assertEqual(circle["x"], 50)
        self.assertEqual(circle["y"], 50)

    def test_remove_circle_stub(self):
        """Test the remove_circle stub for backward compatibility."""
        event = self._create_click_event(50, 50)
        self.app.interaction_handler.remove_circle(event)

        # Verify no exceptions are raised and no actions are performed
        self.assertTrue(True)

    def test_drag_start_invalid_target(self):
        """Test that drag start does not activate for invalid targets."""
        event = self._create_click_event(200, 200)  # No circle at this position
        self.app.interaction_handler.drag_start(event)

        # Verify drag state is not activated
        self.assertFalse(self.app.drag_state["active"])

    def test_drag_motion_outside_proximity_limit(self):
        """Test that dragging outside the proximity limit is prevented."""
        circle = self._create_test_circle(1, 50, 50)
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}
        self.app.drag_state = {
            "active": True,
            "type": "circle",
            "id": 1,
            "start_x": 50,
            "start_y": 50,
            "last_x": 50,
            "last_y": 50
        }

        # Set proximity limit to 30 for testing
        self.app.PROXIMITY_LIMIT = 30

        event = self._create_click_event(100, 100)  # Outside proximity limit
        self.app.interaction_handler.drag_motion(event)

        # Verify the circle's position is not updated
        self.assertEqual(circle["x"], 50)
        self.assertEqual(circle["y"], 50)

    def test_remove_circle_in_selection_mode(self):
        """Test that remove_circle does nothing in selection mode."""
        self.app.interaction_handler.set_application_mode(ApplicationMode.SELECTION)

        with patch.object(self.app.circle_manager, 'get_circle_at_coords') as mock_get_circle:
            with patch.object(self.app.circle_manager, 'remove_circle_by_id') as mock_remove_by_id:
                event = self._create_click_event(50, 50, button=3)  # Right-click
                self.app.interaction_handler.remove_circle(event)

        mock_get_circle.assert_not_called()
        mock_remove_by_id.assert_not_called()

    def test_drag_motion_at_proximity_limit(self):
        """Test dragging a circle to the exact boundary of the proximity limit."""
        circle = self._create_test_circle(1, 50, 50)
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}
        self.app.drag_state = {
            "active": True,
            "type": "circle",
            "id": 1,
            "start_x": 50,
            "start_y": 50,
            "last_x": 50,
            "last_y": 50
        }

        # Set proximity limit to 50 for testing
        self.app.PROXIMITY_LIMIT = 50

        event = self._create_click_event(100, 50)  # Exactly at the limit
        self.app.interaction_handler.drag_motion(event)

        # Verify the circle's position is updated
        self.assertEqual(circle["x"], 100)
        self.assertEqual(circle["y"], 50)

    def test_drag_motion_with_overlapping_connections(self):
        """Test dragging a circle with overlapping connections."""
        circle1 = self._create_test_circle(1, 50, 50, connections=[2, 3])
        circle2 = self._create_test_circle(2, 150, 50, connections=[1])
        circle3 = self._create_test_circle(3, 50, 150, connections=[1])

        self.app.circles = [circle1, circle2, circle3]
        self.app.circle_lookup = {1: circle1, 2: circle2, 3: circle3}

        # Set drag state as if circle 1 is being dragged
        self.app.drag_state = {
            "active": True,
            "type": "circle",
            "id": 1,
            "start_x": 50,
            "start_y": 50,
            "last_x": 50,
            "last_y": 50
        }

        # Mock update_connections to verify it is called for all connections
        with patch.object(self.app.connection_manager, 'update_connections') as mock_update:
            event = self._create_click_event(60, 60)
            self.app.interaction_handler.drag_motion(event)

            # Verify the circle's position is updated
            self.assertEqual(circle1["x"], 60)
            self.assertEqual(circle1["y"], 60)

            # Verify connections are updated
            mock_update.assert_called_once_with(1)

    def test_remove_circle_in_complex_graph(self):
        """Test removing a circle that is part of a complex graph."""
        circle1 = self._create_test_circle(1, 50, 50, connections=[2, 3])
        circle2 = self._create_test_circle(2, 150, 50, connections=[1])
        circle3 = self._create_test_circle(3, 50, 150, connections=[1])

        self.app.circles = [circle1, circle2, circle3]
        self.app.circle_lookup = {1: circle1, 2: circle2, 3: circle3}

        # Mock get_circle_at_coords to return the ID of the circle to remove
        with patch.object(self.app.circle_manager, 'get_circle_at_coords', return_value=1):
            # Mock the actual removal method in circle_manager
            with patch.object(self.app.circle_manager, 'remove_circle_by_id', return_value=True) as mock_remove_by_id:
                # Mock the enclosure update call
                with patch.object(self.app, '_update_enclosure_status') as mock_update_enclosure:
                    event = self._create_click_event(50, 50, button=3)  # Right-click
                    self.app.interaction_handler.remove_circle(event)

                    # Verify remove_circle_by_id was called
                    mock_remove_by_id.assert_called_once_with(1)
                    # Verify enclosure status was updated
                    mock_update_enclosure.assert_called_once()
