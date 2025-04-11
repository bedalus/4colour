"""
Unit tests for application enumerations.

This module contains tests for the ApplicationMode enum.
"""

import unittest
from app_enums import ApplicationMode

class TestApplicationMode(unittest.TestCase):
    """Test cases for the ApplicationMode enum."""
    
    def test_application_mode_values(self):
        """Test that ApplicationMode enum has the correct values."""
        self.assertIn(ApplicationMode.CREATE, ApplicationMode)
        self.assertIn(ApplicationMode.SELECTION, ApplicationMode)
        self.assertIn(ApplicationMode.ADJUST, ApplicationMode)
        
        # Test that enum values are unique
        self.assertNotEqual(ApplicationMode.CREATE, ApplicationMode.SELECTION)
        self.assertNotEqual(ApplicationMode.CREATE, ApplicationMode.ADJUST)
        self.assertNotEqual(ApplicationMode.SELECTION, ApplicationMode.ADJUST)
