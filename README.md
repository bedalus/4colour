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

## Planning

Use the PLAN.md file for all planning and tracking. Use this file for summaries when work phases are completed.

## Project Structure

The project is organized into the following key files and directories:

*   `README.md`: Current file. Project goals, summaries of initial development phases
*   `PLAN.md`: Development planning and tracking
*   `canvas_app.py`: Main application class with event delegation
*   `app_enums.py`: Application enumerations like ApplicationMode
*   `ui_manager.py`: UI element management and visualization
*   `circle_manager.py`: Circle data operations and lifecycle
*   `connection_manager.py`: Connection management, curve calculation, and angle validation
*   `interaction_handler.py`: User input processing, drag operations, and mode transitions
*   `color_manager.py`: Color assignment operations
*   `color_utils.py`: Color utility functions and priority mappings
*   `boundary_manager.py`: Boundary node identification and enclosure status
*   `fix_VCOLOR.py`: VCOLOR node management and conflict resolution
*   `function_logger.py`, `log_function_calls.py`, `analyze_call_logs.py`: Debugging tools

### Component Relationships

*   `canvas_app.py` serves as the main controller, delegating to specialized managers
*   The Managers focus on specific domains (UI, circles, connections, colors, boundaries)
*   `interaction_handler.py` processes user input and coordinates with managers
*   `app_enums.py` provides consistent mode definitions across components
*   `fix_VCOLOR.py` centralizes color conflict resolution logic

### Phases 1-7 Summary

The initial development phases established core functionality: Tkinter UI, circle drawing with coloring, data storage, connection mechanisms, selection mode for connecting circles, adjust mode for moving/removing circles, and event binding management with improved mode transitions and UI feedback.

### Phase 8-9: Summary

These phases implemented deterministic coloring based on the Four Color Theorem with a priority system (1=yellow, 2=green, 3=blue, 4=red), conflict resolution, and codebase optimization.

### Phase 10-11: Summary

Phase 10 added curved connections with draggable midpoints using displacement vectors. Phase 11 expanded integration tests covering interactions between components, including drag behavior, removal cascades, color conflict resolution, and mode transition side effects.

### Phase 13-15: Summary

Phase 13 implemented clockwise connection ordering. Phase 14 added boundary detection to distinguish between outer and enclosed circles. Phase 15 introduced fixed nodes for consistent traversal starting points and proximity restrictions.

### Phase 16: Summary

Phase 16 centralized all VCOLOR node logic and state into the new `fix_VCOLOR.py` module, with `ColorManager` and related classes delegating VCOLOR node operations. This refactor improved modularity and prepares the codebase for future enhancements.
