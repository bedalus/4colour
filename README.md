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

Completed items are marked with `[x]`. New work items should be itemized and preceded by an empty checkbox (`- [ ]`). When implementing features, follow the requirements of the next unmarked checkbox. Once a feature is fully implemented and tested, mark the checkbox as complete to track progress.

## Test-Driven Development

To ensure smooth development and avoid regressions:

- Update unit tests whenever functionality changes - this is as important as the implementation itself.
- Tests should be updated to match the new behavior, not the other way around.
- Run tests before and after making changes to verify that your implementation works correctly.
- If a test fails, understand whether it's because of a bug in the implementation or because the test needs to be updated for new behavior.
- All new features must have corresponding tests in the `tests` directory.
- Consider writing tests before implementing a feature to clarify expected behavior.

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

- [x] **Modify Connection Trigger:**
    *   Change the connection logic: Instead of automatically connecting to the *last* circle, connections will be made based on user selection *after* placing a new circle. This new logic applies only *after* the very first circle has been placed.
- [x] **Implement Hint Text:**
    *   After the first circle is placed, display instructional text near the control buttons (e.g., "Please select which circles to connect to then press space").
    *   This text should only be visible when the application is waiting for the user to select circles for connection.
- [x] **Enable Circle Selection Mode:**
    *   After placing a new circle (subsequent to the first one), enter a "selection mode".
    *   In this mode, clicking on the canvas should *not* draw a new circle but instead attempt to select an existing circle.
- [x] **Implement Click Detection on Circles:**
    *   Develop a function `get_circle_at_coords(x, y)` that returns the ID of the circle located at the given canvas coordinates (x, y), considering the `circle_radius`.
    *   Return `None` if no circle is found at the clicked location.
    *   Bind the left mouse click event (`<Button-1>`) in selection mode to call this function.
- [x] **Visual Selection Indicator:**
    *   Maintain a list of currently selected circle IDs.
    *   When a user clicks on a circle in selection mode:
        *   If the circle is *not* selected, add its ID to the selection list and draw a visual indicator (e.g., a short horizontal line directly beneath the circle) on the canvas. Store the canvas ID of this indicator line.
        *   If the circle is *already* selected, remove its ID from the selection list and delete its corresponding indicator line from the canvas.
- [x] **Confirm Selection with Spacebar:**
    *   Bind the spacebar key press event (`<space>`) to a confirmation function.
    *   When the spacebar is pressed:
        *   Exit selection mode.
        *   For each circle ID in the selection list, call the `add_connection` method to connect the *newly placed* circle to the *selected* circle.
        *   Clear the selection list.
        *   Remove all visual selection indicators from the canvas.
        *   Hide the instructional hint text.
        *   Re-enable the standard click-to-draw behavior for the next circle.

### Phase 4: Edit Mode

This phase introduces functionality to edit existing circles on the canvas.

- [x] **Add Edit Mode Button:**
    *   Create a new button labeled "Edit Mode" in the control frame.
    *   Implement logic to toggle an `in_edit_mode` state variable when the button is clicked.
- [x] **Implement Edit Mode Hint Text:**
    *   When entering edit mode, display instructional text (e.g., "Click-and-drag to move, right click to remove. Press space when done").
    *   Hide this text when exiting edit mode.
- [x] **Implement Circle Dragging:**
    *   Bind mouse press (`<Button-1>`), drag (`<B1-Motion>`), and release (`<ButtonRelease-1>`) events when in edit mode.
    *   On press, identify if the click is on an existing circle.
    *   On drag, update the position of the selected circle on the canvas.
    *   Continuously redraw connecting lines attached to the dragged circle during the drag motion.
    *   On release, update the circle's stored coordinates (x, y) in the `circles` list and `circle_lookup` dictionary.
- [x] **Implement Circle Removal:**
    *   Bind the right-click event (`<Button-3>`) when in edit mode.
    *   On right-click, identify if the click is on an existing circle using `get_circle_at_coords`.
    *   If a circle is right-clicked:
        *   Remove the circle's visual representation from the canvas.
        *   Remove all connecting lines associated with this circle from the canvas.
        *   Remove the circle's data from the `circles` list and `circle_lookup` dictionary.
        *   Iterate through the `connected_to` list of the removed circle. For each connected circle ID, update *its* `connected_to` list to remove the ID of the deleted circle.
        *   Remove relevant entries from the `connections` dictionary.
- [x] **Implement Exiting Edit Mode:**
    *   Bind the spacebar key press event (`<space>`) to an exit function when in edit mode.
    *   When spacebar is pressed:
        *   Set `in_edit_mode` to `False`.
        *   Hide the edit mode hint text.
        *   Ensure standard click-to-draw behavior is re-enabled (i.e., clicks should draw new circles again).

### Phase 5: Code Improvements and Refactoring

This phase focuses on improving the existing implementation by addressing edge cases, reducing redundancy, and enhancing code organization.

- [x] **Improve Mode Interaction:**
    *   Implement a proper state management system for application modes.
    *   Ensure that entering one mode (e.g., edit mode) properly exits other modes (e.g., selection mode).
    *   Add explicit checks in each mode-specific handler to verify the application is in the correct mode.
    *   Consider creating a `_set_application_mode(mode_name)` method that handles all transition logic.

### Phase 5 Debugging Notes

During the implementation and refinement of the application, several key improvements were made to enhance usability and code structure:

1. **Mode Management System**
   * Renamed modes to "CREATE" and "ADJUST" for better UI clarity
   * Implemented an `ApplicationMode` enum to represent the three distinct states
   * Created a centralized `_set_application_mode` method to handle all transitions
   * Added property getters/setters to maintain backward compatibility

2. **UI Improvements**
   * Enhanced the "Edit Mode" button to act as a clear toggle displaying the action it will perform:
     * Shows "Engage adjust mode" when in create mode
     * Shows "Engage create mode" when in adjust mode
   * Changed selection confirmation from spacebar to the 'y' key for better ergonomics
   * Updated hint text to reflect the new key binding
   * Implemented focus management to shift focus to the debug button after any button click

3. **Mode Transition Enhancement**
   * Simplified mode transitions with a clear toggle mechanism
   * Improved the logic for exiting selection mode
   * Removed the spacebar requirement for exiting adjust mode
   * Added automatic mode reset when the last circle is removed

4. **Event Handling Refinements**
   * Consolidated event binding management
   * Ensured proper cleanup of UI elements when switching modes
   * Improved the handling of overlapping hint text and debug information

All tests now pass, and the application provides clearer visual cues about its current state and available actions.

### Phase 6: Centralize Event Binding Management

This phase focuses on improving how mouse and keyboard events are managed across different application modes (CREATE, ADJUST, SELECTION).

- [x] **Create Mode-Specific Binding Methods:**
    *   Implement `_bind_create_mode_events()` to bind events needed for drawing circles (e.g., `<Button-1>`).
    *   Implement `_bind_adjust_mode_events()` to bind events for moving/removing circles (e.g., `<Button-1>`, `<B1-Motion>`, `<ButtonRelease-1>`, `<Button-3>`).
    *   Implement `_bind_selection_mode_events()` to bind events for selecting circles to connect (e.g., `<Button-1>`, `<y>`).
    *   Ensure appropriate focus management is handled within each binding method.
- [x] **Create Corresponding Unbinding Methods:**
    *   Implement `_unbind_create_mode_events()`, `_unbind_adjust_mode_events()`, and `_unbind_selection_mode_events()` to remove the specific bindings for each mode. Use `self.canvas.unbind(...)` for each event bound in the corresponding bind method.
    *   Add defensive checks to prevent errors when trying to unbind events that weren't bound.
    *   Consider using event tracking to ensure all bindings are properly managed.
- [x] **Refactor `_set_application_mode`:**
    *   Modify the `_set_application_mode` method.
    *   Before setting the new mode, call the appropriate unbinding method for the *current* mode to remove old bindings.
    *   After setting the new mode, call the appropriate binding method for the *new* mode to establish the correct event listeners.
    *   Add validation for mode transitions to prevent invalid state changes.
    *   Update UI elements (button text, hint text) consistently as part of the mode transition.
    *   Ensure all existing event bindings managed outside this new system (if any) are removed or integrated.
- [x] **Verify Event Handling:**
    *   Test transitions between CREATE, ADJUST, and SELECTION modes thoroughly.
    *   Confirm that only the events relevant to the current mode are active.
    *   Test edge cases such as rapid mode switching and interrupting operations mid-mode.
    *   Verify UI state consistency across all mode transitions.
    *   Ensure clicking, dragging, right-clicking, and key presses (`y`) behave correctly in each mode and do not trigger actions from other modes.
- [x] **Canvas background color for ADJUST mode:**
    *   When entering ADJUST mode, make the canvas background pale pink. Return to white when exiting this mode.

### Phase 7: Deferred Improvements

This phase includes improvements deferred from previous phases.

- [x] **Refactor Circle Removal Logic:**
    *   Consolidate the circle and connection removal code into a reusable helper method.
    *   Create a separate method for handling the "last circle removed" scenario.
    *   Ensure consistent cleanup when removing circles, whether through edit mode or through clearing the canvas.

### Phase 8: Deterministic Coloring

This phase introduces rule-based circle coloring to replace random coloring. Colors are assigned based on connections between circles to ensure connected circles never share the same color.

- [x] **Implement Color Priority System:**
    *   Define color priorities: 1=yellow (lowest), 2=green, 3=blue, 4=red (highest)
    *   Update circle data structure to store both color name and priority number
    *   Update debug display to show both color name and priority number
    *   Create a color utility module with functions to convert between priority numbers and color names
    *   Add unit tests for the new color utility functions

- [ ] **Implement Basic Color Assignment Logic:**
    *   Create a new function `_assign_color_based_on_connections()` to replace `_get_random_color()`
    *   When placing the first circle, always assign priority 1 (yellow)
    *   When placing subsequent circles, initially assign priority 1 (yellow)
    *   Update the circles' visual appearance to match their assigned colors
    *   Add appropriate unit tests for this basic functionality

- [ ] **Implement Connection-Aware Color Assignment:**
    *   When connections are confirmed in selection mode, check if color conflicts exist
    *   If a conflict exists, reassign the newly placed circle's color using these rules:
        - Find all colors used by directly connected circles
        - Assign the lowest priority color that isn't used by any connected circle
        - If all lower priority colors are used (priorities 1-3), assign priority 4 (red)
    *   Update the circle's visual appearance when its color changes
    *   Add unit tests for connection-based color reassignment

- [ ] **Add Advanced Color Reassignment (Optional/Placeholder):**
    *   Create a placeholder function `_reassign_colors()` that displays a warning when called
    *   Call this function only when a circle must be assigned priority 4 (red)
    *   Add tests to verify the placeholder function is called in the appropriate scenarios
    *   Note: Full implementation of color graph reassignment will be addressed in a future phase

- [ ] **Cleanup:**
    *   Remove the now-unused `_get_random_color()` function and its associated unit test
    *   Ensure all new code is thoroughly documented with detailed comments
