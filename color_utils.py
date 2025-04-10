"""
Color Utility Module for the 4colour project.

This module provides functions for working with colors and their priorities.
"""

# Define color priority mappings
# Priority order: 1=yellow (lowest), 2=green, 3=blue, 4=red (highest)
COLOR_PRIORITY = {
    "yellow": 1,
    "green": 2,
    "blue": 3,
    "red": 4
}

PRIORITY_COLOR = {
    1: "yellow",
    2: "green",
    3: "blue",
    4: "red"
}

def get_color_from_priority(priority):
    """Get color name from priority number.
    
    Args:
        priority: Integer priority number (1-4)
        
    Returns:
        str: Color name corresponding to the priority
    
    Raises:
        ValueError: If priority is not in the valid range
    """
    if priority not in PRIORITY_COLOR:
        raise ValueError(f"Invalid color priority: {priority}. Must be between 1 and 4.")
    return PRIORITY_COLOR[priority]

def get_priority_from_color(color):
    """Get priority number from color name.
    
    Args:
        color: String color name
        
    Returns:
        int: Priority number corresponding to the color
    
    Raises:
        ValueError: If color is not in the valid set
    """
    if color not in COLOR_PRIORITY:
        raise ValueError(f"Invalid color: {color}. Must be one of {list(COLOR_PRIORITY.keys())}.")
    return COLOR_PRIORITY[color]

def get_all_colors():
    """Get a list of all valid colors.
    
    Returns:
        list: List of all valid color names
    """
    return list(COLOR_PRIORITY.keys())
