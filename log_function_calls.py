"""
Script to run the 4colour application with function call logging.

This script instruments the 4colour modules and runs the application,
logging all function calls to the specified log files.
"""

import sys
import os
import importlib
from function_logger import initialize, instrument_modules

def main():
    """Main function to run the 4colour application with logging."""
    # Initialize the logger
    initialize()
    
    # List of modules to instrument
    modules_to_instrument = [
        'canvas_app',
        'ui_manager',
        'circle_manager',
        'connection_manager',
        'interaction_handler',
        'color_manager',
        'color_utils',
        'app_enums'
    ]
    
    # Instrument all modules
    print("Instrumenting modules...")
    instrumented_modules = instrument_modules(modules_to_instrument)
    
    # Import canvas_app for running the application
    canvas_app = instrumented_modules.get('canvas_app')
    if not canvas_app:
        print("Failed to instrument canvas_app module")
        return
    
    print(f"Function calls will be logged to:")
    print(f"  - Key log: function_key_log.txt")
    print(f"  - Call log: function_call_log.txt")
    print("\nStarting application...")
    
    # Run the application
    try:
        canvas_app.main()
    except Exception as e:
        print(f"Error running application: {e}")

if __name__ == "__main__":
    main()
