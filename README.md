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

### Phase 13: Track the Clockwise Sequence of Connections to Circles

This phase focuses on developing a way of keeping track of the relative position of connections on each circle. Imagine the second hand of a clock sweeping around the clock-face. Which connection does it pass first, second, third, etc...? We need a way of capturing this order. The angle at which the connection arrives at the circle's centre will serve to provide this information, but there is an extra element of complexity, as we must account for the curvature of the connections which is goverened by the mid-point handles and Tkinter's line-smoothing math.

#### Tkinter's Line Smoothing Research Findings
Tkinter's Implementation: Tkinter's smooth=True option indeed uses a form of Bezier curves through the Tk Canvas API. For the case of three points (as in our application), it creates a quadratic Bezier curve.

Math Confirmation: The quadratic Bezier formula P(t) = (1-t)²P₀ + 2(1-t)tP₁ + t²P₂ correctly describes how our curves are rendered, where:

P₀ is the first circle's center
P₁ is our calculated midpoint (with any curve_X and curve_Y offsets applied)
P₂ is the second circle's center

Tangent Calculation: The derivative formulas in the plan are mathematically correct:

At the first endpoint (t=0): The tangent vector is 2(P₁ - P₀)
At the second endpoint (t=1): The tangent vector is 2(P₂ - P₁)

Implementation Feasibility: Looking at the existing code in ConnectionManager.calculate_curve_points(), we already have access to all the points needed for these calculations:

from_circle["x"], from_circle["y"]  # P₀
mid_x, mid_y  # P₁ (with offsets already applied)
to_circle["x"], to_circle["y"]  # P₂

Additional Insight: The calculate_midpoint_handle_position() method already implements similar math by applying half the curve offset, showing the existing code structure supports this type of calculation.

Conclusion: The plan is mathematically sound and achievable with the existing codebase. The tangent vector calculations will accurately determine the angle at which each connection enters/exits a circle, which is exactly what we need for ordering connections in a clockwise manner.

#### Implementation Plan

- [ ] **Implement Curve Tangent Calculation:**
    * Add a new method `ConnectionManager.calculate_tangent_vector(circle_id, other_circle_id)`:
        * This method should return the direction vector of the curve at the point it meets the specified circle's center.
        * Use the circle center coordinates and the midpoint handle position (with curve offset applied).
        * Calculate the tangent vector using the Bezier curve formula mentioned above.
        * Normalize the vector to make angle calculations consistent.
    
    * Add a method `ConnectionManager.calculate_connection_entry_angle(circle_id, other_circle_id)`:
        * Call `calculate_tangent_vector` to get the tangent vector.
        * Convert this vector to an angle in degrees using `math.atan2(dy, dx) * (180/math.pi)`.
        * Adjust the angle to be relative to North (vertical), clockwise from 0 to 360 degrees using `(90 - angle) % 360`.
        * Return this angle value.

- [ ] **Visualize Connection Entry Angles:**
    * Add a new method `UIManager.draw_angle_visualization_line(circle_id, other_circle_id, angle)`:
        * Takes the circle ID, connection ID, and the angle.
        * Calculates the line endpoint using trigonometry: 
          `x2 = circle_x + 3*circle_radius * sin(angle)`
          `y2 = circle_y - 3*circle_radius * cos(angle)`
        * Draws a grey line from the circle center to this calculated endpoint.
        * Makes the line non-interactive and tags it with "angle_viz" and the connection ID.
    
    * Add a method `UIManager.draw_connection_angle_visualizations(connection_key)`:
        * Extracts the two circle IDs from the connection_key.
        * For each circle, calculates its entry angle using `calculate_connection_entry_angle`.
        * Calls `draw_angle_visualization_line` for each circle with its calculated angle.
    
    * Modify `InteractionHandler.drag_midpoint_motion`:
        * Clear any existing "angle_viz" lines when dragging starts.
        * After updating the curve, call `draw_connection_angle_visualizations` with the current connection key.
    
    * Modify `InteractionHandler.drag_end`: 
        * Remove all "angle_viz" lines when dragging ends.
    
    * Modify `InteractionHandler.set_application_mode`:
        * Ensure "angle_viz" lines are cleared when exiting ADJUST mode.

- [ ] **Extend Circle Data Structure:**
    * Modify the circle data structure in `InteractionHandler.draw_on_click` to include:
        * `ordered_connections`: A list that will store connection information sorted by angle.
    
    * Create a data structure to store both the connection key (e.g., "1_2") and the angle value:
        * This can be a tuple `(connection_key, angle)` or a dictionary.
    
    * Update circle creation to initialize the `ordered_connections` list as empty.

- [ ] **Implement Connection Ordering Logic:**
    * Add a method `ConnectionManager.update_ordered_connections(circle_id)`:
        * Get the circle's data from `app.circle_lookup`.
        * Create a list of tuples containing `(connected_id, angle)` for each connection:
            * For each ID in `circle["connected_to"]`, calculate the angle using `calculate_connection_entry_angle`.
            * Store these values along with the connection ID.
        * Sort this list by angle values (ascending).
        * Update the circle's `ordered_connections` list with just the connection IDs/keys, discarding the angle values.
    
    * Add a helper method `ConnectionManager.get_connection_key(circle1_id, circle2_id)`:
        * Create a consistent key format (e.g., always putting the smaller ID first).
        * This ensures we can find the same connection regardless of which circle we start from.

- [ ] **Integrate Connection Ordering Updates:**
    * Modify `ConnectionManager.add_connection`:
        * After successfully adding a connection and updating the connection lists, call `update_ordered_connections` for both circles.
    
    * Modify `ConnectionManager.remove_circle_connections`:
        * Before removing the connection from a connected circle, store its ID.
        * After removing the connection, call `update_ordered_connections` for the stored connected circle ID.
    
    * Modify `ConnectionManager.update_connection_curve`:
        * After updating the curve, call `update_ordered_connections` for both circles involved.
    
    * Modify `InteractionHandler.drag_end`:
        * If a circle was dragged, call `update_ordered_connections` for the dragged circle and all its connections.
        * If a midpoint was dragged, call `update_ordered_connections` for both connected circles.

- [ ] **Verify Connection Ordering with Debug Information:**
    * Extend `UIManager.show_debug_info` to display the ordered connections list for the selected circle.
    * Optional: Add a visual debugging mode that shows numbered arrows indicating the connection order.

- [ ] **Add Comprehensive Unit Tests:**
    * Add tests for `calculate_tangent_vector` and `calculate_connection_entry_angle`:
        * Test with various circle positions (horizontal, vertical, diagonal).
        * Test with different curve offsets.
        * Verify the angles are in the expected range and direction.
    
    * Add tests for `update_ordered_connections`:
        * Test with 2, 3, and more connections.
        * Verify connections are correctly sorted by angle.
        * Test edge cases like connections at similar angles or angles across the 0/360 degree boundary.
    
    * Add tests for the integration of ordering updates:
        * Verify ordering is updated when connections are added/removed.
        * Verify ordering is updated when circles or midpoints are moved.

- [ ] **Documentation and Code Comments:**
    * Add clear documentation explaining the Bezier curve math.
    * Document how angles are calculated and the coordinate system used.
    * Add comments explaining how the connection ordering is determined and maintained.

#### Additional Considerations

* The angle calculation should account for the Tkinter coordinate system, where the y-axis increases downward.
* Consider edge cases where connections might have very similar angles.
* The visualization lines should be for debugging only and not affect the application's core functionality.
* The ordering should be robust when circles are moved or connections are adjusted, maintaining consistent clockwise ordering.

### Phase 14: Advanced Color Network Reassignment

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
