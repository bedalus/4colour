"""
Unit tests for color_utils.py.
"""

import unittest
import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from color_utils import get_color_from_priority, find_lowest_available_priority, determine_color_priority_for_connections

class TestColorUtils(unittest.TestCase):
    """Test cases for the color utility functions."""
    
    def test_get_color_from_priority(self):
        """Test converting priority numbers to color names."""
        self.assertEqual(get_color_from_priority(1), "yellow")
        self.assertEqual(get_color_from_priority(2), "green")
        self.assertEqual(get_color_from_priority(3), "blue")
        self.assertEqual(get_color_from_priority(4), "red")
        
        # Test invalid priority
        self.assertEqual(get_color_from_priority(0), "black")
        self.assertEqual(get_color_from_priority(5), "black")
    
    def test_find_lowest_available_priority(self):
        """Test finding the lowest available priority."""
        # Test with no priorities used
        self.assertEqual(find_lowest_available_priority(set()), 1)
        
        # Test with some priorities used
        self.assertEqual(find_lowest_available_priority({1}), 2)
        self.assertEqual(find_lowest_available_priority({2}), 1)
        self.assertEqual(find_lowest_available_priority({1, 3}), 2)
        self.assertEqual(find_lowest_available_priority({1, 2}), 3)
        
        # Test with all priorities 1-3 used
        self.assertIsNone(find_lowest_available_priority({1, 2, 3}))
    
    def test_determine_color_priority_for_connections(self):
        """Test determining color priority based on connected circles."""
        # No connections
        self.assertEqual(determine_color_priority_for_connections(set()), 1)
        
        # One connection with priority 1
        self.assertEqual(determine_color_priority_for_connections({1}), 2)
        
        # Multiple connections with different priorities
        self.assertEqual(determine_color_priority_for_connections({1, 3}), 2)
        
        # All lower priorities used
        self.assertEqual(determine_color_priority_for_connections({1, 2, 3}), 4)

if __name__ == "__main__":
    unittest.main()
