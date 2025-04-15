# 4colour - Visual Four Color Theorem Implementation

This project provides an interactive visualization and implementation of the Four Color Theorem, demonstrating that any planar graph can be colored using at most four colors such that no adjacent vertices share the same color.

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
- Write unit tests for all new features or changes. Include documentation for running the unit tests in a top level folder called 'tests'.

## Project-Specific Rules
- Use `snake_case` for variables and functions.
- Use `PascalCase` for classes.
- Ensure all code passes linting and formatting checks before committing.
- Use lowercase names for folders.

## Test-Driven Development

- Update unit tests whenever functionality changes - they're as important as the implementation.
- Tests should match the behavior of your implementation.
- Run tests before and after making changes to verify correctness.
- All new features must have corresponding tests.

```bash
# Run basic tests
python -m unittest discover -s tests

# Run with runtime logging
python log_function_calls.py

# Run with coverage analysis (requires: pip install coverage pandas matplotlib)
python -m tests.run_coverage
```

Read tests/README.md for more details on test coverage analysis.

## Planning

Work items use checkboxes (`- [ ]`) and should be completed in sequential order. Mark tasks complete (`- [x]`) when both implementation and tests are finished. Update the Project Structure section when files change.

When adding new phases:
1. Use level 3 heading: `### Phase [Number]: [Brief Title]`
2. Include a summary paragraph explaining the goal
3. List tasks with main items in bold and nested bullet points for subtasks

## Project Structure

The project is organized into the following key files and directories:

*   `README.md`: Current file with project goals and planning
*   `canvas_app.py`: Main application class
*   `ui_manager.py`: UI element management
*   `circle_manager.py`: Circle data operations
*   `connection_manager.py`: Connection management and visualization
*   `interaction_handler.py`: User input processing and mode transitions
*   `color_manager.py`: Color assignment and conflict resolution
*   `color_utils.py`: Color utility functions
*   `app_enums.py`: Application enumerations
*   `boundary_manager.py`: Boundary node identification
*   `function_logger.py`, `log_function_calls.py`, `analyze_call_logs.py`: Debugging tools
*   `tests/`: Unit and integration tests

### Resources

* [Four Color Theorem (Wikipedia)](https://en.wikipedia.org/wiki/Four_color_theorem) - Background on the mathematical theorem this project demonstrates
* [Graph Coloring Algorithms](https://www.geeksforgeeks.org/graph-coloring-applications/) - Overview of common graph coloring approaches

### Phases 1-7 Summary

The initial development phases established core functionality: Tkinter UI, circle drawing with coloring, data storage, connection mechanisms, selection mode for connecting circles, adjust mode for moving/removing circles, and event binding management with improved mode transitions and UI feedback.

### Phase 8-9: Summary

These phases implemented deterministic coloring based on the Four Color Theorem with a priority system (1=yellow, 2=green, 3=blue, 4=red), conflict resolution, and codebase optimization through extracted utility functions and comprehensive tests.

### Phase 10-11: Summary

Phase 10 added curved connections with draggable midpoints using displacement vectors. Phase 11 expanded integration tests covering interactions between components, including drag behavior, removal cascades, color conflict resolution, and mode transition side effects.

### Phase 13-15: Summary

Phase 13 implemented clockwise connection ordering. Phase 14 added boundary detection to distinguish between outer and enclosed circles. Phase 15 introduced fixed nodes for consistent traversal starting points and proximity restrictions.

### Phase 16: Advanced Color Network Reassignment

This phase focuses on enhancing the color management system to handle complex graph coloring scenarios where simple conflict resolution isn't sufficient. The current implementation falls back to priority 4 (red) in difficult cases, but we need a more sophisticated algorithm that can reassign colors throughout the network to maintain the Four Color Theorem more optimally.

- [x] **Review and Understand Existing Color Management:**
    * Study the current implementation in `color_manager.py`, particularly `assign_color_based_on_connections()`, `check_and_resolve_color_conflicts()`, and `_reassign_color_network()`
    * Examine test failures in `test_color_manager.py` to understand expected behavior
    * Color priority system (1=yellow, 2=green, 3=blue, 4=red): Priority 4 (red) is a special case. The additional handling required when red is assigned has not yet been written
    * On the canvas, graph nodes are represented by circles and edges are represented by connections.

- [x] **Modify UI behaviour:**
    * Modify the application so that nodes and connections can be locked in place
    * LOCKED can be a new attribute for nodes and connections
    * This logic is separate to the special Node A and Node B that are always present
    * When the user exits ADJUST mode, every node and connection is assigned LOCKED=true
    * When a user enters ADJUST mode, they cannot interact with locked elements

- [x] **Enhance Core Color Management Functions:**
    * Any new work must ensure appropriate linkage with `check_and_resolve_color_conflicts()` and `assign_color_based_on_connections()` as required
    * Replace placeholder implementation in `_reassign_color_network()` with full algorithm that:
        - Performs a color swap every time a new node is assigned priority 4
        - Details for the swap process: check every node that is connected to the new node until one is identified that has enclosed=true status and then stop and exchange priorities with that one
        - After the priority swap, the two representative circles must be redrawn to show their new color
        - Also, a check must be performed for any conflict on these two nodes. If a conflict is found, a warning should be displayed for debugging purposes. Additional logic to handle this will be added later.

- [ ] **Investigate `_remove_on_right_click`:**
    * Determine the purpose and current usage of the `_remove_on_right_click` method in `canvas_app.py`.
    * Verify if it's still needed or if its functionality is handled elsewhere (e.g., within `InteractionHandler`).
    * If needed, ensure it correctly respects the new `locked` attribute.

- [ ] **Fix and Enhance Unit Tests:**
    * Update test expectations in `test_color_manager.py` to match the new algorithm behavior
    * Include tests for various graph configurations:
        - Linear chains
        - Cycles (odd and even length)

- [ ] **Document Algorithm and Implementation:**
    * Add detailed comments explaining color reassignment strategy

## Phase 16 Implementation Details

This section summarizes the code changes made to address the completed work items in Phase 16 and subsequent bug fixes.

### Item 1: Review and Understand Existing Color Management

This task involved analyzing the existing code in `color_manager.py` and `color_utils.py`, along with related tests. The analysis confirmed that the previous implementation assigned priority 4 (red) as a simple fallback when priorities 1-3 were unavailable for a node, without attempting further network adjustments. This understanding informed the implementation of the color swap logic. This task is marked as complete.

### Item 2: Modify UI Behaviour (Locking)

The goal was to prevent interaction with nodes and connections outside of specific conditions in ADJUST mode.

1.  **Attribute Addition:**
    *   A `locked` boolean attribute (defaulting to `False`) was added to the circle data dictionary upon creation in `interaction_handler.py` (`draw_on_click`).
    *   A `locked` boolean attribute (defaulting to `False`) was added to the connection data dictionary upon creation in `connection_manager.py` (`add_connection`).

2.  **Locking Logic:**
    *   In `interaction_handler.py` (`set_application_mode`), the logic was modified so that all non-fixed circles and connections have their `locked` attribute set to `True` when the application transitions *out of* `CREATE` mode (instead of the initial plan of locking when exiting `ADJUST` mode).

3.  **Unlocking Logic:**
    *   When transitioning *into* `ADJUST` mode (`interaction_handler.py`, `set_application_mode`), specific unlocking occurs:
        *   The circle identified by `self.app.last_circle_id` (if it exists and is not fixed) has its `locked` attribute set to `False`.
        *   The connections associated with `self.app.last_circle_id` also have their `locked` attribute set to `False` by iterating through the circle's `connected_to` list and updating the corresponding connection data in `self.app.connections`.

4.  **Interaction Prevention:**
    *   The `drag_start` method in `interaction_handler.py` was updated. Before initiating a drag (`drag_state["active"] = True`), it now checks the `locked` attribute of the target:
        *   For circles, it checks `circle.get("locked", False)`.
        *   For midpoint handles, it retrieves the corresponding `connection` data using the handle's tag and checks `connection.get("locked", False)`.
    *   If `locked` is `True`, the `drag_start` method returns early, preventing the drag.

5.  **Bug Fix:** An initial bug caused all elements to remain draggable after exiting and re-entering ADJUST mode. This was because the code incorrectly contained loops that set `locked = False` for *all* elements when entering ADJUST mode. These loops were removed, ensuring only the last node and its connections are explicitly unlocked.

### Item 3: Enhance Core Color Management Functions (`reassign_color_network`)

The `reassign_color_network` method in `color_manager.py` was significantly modified to implement the color swap logic when a node is initially assigned priority 4 (red).

1.  **Trigger:** The method is called from `assign_color_based_on_connections` and `check_and_resolve_color_conflicts` when priority 4 is determined as the necessary color.
2.  **Swap Target Search:** The method iterates through the neighbors (`connected_to`) of the `circle_id` that triggered the reassignment. It looks for the first neighbor with `enclosed=True`.
3.  **Swap Execution:**
    *   If an enclosed neighbor (`swap_target_id`) is found:
        *   The original circle (`circle_id`) receives the neighbor's original priority (`swap_target_original_priority`).
        *   The enclosed neighbor (`swap_target_id`) receives priority 4.
        *   The `update_circle_color` method is called for both circles to update their data and visual appearance on the canvas.
4.  **Post-Swap Conflict Check:** After the swap, `check_and_resolve_color_conflicts` is called on both the original circle and the swapped neighbor to handle any *new* conflicts introduced by the swap. Debug `print` statements were added to warn if the final priorities differ from the intended swap priorities.
5.  **Return Value:** The method returns the final priority assigned to the original `circle_id` after the swap and subsequent conflict check.
6.  **Fallback:** If no suitable enclosed neighbor is found, the original circle retains priority 4, and the method returns 4. `update_circle_color` is still called to ensure the circle is visually red.

### Subsequent Modifications & Bug Fixes

1.  **Highlighting Last Node:**
    *   Functionality was added to temporarily highlight the `last_circle_id` when entering ADJUST mode.
    *   A `highlighted_circle_id` attribute was added to `CanvasApplication`.
    *   In `interaction_handler.py` (`set_application_mode`), when entering ADJUST mode and after unlocking the last circle, a larger purple outline (`temp_highlight` tag) is drawn around it, and its canvas ID is stored in `highlighted_circle_id`. Any previous highlight is deleted first.
    *   The highlight is removed (deleted from the canvas and `highlighted_circle_id` reset) either when a drag operation starts (`interaction_handler.py`, `drag_start`) or when exiting ADJUST mode (`interaction_handler.py`, `set_application_mode`).

2.  **Hint Text Update:**
    *   The `show_edit_hint_text` method in `ui_manager.py` was updated to display "You may adjust the last node and its connections" when in ADJUST mode.

3.  **Connection Unlocking Bug:** A bug where connections of the last circle were not being unlocked was addressed by ensuring the unlocking loop within `set_application_mode` correctly targets and modifies the `locked` attribute in the shared `self.app.connections` dictionary.

4.  **Syntax Error:** A `SyntaxError: unterminated string literal` near line 473 in `interaction_handler.py` (`self.app.drag_state["type"] = "circle"`) was reported and fixed by providing a clean version of the `drag_start` method, likely resolving a hidden character or encoding issue.
