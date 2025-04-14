"""
Unit tests for ui_manager.py.
"""

import sys
import os
# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import tkinter as tk
from unittest.mock import patch, MagicMock
from test_utils import MockAppTestCase
from app_enums import ApplicationMode

class TestUIManager(MockAppTestCase):
    """Test cases for the UI Manager."""
    
    def test_focus_after(self):
        """Test that focus is set to debug button after command execution."""
        mock_func = MagicMock()
        self.app._focus_after(mock_func)
        
        mock_func.assert_called_once()
        self.app.debug_button.focus_set.assert_called_once()
    
    def test_toggle_debug_enable(self):
        """Test enabling the debug display."""
        self.app.debug_enabled = False
        self.app.debug_text = None
        
        # Update to patch the ui_manager's show_debug_info method
        with patch.object(self.app.ui_manager, 'show_debug_info') as mock_show_debug:
            self.app._toggle_debug()
            
            self.assertTrue(self.app.debug_enabled)
            mock_show_debug.assert_called_once()
    
    def test_toggle_debug_disable(self):
        """Test disabling the debug display."""
        self.app.debug_enabled = True
        self.app.debug_text = 100  # Mock text ID
        
        self.app._toggle_debug()
        
        self.assertFalse(self.app.debug_enabled)
        self.app.canvas.delete.assert_called_once_with(100)
    
    def test_show_debug_info_with_circle(self):
        """Test showing debug info for a circle."""
        self.app.circles = [{
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color_priority": 3,  # Priority 3 is blue
            "connected_to": [2]
        }]
        self.app.debug_enabled = True
        
        self.app._show_debug_info()
        
        self.app.canvas.create_text.assert_called_once()
        args, kwargs = self.app.canvas.create_text.call_args
        self.assertEqual(kwargs['anchor'], tk.NW)
        self.assertIn("Circle ID: 1", kwargs['text'])
        self.assertIn("Position: (50, 50)", kwargs['text'])
        self.assertIn("Color: blue (priority: 3)", kwargs['text'])
        self.assertIn("Connected to: 2", kwargs['text'])
    
    def test_show_debug_info_no_circles(self):
        """Test showing debug info when no circles are present."""
        self.app.circles = []
        self.app.debug_enabled = True
        
        self.app._show_debug_info()
        
        self.app.canvas.create_text.assert_called_once()
        args, kwargs = self.app.canvas.create_text.call_args
        self.assertEqual(kwargs['anchor'], tk.NW)
        self.assertEqual(kwargs['text'], "No circles drawn yet")
    
    def test_show_hint_text(self):
        """Test displaying the hint text in selection mode."""
        self.app.canvas.create_text.return_value = 300
        self.app.canvas_width = 700
        
        self.app._show_hint_text()
        
        self.app.canvas.create_text.assert_called_once()
        args, kwargs = self.app.canvas.create_text.call_args
        self.assertEqual(args[0], 350)  # Half of canvas_width
        self.assertEqual(args[1], 20)
        self.assertEqual(kwargs['text'], "Please select which circles to connect to then press 'y'")
        self.assertEqual(kwargs['anchor'], tk.N)
        self.assertEqual(self.app.hint_text_id, 300)
    
    def test_show_edit_hint_text(self):
        """Test displaying edit mode hint text."""
        self.app.hint_text_id = 100
        self.app.edit_hint_text_id = None
        self.app.canvas_width = 700
        self.app.canvas.create_text.return_value = 200
        
        self.app._show_edit_hint_text()
        
        # Should delete the hint text
        self.app.canvas.delete.assert_called_once_with(100)
        self.assertIsNone(self.app.hint_text_id)
        
        # Should create edit hint text
        self.app.canvas.create_text.assert_called_once()
        args, kwargs = self.app.canvas.create_text.call_args
        self.assertEqual(args[0], 370)  # (Half of canvas_width) + 20
        self.assertEqual(args[1], 20)
        self.assertEqual(kwargs['text'], "Click-and-drag to move, right click to remove")
        self.assertEqual(self.app.edit_hint_text_id, 200)
        
    def test_clear_canvas(self):
        """Test clearing the canvas."""
        # Test when in ADJUST mode (should not clear)
        self.app._mode = ApplicationMode.ADJUST
        self.app._clear_canvas()
        self.app.canvas.delete.assert_not_called()
        
        # Test when in CREATE mode
        self.app._mode = ApplicationMode.CREATE
        self.app.circles = [{"id": 1}]
        self.app.drawn_items = [(50, 50)]
        self.app.circle_lookup = {1: {"id": 1}}
        self.app.connections = {"1_2": {}}
        self.app.midpoint_handles = {"1_2": 300}
        self.app.last_circle_id = 1
        self.app.next_id = 2
        
        self.app._clear_canvas()
        
        self.app.canvas.delete.assert_called_once_with("all")
        self.assertEqual(len(self.app.drawn_items), 0)
        self.assertEqual(len(self.app.circles), 0)
        self.assertEqual(len(self.app.circle_lookup), 0)
        self.assertEqual(len(self.app.connections), 0)
        self.assertEqual(len(self.app.midpoint_handles), 0)
        self.assertIsNone(self.app.last_circle_id)
        self.assertEqual(self.app.next_id, 1)
        
    # New tests for UI Manager to improve coverage
    
    def test_visualize_connection_angles(self):
        """Test visualization of connection angles in debug display."""
        # Set up a circle with connections
        circle1 = self._create_test_circle(1, 100, 100, connections=[2, 3])
        circle2 = self._create_test_circle(2, 200, 100, connections=[1])
        circle3 = self._create_test_circle(3, 100, 200, connections=[1])
        
        self.app.circles = [circle1, circle2, circle3]
        self.app.circle_lookup = {1: circle1, 2: circle2, 3: circle3}
        
        # Mock UI manager's internal methods
        with patch.object(self.app.ui_manager, 'draw_connection_angle_visualizations') as mock_draw:
            self.app.ui_manager.visualize_connection_angles(1)
            
            # Verify visualization method was called with the right parameters
            mock_draw.assert_called_once_with(1)
    
    def test_draw_connection_angle_visualizations(self):
        """Test drawing angle visualizations for connections."""
        # Set up a circle with connections
        circle1 = self._create_test_circle(1, 100, 100, connections=[2, 3])
        circle2 = self._create_test_circle(2, 200, 100, connections=[1])
        circle3 = self._create_test_circle(3, 100, 200, connections=[1])
        
        self.app.circles = [circle1, circle2, circle3]
        self.app.circle_lookup = {1: circle1, 2: circle2, 3: circle3}
        
        # Test with mock canvas
        self.app.canvas.create_line.return_value = 101
        self.app.canvas.create_text.return_value = 102
        
        # Mock connection manager's angle calculation
        with patch.object(self.app.connection_manager, 'calculate_connection_entry_angle') as mock_angle:
            mock_angle.side_effect = lambda circle_id, other_id: 90.0 if other_id == 2 else 180.0
            
            # Call the method under test
            self.app.ui_manager.draw_connection_angle_visualizations(1)
            
            # Verify angle visualization elements were created
            self.app.canvas.create_line.assert_called()
            self.app.canvas.create_text.assert_called()
            
            # Verify the visualization items were stored
            self.assertGreater(len(self.app.ui_manager.visualization_items), 0)
    
    def test_clear_angle_visualizations(self):
        """Test clearing angle visualizations."""
        # Set up visualization items
        self.app.ui_manager.visualization_items = [101, 102, 103]
        
        # Call the method under test
        self.app.ui_manager.clear_angle_visualizations()
        
        # Verify all items were deleted
        self.app.canvas.delete.assert_any_call(101)
        self.app.canvas.delete.assert_any_call(102)
        self.app.canvas.delete.assert_any_call(103)
        self.assertEqual(len(self.app.ui_manager.visualization_items), 0)
    
    def test_ui_state_changes_during_mode_transitions(self):
        """Test UI state changes during different mode transitions."""
        # Initial mode is CREATE
        self.app._mode = ApplicationMode.CREATE
        
        # TEST 1: Transition to SELECTION mode
        # Setup
        self.app.newly_placed_circle_id = 1
        
        with patch.object(self.app.ui_manager, 'show_hint_text') as mock_hint:
            # Transition to SELECTION mode
            self.app._set_application_mode(ApplicationMode.SELECTION)
            
            # Verify UI state changes
            mock_hint.assert_called_once()
            self.assertEqual(self.app._mode, ApplicationMode.SELECTION)
        
        # TEST 2: Transition to ADJUST mode
        with patch.object(self.app.ui_manager, 'show_edit_hint_text') as mock_edit_hint:
            with patch.object(self.app.connection_manager, 'show_midpoint_handles') as mock_handles:
                # Transition to ADJUST mode
                self.app._mode = ApplicationMode.CREATE  # Reset first since SELECTION→ADJUST is blocked
                self.app._set_application_mode(ApplicationMode.ADJUST)
                
                # Verify UI state changes
                mock_edit_hint.assert_called_once()
                mock_handles.assert_called_once()
                self.assertEqual(self.app._mode, ApplicationMode.ADJUST)
                self.app.canvas.config.assert_called_with(bg="#FFEEEE")  # Pink background
        
        # TEST 3: Transition back to CREATE mode
        self.app.edit_hint_text_id = 200
        
        with patch.object(self.app.connection_manager, 'hide_midpoint_handles') as mock_hide:
            # Transition to CREATE mode
            self.app._set_application_mode(ApplicationMode.CREATE)
            
            # Verify UI state changes
            mock_hide.assert_called_once()
            self.assertEqual(self.app._mode, ApplicationMode.CREATE)
            self.app.canvas.config.assert_called_with(bg="white")  # White background
            self.app.canvas.delete.assert_called_with(200)  # Delete edit hint text
    
    def test_button_state_management(self):
        """Test button state management during mode transitions."""
        # Mock the toggle button
        self.app.toggle_button = MagicMock()
        
        # Test CREATE mode button state
        self.app._mode = ApplicationMode.CREATE
        self.app.ui_manager.update_button_states()
        self.app.toggle_button.config.assert_called_with(text="Adjust Mode")
        
        # Test ADJUST mode button state
        self.app._mode = ApplicationMode.ADJUST
        self.app.ui_manager.update_button_states()
        self.app.toggle_button.config.assert_called_with(text="Create Mode")
        
        # Test SELECTION mode button state (button should be disabled)
        self.app._mode = ApplicationMode.SELECTION
        self.app.ui_manager.update_button_states()
        self.app.toggle_button.config.assert_called_with(state="disabled")
    
    def test_hint_text_updating_in_various_scenarios(self):
        """Test hint text updating in various scenarios."""
        # Test scenario 1: Selection mode with newly placed circle
        self.app._mode = ApplicationMode.SELECTION
        self.app.newly_placed_circle_id = 1
        self.app.hint_text_id = None
        self.app.canvas.create_text.return_value = 101
        
        self.app.ui_manager.update_hint_text()
        
        self.app.canvas.create_text.assert_called()
        self.assertEqual(self.app.hint_text_id, 101)
        
        # Test scenario 2: Edit mode with hint text
        self.app._mode = ApplicationMode.ADJUST
        self.app.hint_text_id = 101
        self.app.edit_hint_text_id = None
        self.app.canvas.create_text.return_value = 102
        
        self.app.ui_manager.update_hint_text()
        
        self.app.canvas.delete.assert_called_with(101)  # Delete old hint text
        self.app.canvas.create_text.assert_called()
        self.assertEqual(self.app.edit_hint_text_id, 102)
        
        # Test scenario 3: Create mode with edit text
        self.app._mode = ApplicationMode.CREATE
        self.app.edit_hint_text_id = 102
        
        self.app.ui_manager.update_hint_text()
        
        self.app.canvas.delete.assert_called_with(102)  # Delete edit hint text
        self.assertIsNone(self.app.edit_hint_text_id)
    
    def test_debug_overlay_updating_various_scenarios(self):
        """Test debug overlay updating in various scenarios."""
        # Test scenario 1: Debug enabled, show debug info for circle
        self.app.debug_enabled = True
        self.app.debug_text = None
        circle = self._create_test_circle(1, 100, 100)
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}
        self.app.canvas.create_text.return_value = 101
        
        self.app.ui_manager.update_debug_overlay()
        
        self.app.canvas.create_text.assert_called()
        self.assertEqual(self.app.debug_text, 101)
        
        # Test scenario 2: Debug enabled, update existing debug info
        self.app.debug_enabled = True
        self.app.debug_text = 101
        
        self.app.ui_manager.update_debug_overlay()
        
        self.app.canvas.delete.assert_called_with(101)
        self.app.canvas.create_text.assert_called()
        
        # Test scenario 3: Debug disabled, remove debug info
        self.app.debug_enabled = False
        self.app.debug_text = 101
        
        self.app.ui_manager.update_debug_overlay()
        
        self.app.canvas.delete.assert_called_with(101)
        self.assertIsNone(self.app.debug_text)
    
    def test_set_active_circle(self):
        """Test setting a single active circle for debug info."""
        self.app.ui_manager.set_active_circle(1)
        self.assertEqual(self.app.ui_manager.active_circle_id, 1)

    def test_set_active_circles(self):
        """Test setting multiple active circles for debug info."""
        self.app.ui_manager.set_active_circles(1, 2, 3)
        self.assertEqual(self.app.ui_manager.active_circle_ids, [1, 2, 3])

    def test_draw_angle_visualization_line(self):
        """Test drawing an angle visualization line."""
        circle = self._create_test_circle(1, 100, 100)
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}

        line_id = self.app.ui_manager.draw_angle_visualization_line(1, None, 90)
        self.assertIsNotNone(line_id)
        self.app.canvas.create_line.assert_called_once()

    def test_draw_connection_angle_visualizations_invalid_key(self):
        """Test drawing connection angle visualizations with an invalid key."""
        viz_ids = self.app.ui_manager.draw_connection_angle_visualizations("invalid_key")
        self.assertEqual(viz_ids, [])

    def test_clear_angle_visualizations_no_items(self):
        """Test clearing angle visualizations when no items are present."""
        self.app.ui_manager.visualization_items = []
        self.app.ui_manager.clear_angle_visualizations()
        self.app.canvas.delete.assert_not_called()

    def test_show_debug_info_multiple_active_circles(self):
        """Test showing debug info for multiple active circles."""
        circle1 = self._create_test_circle(1, 50, 50, color_priority=1, connections=[2])
        circle2 = self._create_test_circle(2, 100, 100, color_priority=2, connections=[1])
        self.app.circles = [circle1, circle2]
        self.app.circle_lookup = {1: circle1, 2: circle2}
        self.app.ui_manager.set_active_circles(1, 2)

        self.app.ui_manager.show_debug_info()

        # Verify debug info is displayed for both circles
        self.app.canvas.create_text.assert_called_once()
        args, kwargs = self.app.canvas.create_text.call_args
        self.assertIn("Circle ID: 1", kwargs['text'])
        self.assertIn("Circle ID: 2", kwargs['text'])

    def test_format_circle_info_missing_fields(self):
        """Test formatting circle info with missing fields."""
        circle = {
            "id": 1,
            "x": 50,
            "y": 50,
            "color_priority": 1,
            "connected_to": []
            # Missing 'ordered_connections' and 'enclosed'
        }

        formatted_info = self.app.ui_manager._format_circle_info(circle)

        # Verify the formatted info handles missing fields gracefully
        self.assertIn("Circle ID: 1", formatted_info)
        self.assertIn("Position: (50, 50)", formatted_info)
        self.assertIn("Connected to: None", formatted_info)
        self.assertIn("Clockwise order: None", formatted_info)
        self.assertIn("Enclosed: False", formatted_info)

    def test_draw_connection_angle_visualizations_valid_key(self):
        """Test drawing connection angle visualizations with a valid key."""
        circle1 = self._create_test_circle(1, 50, 50, connections=[2])
        circle2 = self._create_test_circle(2, 100, 100, connections=[1])
        self.app.circles = [circle1, circle2]
        self.app.circle_lookup = {1: circle1, 2: circle2}

        with patch.object(self.app.connection_manager, 'calculate_connection_entry_angle', return_value=90):
            viz_ids = self.app.ui_manager.draw_connection_angle_visualizations("1_2")

        # Verify visualization lines are created
        self.assertEqual(len(viz_ids), 2)
        self.app.canvas.create_line.assert_called()
