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

Completed items are marked with `[x]`. New work items should be itemized and preceded by an empty checkbox (`- [ ]`).

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

- [x] **Implement Circle Coloring:**
    *   Assign a color to each new circle.
    *   Available colors: green, blue, red, yellow.
    *   Initially, implement random color assignment by calling a dedicated function. Logic for non-random coloring will be added later.
- [x] **Method to Connect Circles:**
    *   Draw a straight line connecting each newly added circle to the previously added circle.
- [x] **Collect Data to Track the Circles:**
    *   Create a data store to collect information about each circle when it is drawn on the canvas.
    *   Ensure the storage method is versatile enough to be updated with new attributes as this be required in a future phase.
    *   Store its coordinates (x, y).
    *   Store a unique numerical identifier (ID) incrementing from 1 upward for each new circle.
    *   Store its color.
    *   When a connecting line is added, store the ID of the other circle it has been connected to.
- [x] **Circle Data Debug display option:**
    *   Add a debug button
    *   When clicked this button should add an overlay that shows the data collected for the most recent circle

### Phase 3: Advanced Circle Connection

This phase introduces a more interactive way to connect circles.

- [ ] **Modify Connection Trigger:**
    *   Change the connection logic: Instead of automatically connecting to the *last* circle, connections will be made based on user selection *after* placing a new circle. This new logic applies only *after* the very first circle has been placed.
- [ ] **Implement Hint Text:**
    *   After the first circle is placed, display instructional text near the control buttons (e.g., "Please select which circles to connect to then press space").
    *   This text should only be visible when the application is waiting for the user to select circles for connection.
- [ ] **Enable Circle Selection Mode:**
    *   After placing a new circle (subsequent to the first one), enter a "selection mode".
    *   In this mode, clicking on the canvas should *not* draw a new circle but instead attempt to select an existing circle.
- [ ] **Implement Click Detection on Circles:**
    *   Develop a function `get_circle_at_coords(x, y)` that returns the ID of the circle located at the given canvas coordinates (x, y), considering the `circle_radius`.
    *   Return `None` if no circle is found at the clicked location.
    *   Bind the left mouse click event (`<Button-1>`) in selection mode to call this function.
- [ ] **Visual Selection Indicator:**
    *   Maintain a list of currently selected circle IDs.
    *   When a user clicks on a circle in selection mode:
        *   If the circle is *not* selected, add its ID to the selection list and draw a visual indicator (e.g., a short horizontal line directly beneath the circle) on the canvas. Store the canvas ID of this indicator line.
        *   If the circle is *already* selected, remove its ID from the selection list and delete its corresponding indicator line from the canvas.
- [ ] **Confirm Selection with Spacebar:**
    *   Bind the spacebar key press event (`<space>`) to a confirmation function.
    *   When the spacebar is pressed:
        *   Exit selection mode.
        *   For each circle ID in the selection list, call the `add_connection` method to connect the *newly placed* circle to the *selected* circle.
        *   Clear the selection list.
        *   Remove all visual selection indicators from the canvas.
        *   Hide the instructional hint text.
        *   Re-enable the standard click-to-draw behavior for the next circle.
