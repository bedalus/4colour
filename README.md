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

### Phase 14: Identify Outer Boundary Nodes - Summary

Phase 14 introduced the capability to distinguish between circles on the outer boundary of the graph and those enclosed within faces. An `enclosed` boolean attribute was added to each circle's data structure, defaulting to `False`. The core logic resides in the `_update_enclosure_status` method within `CanvasApplication` (`canvas_app.py`). This method implements an outer face traversal algorithm to identify all circles belonging to the outer boundary.

The algorithm critically depends on the `ordered_connections` list maintained for each circle by the `ConnectionManager`, which stores neighbors in clockwise order based on the calculated angle of the connection line (including any curve adjustments).

To start the traversal, the algorithm first identifies the connection edge whose midpoint handle position is "most extreme" (minimum y, then minimum x, accounting for curves). The starting node for the traversal is then chosen as the endpoint of this extreme edge that is itself most extreme (minimum y, then minimum x).

Once the starting node is determined, the traversal identifies the first outgoing edge to follow by finding the connection leaving the start node with the smallest angle (measured clockwise from North, 0 degrees). From this initial edge, the algorithm "walks" the outer boundary using the Right-Hand Rule (see below). At each circle (`current_node`), it identifies the connection it arrived from (`previous_node`). Using the `ordered_connections` of the `current_node`, it finds the index of the `previous_node` and selects the *next* connection in the clockwise sequence as the path to the next circle on the outer boundary. This process repeats until the walk returns to the starting circle. All circles visited during this walk are marked as `enclosed=False`, and all others are marked `enclosed=True`.

A key complexity arises from curved connections. A significant curve can alter the effective angle of a connection line where it meets the circle, potentially changing its position within the `ordered_connections` list compared to a straight line. The angle calculation methods (`_calculate_corrected_angle` in `canvas_app.py` and related methods in `connection_manager.py`) account for these curves when determining the order, ensuring the traversal algorithm correctly follows the topological outer face even when geometric shapes are distorted by curves.

The `_update_enclosure_status` calculation is triggered after operations that modify the graph's topology or geometry: circle creation (`draw_on_click`), connection creation (`confirm_selection`), circle removal (`remove_circle_by_id`), and drag completion (`drag_end`). Comprehensive integration tests were added in `test_integration.py` to validate the enclosure status under various graph structures and modifications.

**The Right-Hand Rule:** In the context of traversing faces in a planar graph embedding (where edges around each node have a defined cyclic order, like our clockwise `ordered_connections`), the Right-Hand Rule provides a consistent way to trace a face boundary. Imagine walking along an edge towards a node. When you arrive, you look at the available edges leaving that node, ordered clockwise. To follow the Right-Hand Rule, you always choose the *next* edge in the clockwise order immediately after the edge you just arrived on. If you consistently apply this rule, you will trace the boundary of a single face in a clockwise direction. The Left-Hand Rule is analogous, choosing the next edge *counter-clockwise*, tracing the face in the opposite direction. For finding the outer face (often considered the "infinite" face), starting on a known outer edge and consistently applying one of these rules allows traversal of its boundary.

### Phase 15: Guaranteeing an Outer Face Starting Point

This phase aims to simplify the identification of the outer face boundary by establishing a guaranteed starting point that is always part of the outer face and remains the "most extreme" element geometrically. This avoids complexities with curved connections potentially altering which node or edge appears most extreme.

- [x] **Initialize with Fixed Outer Nodes:**
    *   Modify `CanvasApplication.__init__` to automatically create two specific nodes upon startup (e.g., Node A at (10, 40), Node B at (40, 10)).
    *   Automatically create a connection between these two initial nodes.
    *   Assign unique, reserved IDs (e.g., -1, -2) or use a flag to mark these nodes as special/fixed.
    *   Be sure to reinitialize if the clear canvas button is pressed.

- [x] **Make Initial Nodes Non-Adjustable:**
    *   Modify `InteractionHandler.drag_start` to prevent dragging of these fixed nodes.
    *   Modify `CircleManager.remove_circle_by_id` (or related interaction logic) to prevent deletion of these fixed nodes.
    *   Ensure the connection between them cannot be removed or its midpoint handle dragged.

- [x] **Implement Proximity Restrictions:**
    *   Modify `InteractionHandler.draw_on_click` to prevent placing new nodes within a defined radius of the origin or the fixed nodes (e.g., disallow placement if x < 50 and y < 50).
    *   Modify `InteractionHandler.drag_midpoint_motion` (or `drag_end`) to prevent midpoint handles from being dragged into this restricted zone. This ensures no new element can become "more extreme" than the initial fixed nodes/edge.

- [x] **Adapt Outer Face Traversal Start:**
    *   Modify `CanvasApplication._update_enclosure_status` to *always* use one of the fixed nodes (e.g., Node A) as the `start_node` for the outer face traversal.
    *   The logic to find the first outgoing edge (minimum angle clockwise from North) can remain, starting from this fixed node.
    *   We no longer need to find the starting point, as we can use the Node A -> Node B connection as a guaranteed outer edge, so the existing code that does this is redundant and can be removed.

- [x] **Update Tests:**
    *   Adjust existing tests (`test_integration.py`, `test_canvas_app.py`) to account for the presence and behavior of the fixed initial nodes.
    *   Add new tests specifically verifying the non-adjustability and proximity restrictions.
    *   When working on the tests, anticipate that there may be undocumented reasons why they are out of alignment with the revised application code, so may need multiple passes to fully repair.

### Phase 16: Deal with current bugs

E.g. error: Warning: Boundary traversal revisited node 4 and edge (4, 5) unexpectedly. Breaking loop.

This happens when there's one sticking out on its own. But this should be allowed. Or if a single edge joins two more complex graphs. Its a boundary you pass with the right-hand rule in one direction, then the other. You still traverse the entire outer perimeter. Fix the code to allow this.

### Phase 17: Advanced Color Network Reassignment

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
