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
    *   Use nested bullet points (`    *   Sub-task or detail`) for breaking down the main task or adding specific implementation notes.

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

### Phase 13: Track the clockwise sequence of connections to circles

This phase focuses on developing a way of keeping track of the relative position of connections on each circle. Imagine the second hand of a clock sweeping around the clock-face. Which connection does it pass first, second, third, etc...? We need a way of capturing this order. The angle at which the connection arrives at the circle's centre will serve to provide this information, but there is an extra element of complexity, as we must account for the curvature of the connections which is goverened by the mid-point handles and Tkinter's line-smoothing math.

- [ ] **Visualize the impact of Tkinter's line-smoothing at the centre of the circle:**
    *   Extend the graphical capabilities of the ADJUST mode such that whenever a mid-point handle is being moved, two additional lines are drawn originating from both connected circles. They should be grey and cannot be interacted with directly by the user. These are straight lines with a length equivalent to three times the width of one standard circle. The line drawing function should be generic and reusable since it needs to be called twice for each circle associated with a curve. Each line must protrude at the same angle at which the curved connection arrives at the circle centre. This will require determining the most appropriate Bezier curve math that can transform the co-ordinates of the two circles and the connection mid-point handle into the angle we require. Design this angle determination function as a generic reusable method within the most appropriate code module.

- [ ] **Extend the circle data tracking capabilities:**
    *   The existing code already has data tracking capabilities for each circle, including some information about the connections (identified by their line_id). Extend that tracking functionality to allow for the storage of an ordered list of line_ids. The list will need to include every line_id that is connected in sequential order from the smallest angle to largest angle (relative to vertical). We can reuse the method from the previous work item to provide each angle, using that information to determine the clockwise sequence. Once the ordered list is stored, the angle information can be discarded.
    *   The required code needs to be a generic reusable function or method.
    *   The ordered list needs to be updated when a new circle is created in CREATE mode for the new circle, and any other circles it has been connected to. The list also needs to be updated in ADJUST mode for both circles that are connected by a midpoint handle, if one is moved. Also in ADJUST mode, if a circle is moved, the list needs to be recalculated for the moved circle, and any other circles it is connected to.

### Phase 13: Advanced Color Network Reassignment

This phase focuses on developing a sophisticated algorithm for reassigning colors throughout the network of connected circles when simple conflict resolution is insufficient. Currently, the application assigns priority 4 (red) as a fallback, but a more optimal solution would rearrange existing colors to maintain the Four Color Theorem guarantee.

- [ ] **Design Network Reassignment Algorithm:**
    *   Define a graph traversal approach for analyzing the network of connected circles
    *   Develop strategy for identifying color reassignment opportunities (e.g., swapping colors between distant circles)
    *   Determine stopping conditions to prevent infinite loops during recursive traversal
    *   Document the algorithm design with clear pseudocode or diagrams for implementation reference

- [ ] **Implement Network Analysis Functions:**
    *   Create helper functions in `color_utils.py` to analyze graph properties relevant for coloring
    *   Implement functions to identify color domains, conflict regions, and potential reassignment candidates
    *   Add utility functions to test whether a proposed coloring solution is valid
    *   Write unit tests for these utility functions with various graph configurations

- [ ] **Implement Core Reassignment Logic:**
    *   Replace the placeholder implementation in `_reassign_color_network()` with the new algorithm
    *   Develop a recursive function that can traverse the circle network and test different color assignments
    *   Implement backtracking capability to revert unsuccessful color assignments during traversal
    *   Ensure the implementation prioritizes using colors 1-3 (yellow, green, blue) and minimizes use of color 4 (red)
    *   Add appropriate error handling for edge cases (circular references, disconnected components)

- [ ] **Add Performance Optimizations:**
    *   Implement memoization or caching to avoid redundant calculations during traversal
    *   Add early termination conditions for branches that cannot lead to valid solutions
    *   Optimize the algorithm to prefer minimal color changes when resolving conflicts
    *   Consider adding a complexity threshold beyond which a simpler fallback solution is used

- [ ] **Update UI Feedback for Reassignment:**
    *   Implement visual feedback when network reassignment occurs (e.g., brief animation, status message)
    *   Add optional debugging overlay to visualize the reassignment process for educational purposes
    *   Ensure all circle colors update smoothly after network reassignment

- [ ] **Create Comprehensive Unit Tests:**
    *   Develop test cases for various network configurations (linear chains, loops, complete graphs, etc.)
    *   Add tests for edge cases like maximum connections and highly constrained networks
    *   Implement tests to verify the algorithm's performance characteristics
    *   Create tests that validate the four-color theorem is maintained across the application

- [ ] **Update Documentation:**
    *   Add detailed comments explaining the network reassignment algorithm
    *   Include high-level description of the algorithm in code documentation
    *   Document any limitations or known edge cases for future reference
