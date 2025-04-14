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
- Write unit tests for all new features or changes. Include documentation for running the unit tests in a top level folder called 'tests'

## Project-Specific Rules
- Use `snake_case` for variables and functions.
- Use `PascalCase` for classes.
- Ensure all code passes linting and formatting checks before committing.
- Use lowercase names for folders.
- Even though I am English, use the American spelling of colour, i.e. color, except for the title '4colour'.

## Test-Driven Development

- Update unit tests whenever functionality changes - they're as important as the implementation
- Tests should match the behavior of your implementation
- Run tests before and after making changes to verify correctness
- All new features must have corresponding tests
- Consider writing tests before implementing features to clarify requirements

Note: Some tests may intentionally fail if they were written to describe future functionality that hasn't been implemented yet (especially in Phase 16).

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

- [ ] **Review and Understand Existing Color Management:**
    * Study the current implementation in `color_manager.py`, particularly `assign_color_based_on_connections()`, `check_and_resolve_color_conflicts()`, and `_reassign_color_network()`
    * Examine test failures in `test_color_manager.py` to understand expected behavior
    * Ensure color priority system (1=yellow, 2=green, 3=blue, 4=red, with 5 being an "overflow" priority) is consistently implemented

- [ ] **Extend Color Priority System:**
    * Update `color_utils.py` to handle priority 5 (recommend using purple or another distinct color)
    * Modify `get_color_from_priority()` to support the extended range
    * Add entry to `_PRIORITY_TO_COLOR` dictionary
    * Update any related UI components to handle the new color

- [ ] **Design Graph Coloring Algorithm:**
    * Research well-established graph coloring algorithms (e.g., greedy coloring, backtracking, kempe chain)
    * Implement a "kempe chain" approach - this allows color swapping between different regions of the graph
    * For complex cases, consider implementing a backtracking algorithm with these components:
        - Function to check if a color assignment is valid for a node
        - Recursive function to try different color assignments
        - Mechanism to track already-tried configurations

- [ ] **Enhance Core Color Management Functions:**
    * Update `check_and_resolve_color_conflicts()` to attempt more sophisticated resolution before falling back to priority 5
    * Implement `_find_valid_coloring()` function that can recursively explore different color assignments
    * Replace placeholder implementation in `_reassign_color_network()` with full algorithm that:
        - Identifies the affected subgraph when a conflict occurs
        - Attempts to reassign colors within the subgraph without introducing new conflicts
        - Uses a depth-first search to explore potential color swaps
        - Falls back to priority 5 only when genuinely necessary

- [ ] **Improve Color Assignment Logic:**
    * Modify `assign_color_based_on_connections()` to handle invalid circle IDs properly (return None)
    * Update conflict detection to consider the full network effect of color changes
    * Add a `get_connected_component()` function that returns all circles in a connected subgraph
    * Implement proper handling for "saturated" scenarios where all 4 colors are already in use

- [ ] **Add Data Structures for Efficient Color Management:**
    * Create a `ColorGraph` class in a new file `color_graph.py` to represent the coloring problem:
        ```python
        class ColorGraph:
            def __init__(self, app):
                self.app = app
                self.nodes = {}  # Mapping of circle IDs to node objects
                self.max_color = 4  # Default to 4 colors
            
            def build_from_circles(self, circles, circle_lookup):
                """Build graph representation from application's circle data"""
                # Implementation here
            
            def is_valid_coloring(self):
                """Check if current coloring is valid"""
                # Implementation here
            
            def find_optimal_coloring(self):
                """Find an optimal coloring using backtracking"""
                # Implementation here
            
            def apply_coloring_to_app(self):
                """Apply the graph's coloring solution back to the app"""
                # Implementation here
        ```
    * Add methods to analyze color constraints and identify minimal changes needed

- [ ] **Implement Kempe Chain Algorithm:**
    * Create a function that can swap colors along a chain:
        ```python
        def kempe_chain_swap(graph, node_id, color1, color2):
            """
            Perform a Kempe chain color swap starting from node_id.
            Swaps color1 and color2 throughout the connected component.
            """
            # Implementation here
        ```
    * Use this function when resolving conflicts to avoid using a 5th color

- [ ] **Add Performance Considerations:**
    * Implement memoization to cache results of subproblems
    * Add early termination for branches that can't lead to valid solutions
    * Consider adding a complexity threshold (e.g., number of affected nodes) beyond which a simpler approach is used
    * For very large graphs (20+ nodes), implement a timeout mechanism to fall back to greedy coloring

- [ ] **Update UI Feedback for Reassignment:**
    * Add visual indication when network reassignment occurs
    * Consider showing a brief animation of color changes or status message
    * Add debug mode to visualize the coloring algorithm in action (optional)

- [ ] **Fix and Enhance Unit Tests:**
    * Update test expectations in `test_color_manager.py` to match the new algorithm behavior
    * Fix tests that expect priority 5 for overflow cases
    * Add tests for kempe chain and backtracking algorithms
    * Include tests for various graph configurations:
        - Linear chains
        - Cycles (odd and even length)
        - Complete graphs (K3, K4, K5)
        - Planar and non-planar graphs
        - Bipartite graphs

- [ ] **Document Algorithm and Implementation:**
    * Add detailed comments explaining color reassignment strategy
    * Create a visual diagram of the algorithm flow
    * Document any limitations (e.g., performance with very large graphs)
    * Include references to graph coloring literature
    * Update user documentation if the color scheme changes
