"""
Color Utility Module for the 4colour project.

This module provides functions for working with colors and their priorities.
"""

# Define color priority mappings
# Priority order: 1=yellow (lowest), 2=green, 3=blue, 4=red, 5=black (highest)
COLOR_PRIORITY = {
    1: "yellow",
    2: "green",
    3: "blue",
    4: "red",
    5: "black"
}

def get_color_from_priority(priority):
    """Get the color name corresponding to a given priority."""
    return COLOR_PRIORITY.get(priority)

def find_lowest_available_priority(used_priorities):
    """Find the lowest color priority that isn't in the used_priorities set.
    
    Args:
        used_priorities (set): Set of priority numbers already in use
        
    Returns:
        int or None: The lowest available priority (1-4), or None if all are used
    """
    for priority in range(1, 5):  # Check priorities 1, 2, 3, 4
        if priority not in used_priorities:
            return priority
    return None  # All priorities 1-4 are used

def determine_color_priority_for_connections(connected_priorities):
    """Determine the appropriate color priority given connected circles' priorities.
    
    This implements the core 4-color algorithm logic:
    1. If there are no connections, use priority 1 (yellow)
    2. Otherwise, use the lowest priority not used by any connected circle
    3. If all priorities 1-4 are used, return priority 5 (black)
    
    Args:
        connected_priorities (set): Set of priorities used by connected circles
        
    Returns:
        int: The appropriate color priority to use
    """
    if not connected_priorities:
        return 1  # Default to lowest priority
        
    # Find lowest unused priority
    available_priority = find_lowest_available_priority(connected_priorities)
    
    # If all priorities 1-4 are used, return priority 5 (black)
    return available_priority if available_priority is not None else 5
