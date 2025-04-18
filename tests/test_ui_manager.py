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
        # Create a mock command function
        mock_func = MagicMock()
        
        # Call the focus_after method
        self.app.ui_manager.focus_after(mock_func)
        
        # Verify the mock function was called and focus was set
        mock_func.assert_called_once()
        self.app.debug_button.focus_set.assert_called_once()
    
    def test_toggle_debug_enable(self):
        """Test enabling the debug display."""
        # Setup initial state
        self.app.debug_enabled = False
        self.app.debug_text = None
        
        # Mock the show_debug_info method
        with patch.object(self.app.ui_manager, 'show_debug_info') as mock_show_debug:
            # Call toggle_debug
            self.app.ui_manager.toggle_debug()
            
            # Verify the debug state was toggled and show_debug_info was called
            self.assertTrue(self.app.debug_enabled)
            mock_show_debug.assert_called_once()
    
    def test_toggle_debug_disable(self):
        """Test disabling the debug display."""
        # Setup initial state
        self.app.debug_enabled = True
        self.app.debug_text = 100  # Mock text ID
        
        # Call toggle_debug
        self.app.ui_manager.toggle_debug()
        
        # Verify the debug state was toggled and text was deleted
        self.assertFalse(self.app.debug_enabled)
        self.app.canvas.delete.assert_called_once_with(100)
        self.assertIsNone(self.app.debug_text)
    
    def test_set_active_circle(self):
        """Test setting a single active circle for debug info."""
        # Call set_active_circle
        self.app.ui_manager.set_active_circle(1)
        
        # Verify active_circle_id was set
        self.assertEqual(self.app.ui_manager.active_circle_id, 1)
    
    def test_set_active_circles(self):
        """Test setting multiple active circles for debug info."""
        # Call set_active_circles with multiple IDs
        self.app.ui_manager.set_active_circles(1, 2, 3)
        
        # Verify active_circle_ids was set correctly
        self.assertEqual(self.app.ui_manager.active_circle_ids, [1, 2, 3])
    
    def test_show_debug_info_with_circle(self):
        """Test showing debug info for a circle."""
        # Setup a circle
        circle = {
            "id": 1,
            "canvas_id": 100,
            "x": 50,
            "y": 50,
            "color_priority": 3,  # Priority 3 is blue
            "connected_to": [2],
            "ordered_connections": [2],
            "enclosed": False
        }
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}
        
        # Create canvas.create_text mock return value
        self.app.canvas.create_text.return_value = 200
        
        # Call show_debug_info
        self.app.ui_manager.show_debug_info()
        
        # Verify canvas.create_text was called
        self.app.canvas.create_text.assert_called_once()
        args, kwargs = self.app.canvas.create_text.call_args
        
        # Verify the text contains expected information
        self.assertEqual(kwargs['anchor'], tk.NE)
        self.assertIn("1", kwargs['text'])  # Circle ID
        self.assertIn("(50, 50)", kwargs['text'])  # Position
        self.assertIn("3", kwargs['text'])  # Color priority
        self.assertIn("2", kwargs['text'])  # Connected to
        
        # Verify debug_text was set
        self.assertEqual(self.app.debug_text, 200)
    
    def test_show_debug_info_multiple_active_circles(self):
        """Test showing debug info for multiple active circles."""
        # Setup circles
        circle1 = self._create_test_circle(1, 50, 50, priority=1, connections=[2])
        circle2 = self._create_test_circle(2, 100, 100, priority=2, connections=[1])
        self.app.circles = [circle1, circle2]
        self.app.circle_lookup = {1: circle1, 2: circle2}
        
        # Set active circle IDs
        self.app.ui_manager.active_circle_ids = [1, 2]
        
        # Create canvas.create_text mock return value
        self.app.canvas.create_text.return_value = 200
        
        # Call show_debug_info
        self.app.ui_manager.show_debug_info()
        
        # Verify canvas.create_text was called
        self.app.canvas.create_text.assert_called_once()
        
        # Verify active_circle_ids was reset
        self.assertEqual(self.app.ui_manager.active_circle_ids, [])
    
    def test_show_debug_info_no_circles(self):
        """Test showing debug info when no circles are present."""
        # Setup empty circles list
        self.app.circles = []
        
        # Create canvas.create_text mock return value
        self.app.canvas.create_text.return_value = 200
        
        # Call show_debug_info
        self.app.ui_manager.show_debug_info()
        
        # Verify canvas.create_text was called with correct message
        self.app.canvas.create_text.assert_called_once()
        args, kwargs = self.app.canvas.create_text.call_args
        self.assertEqual(kwargs['text'], "No circles drawn yet")
        
        # Verify debug_text was set
        self.assertEqual(self.app.debug_text, 200)
    
    def test_format_circle_info(self):
        """Test formatting circle info for display."""
        # Create a test circle
        circle = {
            "id": 1,
            "x": 50,
            "y": 50,
            "color_priority": 2,
            "connected_to": [2, 3],
            "ordered_connections": [3, 2],
            "enclosed": True
        }
        
        # Format the circle info
        formatted_info = self.app.ui_manager._format_circle_info(circle)
        
        # Verify the formatted info contains expected information
        self.assertIn("1 : Circle ID", formatted_info)
        self.assertIn("(50, 50) : Position", formatted_info)
        self.assertIn("green (priority: 2) : Color", formatted_info)
        self.assertIn("2, 3 : Connected to", formatted_info)
        self.assertIn("3→2 : Clockwise order", formatted_info)
        self.assertIn("True : Enclosed", formatted_info)
    
    def test_format_circle_info_missing_fields(self):
        """Test formatting circle info with missing fields."""
        # Create a circle with missing fields
        circle = {
            "id": 1,
            "x": 50,
            "y": 50,
            "color_priority": 1,
            "connected_to": [],
            "enclosed": False  # Add the enclosed field with default value
            # Missing ordered_connections
        }
        
        # Format the circle info
        formatted_info = self.app.ui_manager._format_circle_info(circle)
        
        # Verify the formatted info handles missing fields gracefully
        self.assertIn("1 : Circle ID", formatted_info)
        self.assertIn("(50, 50) : Position", formatted_info)
        self.assertIn("None : Clockwise order", formatted_info)
        self.assertIn("False : Enclosed", formatted_info)
    
    def test_show_hint_text(self):
        """Test displaying the hint text in selection mode."""
        # Setup canvas width
        self.app.canvas_width = 700
        
        # Create canvas.create_text mock return value
        self.app.canvas.create_text.return_value = 300
        
        # Call show_hint_text
        self.app.ui_manager.show_hint_text()
        
        # Verify canvas.create_text was called with correct parameters
        self.app.canvas.create_text.assert_called_once()
        args, kwargs = self.app.canvas.create_text.call_args
        self.assertEqual(args[0], 350)  # Half of canvas_width
        self.assertEqual(args[1], 20)
        self.assertIn("Please select which circles to connect to then press", kwargs['text'])
        self.assertEqual(kwargs['anchor'], tk.N)
        
        # Verify hint_text_id was set
        self.assertEqual(self.app.hint_text_id, 300)
    
    def test_show_hint_text(self):
        """Test displaying edit mode hint text."""
        # Setup initial state
        self.app.hint_text_id = 100
        self.app.edit_hint_text_id = None
        self.app.canvas_width = 700
        
        # Create canvas.create_text mock return value
        self.app.canvas.create_text.return_value = 200
        
        # Call show_hint_text
        self.app.ui_manager.show_hint_text()
        
        # Verify hint_text_id was cleared
        self.app.canvas.delete.assert_called_once_with(100)
        self.assertIsNone(self.app.hint_text_id)
        
        # Verify edit_hint_text was created
        self.app.canvas.create_text.assert_called_once()
        args, kwargs = self.app.canvas.create_text.call_args
        self.assertEqual(args[0], (700 // 2) + 20)  # (canvas_width/2) + 20
        self.assertEqual(args[1], 20)
        self.assertIn("Click-and-drag to move circles and handles", kwargs['text'])
        self.assertEqual(kwargs['anchor'], tk.N)
        
        # Verify edit_hint_text_id was set
        self.assertEqual(self.app.edit_hint_text_id, 200)
    
    def test_clear_canvas(self):
        """Test clearing the canvas."""
        # Setup initial state with some data
        self.app.circles = [{"id": 1}]
        self.app.drawn_items = [(50, 50)]
        self.app.circle_lookup = {1: {"id": 1}}
        self.app.connections = {"1_2": {}}
        self.app.midpoint_handles = {"1_2": 300}
        self.app.last_circle_id = 1
        self.app.next_id = 2
        self.app.debug_text = 400
        
        # Mock _initialize_fixed_nodes to avoid adding fixed nodes
        with patch.object(self.app, '_initialize_fixed_nodes'):
            # Call clear_canvas
            self.app.ui_manager.clear_canvas()
            
            # Verify everything was cleared
            self.app.canvas.delete.assert_called_with("all")
            self.assertEqual(len(self.app.drawn_items), 0)
            self.assertEqual(len(self.app.circles), 0)
            self.assertEqual(len(self.app.circle_lookup), 0)
            self.assertEqual(len(self.app.connections), 0)
            self.assertEqual(len(self.app.midpoint_handles), 0)
            self.assertIsNone(self.app.last_circle_id)
            self.assertEqual(self.app.next_id, 1)
            self.assertIsNone(self.app.debug_text)
            
            # Verify application mode was set to CREATE
            self.assertEqual(self.app._mode, ApplicationMode.CREATE)
            
            # Verify _initialize_fixed_nodes was called
            self.app._initialize_fixed_nodes.assert_called_once()
    
    def test_draw_angle_visualization_line(self):
        """Test drawing an angle visualization line."""
        # Setup a circle
        circle = self._create_test_circle(1, 100, 100)
        self.app.circles = [circle]
        self.app.circle_lookup = {1: circle}
        self.app.circle_radius = 10
        
        # Setup canvas.create_line mock return value
        self.app.canvas.create_line.return_value = 101
        
        # Call draw_angle_visualization_line
        line_id = self.app.ui_manager.draw_angle_visualization_line(1, 2, 90)
        
        # Verify create_line was called
        self.app.canvas.create_line.assert_called_once()
        
        # Verify the line ID was returned
        self.assertEqual(line_id, 101)
    
    def test_draw_connection_angle_visualizations_valid_key(self):
        """Test drawing connection angle visualizations with a valid key."""
        # Setup circles
        circle1 = self._create_test_circle(1, 50, 50, connections=[2])
        circle2 = self._create_test_circle(2, 100, 100, connections=[1])
        self.app.circles = [circle1, circle2]
        self.app.circle_lookup = {1: circle1, 2: circle2}
        
        # Mock calculate_connection_entry_angle
        with patch.object(self.app.connection_manager, 'calculate_connection_entry_angle', return_value=90):
            # Mock draw_angle_visualization_line to return IDs
            with patch.object(self.app.ui_manager, 'draw_angle_visualization_line', side_effect=[101, 102]):
                # Call draw_connection_angle_visualizations
                viz_ids = self.app.ui_manager.draw_connection_angle_visualizations("1_2")
                
                # Verify visualization lines were created
                self.assertEqual(len(viz_ids), 2)
                self.assertEqual(viz_ids, [101, 102])
                
                # Verify draw_angle_visualization_line was called twice
                self.assertEqual(self.app.ui_manager.draw_angle_visualization_line.call_count, 2)
    
    def test_draw_connection_angle_visualizations_invalid_key(self):
        """Test drawing connection angle visualizations with an invalid key."""
        # Call with invalid key
        viz_ids = self.app.ui_manager.draw_connection_angle_visualizations("invalid_key")
        
        # Verify empty list was returned
        self.assertEqual(viz_ids, [])
    
    def test_clear_angle_visualizations(self):
        """Test clearing angle visualizations."""
        # Setup mock visualization items
        # (These canvas IDs would normally be returned from draw_connection_angle_visualizations)
        mock_viz_ids = [101, 102, 103]
        
        # Call clear_angle_visualizations
        self.app.ui_manager.clear_angle_visualizations()
        
        # Verify canvas.delete was called with the 'angle_viz' tag
        self.app.canvas.delete.assert_called_with('angle_viz')

    def test_clear_angle_visualizations_no_items(self):
        """Test clearing angle visualizations when no items are present."""
        # Call clear_angle_visualizations
        self.app.ui_manager.clear_angle_visualizations()
        
        # Verify canvas.delete was still called with the tag
        # (The implementation always calls delete with the tag, even if there are no items)
        self.app.canvas.delete.assert_called_with('angle_viz')
    
    def test_ui_state_changes_during_mode_transitions(self):
        """Test UI state changes during different mode transitions."""
        # Test CREATE to ADJUST transition
        # Setup initial state
        self.app._mode = ApplicationMode.CREATE
        
        # Mock required methods
        with patch.object(self.app.ui_manager, 'show_hint_text') as mock_edit_hint:
            with patch.object(self.app.connection_manager, 'show_midpoint_handles') as mock_handles:
                # Transition to ADJUST mode
                self.app._set_application_mode(ApplicationMode.ADJUST)
                
                # Verify UI state changes
                mock_edit_hint.assert_called_once()
                mock_handles.assert_called_once()
                self.assertEqual(self.app._mode, ApplicationMode.ADJUST)
                self.app.canvas.config.assert_called_with(bg="#FFEEEE")  # Pink background
        
        # Test ADJUST to CREATE transition
        # Setup initial state
        self.app._mode = ApplicationMode.ADJUST
        self.app.edit_hint_text_id = 200
        
        # Mock required methods
        with patch.object(self.app.connection_manager, 'hide_midpoint_handles') as mock_hide:
            # Transition to CREATE mode
            self.app._set_application_mode(ApplicationMode.CREATE)
            
            # Verify UI state changes
            mock_hide.assert_called_once()
            self.assertEqual(self.app._mode, ApplicationMode.CREATE)
            self.app.canvas.config.assert_called_with(bg="white")  # White background
            self.app.canvas.delete.assert_called_with(200)  # Delete edit hint text
