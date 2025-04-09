# Contribution Guidelines

NOTE: These guidelines apply only to code in the 4colour repo.

## Coding Standards
- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python or equivalent standards for other languages.
- Use meaningful variable and function names.
- Write modular, reusable, and succinctly documented code. To avoid clutter, do not document self-explanatary code.

## General Rules
- Always include comments for complex logic.
- Avoid hardcoding values; use configuration files or constants.
- Write unit tests for all new features or changes. Include documentation for running the unit tests in a top level folder called 'tests'

## Project-Specific Rules
- Use `snake_case` for variables and functions.
- Use `PascalCase` for classes.
- Ensure all code passes linting and formatting checks before committing.
- Use lowercase names for folders.
- Even though I am English, use the American spelling of colour, i.e. color

## Commit Messages
- Use descriptive commit messages.
- Follow the format: `<type>: <short description>` (e.g., `feat: add user authentication`).

## Planning

Completed items are marked with `[x]`.

### Coding Plan

The initial phase focuses on creating the user interface using `tkinter`.

- [x] **Setup Tkinter Window:**
    *   Create the main application window.
    *   Set the window title and initial size.
- [x] **Create Canvas Widget:**
    *   Add a `tkinter.Canvas` widget to the main window.
    *   Configure the canvas dimensions and background color.
- [x] **Implement Drawing on Click:**
    *   Bind mouse click events to the canvas.
    *   Implement simple functions to draw a small circle on the canvas wherever the user has clicked.
- [x] **Add Clear Canvas Control:**
    *   Create a 'Clear Canvas' button.
    *   Position the button in a control frame above the canvas.
    *   Implement function to clear all drawings from the canvas when pressed.

### Phase 2: Basic Canvas Functionality

This phase introduces more capabilities to the canvas application.

- [ ] **Implement Circle Coloring:**
    *   Assign a color to each new circle.
    *   Available colors: green, blue, red, yellow.
    *   Initially, implement random color assignment by calling a dedicated function. Logic for non-random coloring will be added later.
- [ ] **Method to Connect Circles:**
    *   Draw a straight line connecting each newly added circle to the previously added circle.
- [ ] **Collect Data to Track the Circles:**
    *   Create a data store to collect information about each circle when it is drawn on the canvas.
    *   Ensure the storage method is versatile enough to be updated with new attributes as this be required in a future phase.
    *   Store its coordinates (x, y).
    *   Store a unique numerical identifier (ID) incrementing from 1 upward for each new circle.
    *   Store its color.
    *   When a connecting line is added, store the ID of the other circle it has been connected to.
- [ ] **Circle Data Debug display option:**
    *   Add a debug button
    *   When clicked this button should add an overlay that shows the data collected for the most recent circle
