# Contribution Guidelines

NOTE: These guidelines apply only to code in the 4colour repo.

## Coding Standards
- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python or equivalent standards for other languages.
- Use meaningful variable and function names.
- Write modular, reusable, and succinctly documented code. To avoid clutter, do not document self-explanatary code.
- The preference is for precision, not creativity.

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

## Test-Driven Development

To ensure smooth development and avoid regressions:

- Update unit tests whenever functionality changes - this is as important as the implementation itself.
- Tests should be updated to match the new behavior, not the other way around.
- Run tests before and after making changes to verify that your implementation works correctly.
- If a test fails, understand whether it's because of a bug in the implementation or because the test needs to be updated for new behavior.
- All new features must have corresponding tests in the `tests` directory.
- Consider writing tests before implementing a feature to clarify expected behavior.

## Planning

Completed items are marked with `[x]`. These completed items provide valuable context that document the genesis of the existing code base.

New work items should be itemized and preceded by an empty checkbox (`- [ ]`). When engaging in a new coding session to implement new features and improvements, follow the requirements in sequential order starting at the first unmarked checkbox. Once the feature and corresponding unit tests are written or updated to the required specification, mark the checkbox as complete to track progress. Always remember to complete this step.

### Phases 1-7 Summary

The initial development phases (1-7) established the core functionality of the canvas application. This included setting up the Tkinter UI, implementing basic circle drawing and random coloring on click, adding data storage for circle properties (ID, coordinates, color, connections), and introducing a mechanism to connect circles. A selection mode was implemented, allowing users to place a circle and then select existing circles to connect to, confirming with the 'y' key. An "adjust" mode was added to allow moving circles via drag-and-drop and removing circles via right-click. Significant refactoring occurred, including centralizing event binding management based on application modes (CREATE, ADJUST, SELECTION), improving mode transitions, enhancing UI feedback (button text, hint text, canvas background color changes), and consolidating circle removal logic.

### Phase 8: Deterministic Coloring

This phase introduces rule-based circle coloring to replace random coloring. Colors are assigned based on connections between circles to ensure connected circles never share the same color. This phase introduces the most critical functionality of the app, the coloring logic. In this phase, ensure all new code is thoroughly documented with detailed comments.

- [x] **Implement Color Priority System:**
    *   Define color priorities: 1=yellow (lowest), 2=green, 3=blue, 4=red (highest)
    *   Update circle data structure to store both color name and priority number
    *   Update debug display to show both color name and priority number
    *   Create a color utility module with functions to convert between priority numbers and color names
    *   Add unit tests for the new color utility functions

- [x] **Implement Basic Color Assignment Logic:**
    *   Create a new function `_assign_color_based_on_connections()` to replace `_get_random_color()`
    *   When placing a new circle, initially assign priority 1 (yellow)
    *   Ensure this function is designed so that the priority assignment logic can be extended in the future
    *   Add appropriate unit tests for this basic functionality

- [x] **Cleanup:**
    *   Remove the now-unused `_get_random_color()` function and its associated unit test

- [x] **Implement Connection-Aware Color Assignment:**
    *   Note: a color conflict is when two connected circles have the same color.
    *   When connections are confirmed in selection mode, check if color conflicts exist
    *   If a conflict exists, reassign the newly placed circle's color using these rules:
        - Find all colors used by directly connected circles
        - Assign the lowest priority color that isn't used by any connected circle
        - If all lower priorities are used (priorities 1-3), treat this as a special case and call a separate function called `_reassign_color_network()`. Initially this function will just assign priority 4 (red), but will be extended later.
    *   Update the circle's visual appearance when its color changes
    *   Add unit tests for connection-based color reassignment

### Phase 8: debugging

This section addresses discrepancies found during the review of the Phase 8 implementation.

- [x] **Refactor Conflict Check Trigger:**
    *   Modify `_confirm_selection` to perform the color conflict check (`_check_and_resolve_color_conflicts`) only *once* after all selected connections for the `newly_placed_circle_id` have been added in the loop.
    *   Remove the redundant call to `_assign_color_based_on_connections` and `_update_circle_color` after the loop in `_confirm_selection`, as the conflict resolution should handle the final color assignment.
- [x] **Implement `_reassign_color_network` Call:**
    *   Modify `_check_and_resolve_color_conflicts` to call the `_reassign_color_network` function when priorities 1-3 are all used by connected circles, as specified in the requirements.
    *   Ensure `_reassign_color_network` correctly assigns priority 4 (red) for now.
- [x] **Update Unit Tests:**
    *   Review and update `test_confirm_selection`, `test_check_and_resolve_color_conflicts`, and any related tests in `test_canvas_app.py` to accurately reflect the corrected conflict check timing and the call to `_reassign_color_network`.

### Phase 9: Refactoring and Optimization

This phase focuses on removing redundant code related to color handling now that the priority system is the source of truth, and improving overall efficiency.

- [x] **Remove Redundant `color` Field:**
    *   Remove the `color` key from the `circle_data` dictionary definition and all instances where it's assigned or read in `canvas_app.py`. Color will be derived solely from `color_priority` using `get_color_from_priority`.
    *   Update `_draw_on_click` in `canvas_app.py` to only store `color_priority`.
    *   Update `_update_circle_color` in `canvas_app.py`: remove the `color` parameter, update only `color_priority`, and use `get_color_from_priority` to set the canvas item's fill.
    *   Update `_check_and_resolve_color_conflicts` in `canvas_app.py` to use `get_color_from_priority` for setting the fill color and remove any logic setting the `color` field.
    *   Update `_reassign_color_network` in `canvas_app.py` similarly.
- [x] **Update Debug Information:**
    *   Modify `_show_debug_info` in `canvas_app.py` to derive the color name for display by calling `get_color_from_priority(latest_circle['color_priority'])`.
- [x] **Remove Unused Color Utilities:**
    *   Remove the `get_priority_from_color` function from `color_utils.py`.
    *   Remove the import of `get_priority_from_color` from `canvas_app.py` and `tests/test_canvas_app.py`.
    *   Remove the `available_colors` attribute and its initialization using `get_all_colors` in `CanvasApplication.__init__` as it's no longer used.
- [x] **Update Unit Tests:**
    *   Modify tests in `tests/test_canvas_app.py` to no longer check for the `color` key in `circle_data`.
    *   Remove tests related to `get_priority_from_color` in `tests/test_color_utils.py`.
    *   Ensure tests for `_show_debug_info` verify the color name is correctly derived from the priority.
    *   Adjust any other tests affected by the removal of the `color` field or `get_priority_from_color`.
