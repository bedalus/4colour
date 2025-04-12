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

### Phase 14: Track which circles form a border at the outer edge of the map

This phase aims to establish tracking of the outer border of the map. Circles will be classed as 'outer' if they are not enclosed by other circles and connections. The most basic example of an enclosure is a triangle arrangement with one circle in the middle; the middle one would be classed as 'enclosed'. This 'enclosed' status (True/False) will be stored as a boolean attribute for each circle. This information is crucial for Phase 15, where the red color (priority 4) might need to be preferentially assigned to or swapped from an 'outer' circle.

The determination of which circles are 'outer' (not enclosed) will be done using an outer face traversal algorithm on the graph formed by circles and connections. This assessment must be triggered whenever the graph's topology or geometry changes significantly, such as adding/removing circles or connections, or moving circles or connection midpoints (as this affects connection angles and thus `ordered_connections`).

- [x] **Preliminary Research Stage**
    *   ~~Figure out what sort of algorithm we need to be able to 'walk' the circles forming the outer border.~~ **Chosen Algorithm:** Outer Face Traversal using `ordered_connections`.
    *   ~~The algorithm should be triggered every time a reassessment is required, i.e. a circle added or removed, or its position adjusted, or a connection midpoint is moved.~~ **Trigger Points:** Identified (see Implementation Stage 2).
    *   ~~It should make use of the ordered_connections information to know that it is 'walking' to the next 'border' and not and interior circle that is 'enclosed'~~ **Mechanism:** Use the clockwise order in `ordered_connections` relative to the incoming edge to determine the next edge on the outer face boundary.
    *   ~~When the understanding is deep enough, flesh out the impementation plan below with additional stages. The planning should be suitable for a mid-level developer to be able to follow step-by-step, with plenty of technical detail, code suggestions, warnings about potential pitfalls, but must not state the obvious. Assume the developer has a good awareness of the existing project codebase. Adhere to the 'contribution guidelines' in this document.~~ **Done.**

- [x] **Implementation Stage 1: Add 'enclosed' Attribute**
    *   Modify the `InteractionHandler.draw_on_click` method (in `interaction_handler.py`) to add a new key-value pair `enclosed: False` to the dictionary representing each new circle. This ensures all circles start with a default status.
    *   Update any relevant unit tests for circle creation (`test_circle_manager.py` or relevant interaction tests) to check for the presence and default value of this new attribute.

- [ ] **Implementation Stage 2: Implement Outer Face Traversal Algorithm**
    *   Create a new method, potentially `_update_enclosure_status(self)`, within the main `CanvasApplication` class (`canvas_app.py`). This method will encapsulate the logic for finding the outer border and updating the `enclosed` status of all circles.
    *   **Inside `_update_enclosure_status`:**
        *   Handle edge cases: If there are 0, 1, or 2 circles, none are enclosed. Set `enclosed = False` for all and return early.
        *   **Find Starting Node:** Identify a circle guaranteed to be on the outer boundary. A reliable choice is the circle with the minimum y-coordinate. If there's a tie, use the minimum x-coordinate among those tied. Store its ID in `start_node_id`. Handle the case where no circles exist.
        *   **Initialize Traversal:**
            *   Create an empty set `outer_border_ids = set()`.
            *   Set `current_node_id = start_node_id`.
            *   Determine the "entry edge" for the `start_node_id`. Since it's the lowest point, we can conceptually imagine entering it from infinitely far below, corresponding to an *entry* angle of 0 degrees (North). Store this as `entry_angle`. Alternatively, find its connection with the largest clockwise angle and start from there. A simpler approach might be to pick its first connection in `ordered_connections` as the initial exit edge. Let's refine this:
                *   Find the connection to `start_node_id` that has the *largest* entry angle (closest to 360 degrees, just before North). The *next* connection clockwise from this one will be the first edge of the outer boundary walk. Let the node connected via this first edge be `next_node_id`.
                *   If `start_node_id` has only one connection, the graph is linear; handle appropriately (both nodes are outer).
            *   Set `previous_node_id = start_node_id`.
            *   Set `current_node_id = next_node_id`. Add `start_node_id` to `outer_border_ids`.
        *   **Traversal Loop:** Start a loop that continues until `current_node_id == start_node_id`.
            *   Add `current_node_id` to `outer_border_ids`.
            *   Get the `current_circle = self.circle_lookup[current_node_id]`.
            *   Get its `ordered_connections`. If empty or only contains `previous_node_id`, handle potential errors or edge cases (e.g., dangling node).
            *   Find the index of `previous_node_id` within `ordered_connections`.
            *   Determine the index of the *next* node in the clockwise order: `next_index = (previous_node_index + 1) % len(ordered_connections)`.
            *   Get the `next_node_id = ordered_connections[next_index]`.
            *   Update for the next iteration: `previous_node_id = current_node_id`, `current_node_id = next_node_id`.
            *   Include a safety break (e.g., max iterations based on number of circles) to prevent infinite loops in case of unexpected graph states.
        *   **Update Status:** After the loop completes, iterate through `self.circle_lookup.values()`. For each `circle`, set `circle['enclosed'] = (circle['id'] not in outer_border_ids)`.

- [ ] **Implementation Stage 3: Integrate Algorithm Trigger Points**
    *   Identify all places where the graph structure or geometry changes significantly enough to potentially alter which circles are enclosed.
    *   Call `self._update_enclosure_status()` at the end of these operations:
        *   `InteractionHandler._on_canvas_click` (after a circle is successfully created in CREATE mode).
        *   `InteractionHandler.confirm_selection` (after connections are successfully added).
        *   `InteractionHandler._remove_circle` (after a circle and its connections are removed). Ensure `ordered_connections` for neighbors are updated *before* calling the enclosure update.
        *   `InteractionHandler._on_circle_release` (after a circle drag is completed). Ensure `ordered_connections` for the moved circle and its neighbors are updated first.
        *   `InteractionHandler._on_midpoint_release` (after a midpoint drag is completed). Ensure `ordered_connections` for the two connected circles are updated first.
    *   **Refactor Prerequisite:** Ensure that `ConnectionManager.update_ordered_connections` is reliably called *before* `_update_enclosure_status` in the ADJUST mode drag release handlers (`_on_circle_release`, `_on_midpoint_release`).

- [ ] **Implementation Stage 4: Unit Testing**
    *   Create new tests in `test_integration.py` or potentially a new `test_geometry.py`.
    *   Test `_update_enclosure_status` directly with various pre-defined graph structures:
        *   Empty graph, single circle, two connected circles.
        *   Triangle (all outer).
        *   Square (all outer).
        *   Triangle with one circle inside (inner circle should be `enclosed=True`).
        *   Square with one circle inside.
        *   More complex structures with multiple enclosed circles.
        *   Test cases where moving a circle or midpoint changes the enclosure status.
    *   Verify that the `enclosed` status is correctly updated after operations like adding/removing circles/connections in integration tests.

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
