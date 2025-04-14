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

To ensure smooth development and avoid regressions:

- Update unit tests whenever functionality changes - this is as important as the implementation itself.
- Tests should be updated to match the new behavior, not the other way around.
- Run tests before and after making changes to verify that your implementation works correctly.
- If a test fails, understand whether it's because of a bug in the implementation or because the test needs to be updated for new behavior.
- All new features must have corresponding tests in the `tests` directory.
- Consider writing tests before implementing a feature to clarify expected behavior.

Tests can be run with: python -m unittest discover -s tests

If running with runtime logging: python log_function_calls.py

To analyse the results*: python analyze_call_logs.py

(* if missing pandas/matplotlib, open a terminal as admin, then: pip install pandas matplotlib)

Install coverage if missing: pip install coverage (as an admin)

Run: python -m tests.run_coverage (normal user)

This runs all tests with coverage management and produces a report. Read tests/README.md for more detail.

## Planning

New work items should be itemized and preceded by an empty checkbox (`- [ ]`). When engaging in a new coding session to implement new features and improvements, follow the requirements in sequential order starting at the first unmarked checkbox. Once the feature and corresponding unit tests are written or updated to the required specification, mark the checkbox as complete ([x]) to track progress. Always remember to complete this step.

If new files are introduced, or if files are removed, update the '## Project Structure' section below accordingly.

**Introducing New Work Phases:**

When the current phase's objectives are complete or a new major area of work is identified, introduce a new phase at the end of this ReadMe file. Follow the following format:

1.  **Add a Phase Heading:** Use a level 3 Markdown heading with the format `### Phase [Number]: [Brief, Descriptive Title]`. Increment the phase number sequentially.
2.  **Write a Summary:** Immediately below the heading, add a short paragraph summarizing the overall goal or focus of this new phase. Explain *why* this work is being undertaken.
3.  **Structure Work Items:** List the specific tasks for the phase using the standard format:
    *   Start each major task with `- [ ] **Task Description:**`. Use bold text for the main task description.
    *   Use nested bullet points (`    * Sub-task or detail`) for breaking down the main task or adding specific implementation notes.

## Project Structure

The project is organized into the following key files and directories:

*   `README.md`: The current file. This outlines the goals of the project and can be updated as required, e.g. when planning.
*   `canvas_app.py`: The main application class that initializes the UI and managers.
*   `ui_manager.py`: Handles UI elements like buttons, hint text, and the debug overlay.
*   `circle_manager.py`: Manages circle data (creation, storage, retrieval, removal).
*   `connection_manager.py`: Manages connections between circles, including drawing lines, handling curves, and midpoint interactions.
*   `interaction_handler.py`: Processes user input events (clicks, drags, key presses) and manages application mode transitions.
*   `color_manager.py`: Implements the logic for assigning colors based on priority and resolving conflicts between connected circles.
*   `color_utils.py`: Provides utility functions for mapping color priorities to names and finding available priorities.
*   `app_enums.py`: Defines enumerations used across the application, such as `ApplicationMode`.
*   `boundary_manager.py`: Identifies outer boundary nodes and updates enclosure status.
*   `function_logger.py`: Instruments modules to log function calls for debugging and analysis.
*   `log_function_calls.py`: Runs the application with function call logging enabled.
*   `analyze_call_logs.py`: Analyzes function call logs to generate insights.
*   `tests/`: Contains all unit and integration tests:
    * `test_app_enums.py`: Tests for application enum definitions.
    * `test_boundary_manager.py`: Tests for boundary detection and enclosure status.
    * `test_canvas_app.py`: Tests for the main canvas application class.
    * `test_circle_manager.py`: Tests for circle creation, removal, and data management.
    * `test_color_manager.py`: Tests for color assignment and conflict resolution logic.
    * `test_color_utils.py`: Tests for color utility functions.
    * `test_connection_manager.py`: Tests for connection creation, curve management, and angle calculations.
    * `test_integration.py`: Tests for interactions between multiple components and workflows.
    * `test_interaction_handler.py`: Tests for user input handling, mode transitions, and drag/drop logic.
    * `test_ui_manager.py`: Tests for UI element management and display updates.
    * `test_utils.py`: Contains testing utilities and mock objects like `MockAppTestCase`.

### Phases 1-7 Summary

The initial development phases (1-7) established the core functionality of the canvas application. This included setting up the Tkinter UI, implementing basic circle drawing and random coloring on click, adding data storage for circle properties (ID, coordinates, color, connections), and introducing a mechanism to connect circles. A selection mode was implemented, allowing users to place a circle and then select existing circles to connect to, confirming with the 'y' key. An "adjust" mode was added to allow moving circles via drag-and-drop and removing circles via right-click. Significant refactoring occurred, including centralizing event binding management based on application modes (CREATE, ADJUST, SELECTION), improving mode transitions, enhancing UI feedback (button text, hint text, canvas background color changes), and consolidating circle removal logic.

### Phase 8-9: Summary

Phases 8 and 9 focused on implementing deterministic coloring based on the Four Color Theorem, followed by optimization and refactoring. A color priority system (1=yellow, 2=green, 3=blue, 4=red) was established with utility functions to convert between priorities and color names. The application now assigns colors based on connections—when two connected circles have the same color, a conflict resolution algorithm assigns the lowest available priority color to ensure connected circles never share the same color. A placeholder for advanced network color reassignment was added for cases when all lower priorities are used. The codebase was then optimized by removing redundant color fields, since colors are now derived directly from priorities. Utility functions were extracted to a separate module to improve reusability and testability. Comprehensive unit tests were added for all the new functionality, ensuring the coloring logic works correctly across various scenarios.

### Phase 10-11: Summary

Phase 10 enhanced connections with curved lines using Tkinter's smoothing, adding draggable midpoints to adjust curve shapes. Displacement vectors store curve offsets, maintained when circles move. Unit tests verified curve behavior in various scenarios.

Phase 11 expanded integration tests (`test_integration.py`) to cover complex component interactions. Tests were added for dragging circles and midpoints, ensuring coordinate and connection updates. Removal cascade tests were enhanced to verify neighbor updates and color conflict checks. New tests validated color conflict resolution during connections, the complete reset functionality of clearing the canvas, and the side effects of mode transitions (e.g., midpoint handle visibility, hint text display, background color changes).

### Phase 13-15: Summary

Phase 13 established a method to determine the clockwise order of connections around each circle, storing this in ordered_connections (connection_manager.py). This is necessary functionality for the 'Right-hand' rule commonly used in planar graphs when establishing the 'outer face'.

Phase 14 introduced the ability to distinguish between circles on the outer boundary and those enclosed within faces. The `enclosed` attribute was added to circle data, and the `_update_enclosure_status` method in `CanvasApplication` identifies boundary nodes on the 'outer face' using a traversal algorithm. The traversal relies on the clockwise `ordered_connections` list for each circle, ensuring accurate boundary detection even with curved connections. Tests were added to validate the enclosure status under various graph configurations.

Phase 15 ensured a consistent starting point for the outer face traversal by introducing two fixed nodes (Node A and Node B) connected by a fixed edge. These nodes are created at initialization and cannot be moved or removed. Proximity restrictions prevent placing new nodes or dragging midpoint handles into a restricted zone near the fixed nodes. The `_update_enclosure_status` method was updated to always start traversal from Node A. Tests were updated and added to verify the behavior of fixed nodes, proximity restrictions, and traversal logic.

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
