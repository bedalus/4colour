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
- Even though I am English, use the American spelling of colour, i.e. color

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

### Phase 10: Allow lines to curve

This phase focuses on enhancing connections between circles by allowing lines to curve. Instead of implementing complex Bezier mathematics, we'll utilize Tkinter's built-in line smoothing capabilities (`create_line()` with `smooth=True`). Each connection will have an adjustable midpoint that users can drag to define the curve's shape. In Adjust mode, users will see and be able to interact with this midpoint, dragging it to create the desired curvature. The system will store the displacement vector (distance and direction) from the original midpoint and maintain these relationships when circles are moved.

- [x] **Design Simple Curve Data Structure:**
    *   Define how to store displacement data for each line's midpoint (x and y offsets from center):
        *   Enhance self.connections data storage capabilities so that x and y offsets from the center can be captured for any line that has been curved by the user, e.g. curve_X, curve_Y
    *   Determine how to integrate this displacement data with existing connection information:
        *   The values for curve_X and curve_Y offsets will be added to the existing data since each line has a unique connection_key
    *   Document the data structure for implementation reference:
        *   curve_X and curve_Y offsets are integer values that always exist in pairs.

- [x] **Implement Line Storage and Persistence:**
    *   Extend existing data structures to include X/Y displacement values for each connection in line with the above design.
    *   Create a method to calculate the default midpoint (straight line) between connected circles.
    *   Ensure displacement data is saved and loaded with other application data.
    *   Write utility functions to access and update the displacement data.

- [x] **Implement Curved Line Drawing:**
    *   Update line drawing code to use Tkinter's `create_line()` with `smooth=True`.
    *   Create a function to calculate the three points needed for each curved line (start, middle+displacement, end).
    *   Update the canvas rendering to display curved lines.
    *   Write tests to verify curve rendering with various displacement values.

- [x] **Add Midpoint Visualization:**
    *   Create a visual representation for the adjustable midpoint (small handle or dot).
    *   Implement conditional display logic to show midpoints only in Adjust mode.
    *   Add appropriate styling to make midpoints visually distinct from circles.
    *   Write tests to verify midpoint visualization behavior.

- [ ] **Implement Midpoint Interaction:**
    *   Add event handlers for midpoint selection and dragging.
    *   Create a mechanism to identify which line's midpoint was clicked.
    *   Implement real-time line updates during midpoint movement.
    *   Update the displacement vector data when drag is completed.
    *   Write unit tests to verify midpoint interaction behavior.

- [ ] **Update Circle Movement Logic:**
    *   Modify circle movement logic to maintain proper curved connections.
    *   Ensure that when circles move, the line midpoints maintain their relative position based on stored displacement.
    *   Write unit tests to verify line integrity during circle movement.

- [ ] **Create Comprehensive Unit Tests:**
    *   Develop test cases for midpoint displacement in different directions.
    *   Test the interaction with the midpoint handle and resulting line shapes.
    *   Add tests for edge cases (extreme displacements, overlapping lines).
    *   Create tests to validate curved line behavior across different application modes.

- [ ] **Update Documentation:**
    *   Add comments explaining the curve implementation and displacement calculations.
    *   Document the midpoint adjustment feature in user documentation.
    *   Update any relevant API documentation.

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
