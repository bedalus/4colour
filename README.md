# 4colour - Visual Four Color Theorem Implementation

This project provides an interactive visualization and implementation of the Four Color Theorem, demonstrating that any planar graph can be colored using at most four colors such that no adjacent vertices share the same color. [Four Color Theorem (Wikipedia)](https://en.wikipedia.org/wiki/Four_color_theorem) - Background on the mathematical theorem this project demonstrates

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

- [ ] **Prevent excessive curvature of connections:**
    * Curved lines are allowed, but should be constrained to help prevent overlaps
    * Do not allow the midpoint too close to either of its attached nodes
    * If connections at either connected node are within 2 degrees, automatically adjust the midpoint to increase the angle of separation to at least 3 degrees.
    * When the user creates a new node, assess the distance to the closest node that the user wants to connect too, and if it is too close, move the node further away from the average position of all the connected nodes

- [ ] **Fix and Enhance Unit Tests:**
    * Update test expectations in `test_color_manager.py` to match the new algorithm behavior
    * Include tests for various graph configurations:
        - Linear chains
        - Cycles (odd and even length)

- [ ] **Document Algorithm and Implementation:**
    * Add detailed comments explaining color reassignment strategy
