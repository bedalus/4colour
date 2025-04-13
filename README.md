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

*   `canvas_app.py`: The main application class that initializes the UI and managers.
*   `ui_manager.py`: Handles UI elements like buttons, hint text, and the debug overlay.
*   `circle_manager.py`: Manages circle data (creation, storage, retrieval, removal).
*   `connection_manager.py`: Manages connections between circles, including drawing lines, handling curves, and midpoint interactions.
*   `interaction_handler.py`: Processes user input events (clicks, drags, key presses) and manages application mode transitions.
*   `color_manager.py`: Implements the logic for assigning colors based on priority and resolving conflicts between connected circles.
*   `color_utils.py`: Provides utility functions for mapping color priorities to names and finding available priorities.
*   `app_enums.py`: Defines enumerations used across the application, such as `ApplicationMode`.
*   `tests/`: Contains all unit and integration tests.
*   `README.md`: This file, providing project documentation, guidelines, and planning.

### Phases 1-7 Summary

The initial development phases (1-7) established the core functionality of the canvas application. This included setting up the Tkinter UI, implementing basic circle drawing and random coloring on click, adding data storage for circle properties (ID, coordinates, color, connections), and introducing a mechanism to connect circles. A selection mode was implemented, allowing users to place a circle and then select existing circles to connect to, confirming with the 'y' key. An "adjust" mode was added to allow moving circles via drag-and-drop and removing circles via right-click. Significant refactoring occurred, including centralizing event binding management based on application modes (CREATE, ADJUST, SELECTION), improving mode transitions, enhancing UI feedback (button text, hint text, canvas background color changes), and consolidating circle removal logic.

### Phase 8-9: Summary

Phases 8 and 9 focused on implementing deterministic coloring based on the Four Color Theorem, followed by optimization and refactoring. A color priority system (1=yellow, 2=green, 3=blue, 4=red) was established with utility functions to convert between priorities and color names. The application now assigns colors based on connections—when two connected circles have the same color, a conflict resolution algorithm assigns the lowest available priority color to ensure connected circles never share the same color. A placeholder for advanced network color reassignment was added for cases when all lower priorities are used. The codebase was then optimized by removing redundant color fields, since colors are now derived directly from priorities. Utility functions were extracted to a separate module to improve reusability and testability. Comprehensive unit tests were added for all the new functionality, ensuring the coloring logic works correctly across various scenarios.

### Phase 10-11: Summary

Phase 10 enhanced connections with curved lines using Tkinter's smoothing, adding draggable midpoints to adjust curve shapes. Displacement vectors store curve offsets, maintained when circles move. Unit tests verified curve behavior in various scenarios.

Phase 11 expanded integration tests (`test_integration.py`) to cover complex component interactions. Tests were added for dragging circles and midpoints, ensuring coordinate and connection updates. Removal cascade tests were enhanced to verify neighbor updates and color conflict checks. New tests validated color conflict resolution during connections, the complete reset functionality of clearing the canvas, and the side effects of mode transitions (e.g., midpoint handle visibility, hint text display, background color changes).

### Phase 13: Track the Clockwise Sequence of Connections to Circles

Phase 13 established a method to determine the clockwise order of connections around each circle, storing this in ordered_connections (connection_manager.py). 

Phase 14 aims to implement a more complex algorithm for reassigning colors across the network when simple local adjustments are insufficient. This often involves graph traversal and potentially techniques related to proving or applying the Four Color Theorem. The ordered connection information from Phase 13 could be useful for Phase 14 because:

1.  Planar Graph Algorithms: Many algorithms designed for planar graphs rely on knowing the cyclic order of edges around each vertex. This information defines the planar embedding and is crucial for operations like identifying faces or traversing the dual graph.
2.  Kempe Chain Heuristics: Algorithms attempting to prove or apply the Four Color Theorem often use Kempe chains (paths alternating between two colors). Identifying and manipulating these chains might require knowing the local arrangement of connections around a circle, which the clockwise order provides.
3.  Systematic Traversal: When the reassignment algorithm needs to explore the network (e.g., using backtracking or recursion as mentioned in the Phase 14 plan), having a consistent, topologically meaningful order for visiting neighbors (the clockwise order) can simplify the logic compared to an arbitrary order.

### Phase 14: Track which circles form a border at the outer edge of the map - Summary

Phase 14 introduced the capability to distinguish between circles on the outer boundary of the graph and those enclosed within faces. An `enclosed` boolean attribute was added to each circle's data structure, defaulting to `False`. The core logic resides in the `_update_enclosure_status` method within `CanvasApplication` (`canvas_app.py`). This method implements an outer face traversal algorithm to identify all circles belonging to the outer boundary.

The algorithm critically depends on the `ordered_connections` list maintained for each circle by the `ConnectionManager`, which stores neighbors in clockwise order based on the calculated angle of departure of the connection line (including any curve adjustments).

Identifying the starting node for the traversal involves a two-stage process to handle potential complexities introduced by curved connections. First, the algorithm identifies the geometrically "most extreme" node (minimum y-coordinate, then minimum x-coordinate) as an initial candidate. Second, it calculates the position of the midpoint handle for every connection (accounting for curves) and identifies the connection whose handle position is "most extreme" (minimum y, then minimum x). The algorithm then compares the extremeness of the candidate node and the extreme midpoint handle position. If the midpoint handle position is found to be more extreme (lower y, or same y and lower x) than the candidate node, the starting node for the traversal is selected from the two nodes connected by that extreme edge (specifically, the one with the minimum y, then minimum x coordinate between the two). Otherwise, if the candidate node is more extreme or equally extreme, or if no connections exist, the candidate node itself is chosen as the starting point. Once the starting node is determined, the traversal identifies the first edge to follow by finding the connection *entering* the start node with the largest angle (closest to 360 degrees in the clockwise sweep from North) and then selecting the *next* connection in the start node's `ordered_connections` list as the first outgoing edge.

From this starting edge, the algorithm "walks" the outer boundary. At each circle (`current_node`), it identifies the connection it arrived from (`previous_node`). Using the `ordered_connections` of the `current_node`, it finds the index of the `previous_node` and selects the *next* connection in the clockwise sequence as the path to the next circle on the outer boundary. This process repeats until the walk returns to the starting circle. All circles visited during this walk are marked as `enclosed=False`, and all others are marked `enclosed=True`.

A key complexity arises from curved connections. A significant curve can alter the effective angle of a connection line where it meets the circle, potentially changing its position within the `ordered_connections` list compared to a straight line. The `update_ordered_connections` method accounts for these curves when calculating angles, ensuring the traversal algorithm correctly follows the topological outer face even when geometric shapes are distorted by curves.

The `_update_enclosure_status` calculation is triggered after operations that modify the graph's topology or geometry: circle creation (`draw_on_click`), connection creation (`confirm_selection`), circle removal (`remove_circle`), and drag completion (`drag_end`). Comprehensive integration tests were added in `test_integration.py` to validate the enclosure status under various graph structures and modifications, including scenarios specifically testing the impact of curved connections.

### Phase 14-post-implementation: Debugging the Perimeter Traversal Algorithm

There is a miscalculation happening in the algorithm designed in phase 14 so we are going to try to find the cause. The first circle (or "node") identified as the starting point for determining the graph's perimeter has an arrow pointing out of it to indicate the perimeter node traversal path. Unfortunately it *sometimes* fails at this task (points along the wrong connection). I believe the issue might be related to Tkinter's inverted y-axis. This has been compensated for already in most of the application, but not for these arrows.

Upon examining the logic around these arrows (focusing on the y-axis inversion, "north" as zero-degrees, clockwise ordering, and possible systemic problems) we established that: 

- The starting node is determined correctly.
- Tkinter's y-axis increases downward, the opposite to usual mathematical convention.
- The "most extreme" node (minimum-y and minimum-x for ties) appears closer to the top of the canvas.
- Minimum-x is conventional, i.e. leftmost, so calculations for clockwise may be inverted.
- North = 0° , East = 90° , South = 180° , West = 270°.
- North is still intended to point upward, accounting for the inversion.
- The first outgoing edge (called a connection in the code) from the starting node is determined by a clockwise sweep from North.

We must fix the problem. We must consider possible causes:

- An isolated routine in the algorithm selects the wrong "next" connection to begin traversal when it fails to properly account for the y-axis inversion when calculating the "largest angle" for the entering connection.
- In a standard angle system (with y-up), a vector pointing up has angle 90°, a vector pointing down has angle 270°, but in an inverted y-axis system (with y-down), those same vectors would have up as 270° and down as 90°.
- If the algorithm uses atan2(y, x) directly without accounting for the inversion, angles would be incorrectly calculated, causing the wrong "next" connection to be selected.

To either confirm or refute the above hypothesis we should examine:

- How angles are calculated in the update_ordered_connections method.
- The logic for finding the connection with the "largest angle" entering the start node.
- Whether transformations like (90 + atan2(y, x)) % 360 are being applied to account for the inverted y-axis.

### Phase 15: Advanced Color Network Reassignment

This phase focuses on developing a sophisticated algorithm for reassigning colors throughout the network of connected circles when simple conflict resolution is insufficient. Currently, the application assigns priority 4 (red) as a fallback, but a more optimal solution would rearrange existing colors to maintain the Four Color Theorem guarantee.

- [ ] **Design Network Reassignment Algorithm:**
    * Define a graph traversal approach for analyzing the network of connected circles
    * Develop strategy for identifying color reassignment opportunities (e.g., swapping colors between distant circles)
    * Determine stopping conditions to prevent infinite loops during recursive traversal
    * Document the algorithm design with clear pseudocode or diagrams for implementation reference

- [ ] **Implement Network Analysis Functions:**
    * Create helper functions in `color_utils.py` to analyze graph properties relevant for coloring
    * Implement functions to identify color domains, conflict regions, and potential reassignment candidates
    * Add utility functions to test whether a proposed coloring solution is valid
    * Write unit tests for these utility functions with various graph configurations

- [ ] **Implement Core Reassignment Logic:**
    * Replace the placeholder implementation in `_reassign_color_network()` with the new algorithm
    * Develop a recursive function that can traverse the circle network and test different color assignments
    * Implement backtracking capability to revert unsuccessful color assignments during traversal
    * Ensure the implementation prioritizes using colors 1-3 (yellow, green, blue) and minimizes use of color 4 (red)
    * Add appropriate error handling for edge cases (circular references, disconnected components)

- [ ] **Add Performance Optimizations:**
    * Implement memoization or caching to avoid redundant calculations during traversal
    * Add early termination conditions for branches that cannot lead to valid solutions
    * Optimize the algorithm to prefer minimal color changes when resolving conflicts
    * Consider adding a complexity threshold beyond which a simpler fallback solution is used

- [ ] **Update UI Feedback for Reassignment:**
    * Implement visual feedback when network reassignment occurs (e.g., brief animation, status message)
    * Add optional debugging overlay to visualize the reassignment process for educational purposes
    * Ensure all circle colors update smoothly after network reassignment

- [ ] **Create Comprehensive Unit Tests:**
    * Develop test cases for various network configurations (linear chains, loops, complete graphs, etc.)
    * Add tests for edge cases like maximum connections and highly constrained networks
    * Implement tests to verify the algorithm's performance characteristics
    * Create tests that validate the four-color theorem is maintained across the application

- [ ] **Update Documentation:**
    * Add detailed comments explaining the network reassignment algorithm
    * Include high-level description of the algorithm in code documentation
    * Document any limitations or known edge cases for future reference
