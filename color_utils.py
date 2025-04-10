"""
Color Utility Module for the 4colour project.

This module provides functions for working with colors and their priorities.
"""

# Define color priority mappings
# Priority order: 1=yellow (lowest), 2=green, 3=blue, 4=red (highest)
COLOR_PRIORITY = {
    1: "yellow",
    2: "green",
    3: "blue",
    4: "red"
}

def get_color_from_priority(priority):
    """Get the color name corresponding to a given priority.
    
    Args:
        priority (int): The priority number (1-4)
        
    Returns:
        str: The color name, or "black" if priority is invalid
    """
    return COLOR_PRIORITY.get(priority, "black") # Default to black if invalid
