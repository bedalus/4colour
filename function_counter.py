"""
Function call counter for the 4colour project.

This module provides functionality to count how many times specific functions are called.
"""

# Dictionary to store function call counts
function_calls = {
    "canvas_app.CanvasApplication.get_connection_curve_offset": 0,
    "canvas_app.CanvasApplication.clear_warning": 0,
    "canvas_app.CanvasApplication.show_warning": 0,
    "circle_manager.CircleManager.handle_last_circle_removed": 0,
    "canvas_app.CanvasApplication._calculate_corrected_angle": 0,
    "canvas_app.CanvasApplication._calculate_midpoint": 0,
    "canvas_app.CanvasApplication._calculate_midpoint_handle_position": 0, 
    "canvas_app.CanvasApplication._drag_midpoint_motion": 0,
    "canvas_app.CanvasApplication._draw_midpoint_handle": 0,
    "ui_manager.UIManager.set_active_circle": 0
}

def increment_counter(function_name):
    """Increment the call counter for a specific function.
    
    Args:
        function_name: Full name of the function (module.class.function)
    """
    if function_name in function_calls:
        function_calls[function_name] += 1
        
def get_call_counts():
    """Get all function call counts.
    
    Returns:
        dict: Dictionary with function names as keys and call counts as values
    """
    return function_calls.copy()

def reset_counters():
    """Reset all function call counters to zero."""
    for key in function_calls:
        function_calls[key] = 0
