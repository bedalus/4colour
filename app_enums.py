"""
Application enums for the 4colour project.

This module contains enumerations used throughout the application.
"""

from enum import Enum, auto

class ApplicationMode(Enum):
    """Enum representing the different modes of the application."""
    CREATE = auto()
    SELECTION = auto()
    ADJUST = auto()
