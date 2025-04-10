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

### Phase 8-9: Summary

Phases 8 and 9 focused on implementing deterministic coloring based on the Four Color Theorem, followed by optimization and refactoring. A color priority system (1=yellow, 2=green, 3=blue, 4=red) was established with utility functions to convert between priorities and color names. The application now assigns colors based on connections—when two connected circles have the same color, a conflict resolution algorithm assigns the lowest available priority color to ensure connected circles never share the same color. A placeholder for advanced network color reassignment was added for cases when all lower priorities are used. The codebase was then optimized by removing redundant color fields, since colors are now derived directly from priorities. Utility functions were extracted to a separate module to improve reusability and testability. Comprehensive unit tests were added for all the new functionality, ensuring the coloring logic works correctly across various scenarios.

### Phase 10: Summary

In this phase, connections between circles were enhanced with curved lines using Tkinter's built-in line smoothing capabilities. The implementation added adjustable midpoints that users can drag to define the curve's shape. These midpoints appear as small draggable handles in Adjust mode, allowing users to customize the curve's appearance. The system stores displacement vectors (X/Y offsets) for each connection, maintaining these curves when circles are moved. Comprehensive unit testing was added to verify curve behavior in different scenarios, including extreme displacements, different curve directions, overlapping connections, and interactions across different application modes.

### Phase 11: Advanced Color Network Reassignment

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
