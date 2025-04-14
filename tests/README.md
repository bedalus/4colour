# Unit Tests for 4colour Canvas Application

This directory contains unit tests for the 4colour canvas application.

## Running the Tests

To run all tests, from the project root directory:

```bash
python -m unittest discover tests
```

To run a specific test file:

```bash
python -m unittest tests/test_canvas_app.py
```

To run a specific test case or method:

```bash
python -m unittest tests.test_canvas_app.TestCanvasApplication.test_initialization
```

## Test Coverage Analysis

To analyze test coverage and identify gaps:

1. Install the coverage package if not already installed:
   ```bash
   pip install coverage
   ```

2. Run the coverage analysis script:
   ```bash
   python -m tests.run_coverage
   ```

3. This will:
   - Run all tests with coverage measurement
   - Generate an HTML report in the "htmlcov" directory
   - Automatically open the report in your default web browser
   - Show a summary in the console

4. Use this report to identify code that's not being tested and add tests accordingly.

## Test Coverage

The tests cover the following functionality:

1. Application initialization and fixed node setup
2. Drawing on click and boundary maintenance
3. Mode transitions (CREATE, SELECTION, ADJUST)
4. Circle and connection management
5. Color assignment and conflict resolution
6. Boundary traversal and enclosure detection
7. Fixed nodes and proximity restrictions
8. Curve connections and midpoint manipulation

## Adding New Tests

When adding new features to the application, please also add corresponding tests:

1. Create a new test method in an existing test class for minor features
2. Create a new test class for major features
3. Follow the naming convention `test_feature_name`

### Test Utilities

The `test_utils.py` file provides several helper methods to simplify test creation:

- `_create_test_circle()` - Creates a circle with standard attributes
- `_create_fixed_test_circle()` - Creates a fixed circle node
- `_setup_fixed_nodes()` - Sets up the standard fixed nodes A and B
- `_setup_graph_with_enclosure()` - Creates a test graph with enclosed nodes
- `_simulate_boundary_traversal()` - Simulates boundary traversal algorithm

Remember to run the tests before submitting a pull request.