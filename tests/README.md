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

## Test Coverage

The tests cover the following functionality:

1. Application initialization
2. Drawing on click
3. Canvas resizing (increase/decrease)
4. Minimum canvas size constraint

## Adding New Tests

When adding new features to the application, please also add corresponding tests:

1. Create a new test method in an existing test class for minor features
2. Create a new test class for major features
3. Follow the naming convention `test_feature_name`

Remember to run the tests before submitting a pull request.