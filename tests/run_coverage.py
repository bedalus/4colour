"""
Test coverage analysis script for the 4colour project.

This script runs the test suite with coverage measurement and generates
a coverage report to identify gaps in test coverage.

Usage:
    python -m tests.run_coverage
"""

import os
import sys
import unittest
import coverage
import webbrowser

def run_coverage():
    """Run tests with coverage and generate a report."""
    print("Starting coverage measurement...")
    
    # Initialize coverage.py
    cov = coverage.Coverage(
        source=["canvas_app", "ui_manager", "circle_manager", "connection_manager",
                "color_manager", "color_utils", "boundary_manager", "app_enums",
                "interaction_handler"],
        omit=["*/__pycache__/*", "*/tests/*", "*/site-packages/*"]
    )
    
    # Start coverage measurement
    cov.start()
    
    # Run tests
    print("\nRunning test suite...\n")
    test_loader = unittest.defaultTestLoader
    test_suite = test_loader.discover(os.path.dirname(os.path.abspath(__file__)), pattern="test_*.py")
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Stop coverage measurement
    cov.stop()
    cov.save()
    
    # Report results
    print("\nTest Results:")
    print(f"  Run: {result.testsRun}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Failures: {len(result.failures)}")
    
    # Generate report
    print("\nGenerating coverage report...")
    
    # Create directory for HTML report
    report_dir = "htmlcov"
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    
    # Generate HTML report
    cov.html_report(directory=report_dir)
    
    # Display report summary
    cov_report = cov.report()
    print(f"\nCoverage: {cov_report:.1f}%")
    
    # Open report in browser
    report_path = os.path.join(os.path.abspath(report_dir), "index.html")
    print(f"\nDetailed coverage report available at: {report_path}")
    
    try:
        webbrowser.open(f"file://{report_path}")
        print("Coverage report opened in web browser.")
    except Exception as e:
        print(f"Could not open browser automatically: {e}")
        print("Please open the report manually using the path above.")
    
    return result

if __name__ == "__main__":
    run_coverage()
