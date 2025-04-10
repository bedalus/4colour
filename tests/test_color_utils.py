"""
Unit tests for the color_utils module.

This module contains tests for the color utility functions.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import the color_utils module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from color_utils import get_color_from_priority, get_priority_from_color, get_all_colors

class TestColorUtils(unittest.TestCase):
    """Test cases for the color utility functions."""
    
    def test_get_color_from_priority(self):
        """Test converting priority numbers to color names."""
        self.assertEqual(get_color_from_priority(1), "yellow")
        self.assertEqual(get_color_from_priority(2), "green")
        self.assertEqual(get_color_from_priority(3), "blue")
        self.assertEqual(get_color_from_priority(4), "red")
        
        # Test invalid priority
        with self.assertRaises(ValueError):
            get_color_from_priority(0)
        with self.assertRaises(ValueError):
            get_color_from_priority(5)
    
    def test_get_priority_from_color(self):
        """Test converting color names to priority numbers."""
        self.assertEqual(get_priority_from_color("yellow"), 1)
        self.assertEqual(get_priority_from_color("green"), 2)
        self.assertEqual(get_priority_from_color("blue"), 3)
        self.assertEqual(get_priority_from_color("red"), 4)
        
        # Test invalid color
        with self.assertRaises(ValueError):
            get_priority_from_color("purple")
    
    def test_get_all_colors(self):
        """Test getting the list of all valid colors."""
        colors = get_all_colors()
        self.assertIsInstance(colors, list)
        self.assertEqual(len(colors), 4)
        self.assertIn("yellow", colors)
        self.assertIn("green", colors)
        self.assertIn("blue", colors)
        self.assertIn("red", colors)

if __name__ == "__main__":
    unittest.main()
