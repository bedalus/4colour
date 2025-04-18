# Project Plan: 4colour - Remaining Tasks (Phase 16 onwards)

This document outlines the remaining tasks for the 4colour project, focusing on completing Phase 16 and any subsequent work.

## Phase 16: Advanced Color Network Reassignment (Remaining Tasks)

The goal of this phase is to enhance the color management system for complex graph scenarios and improve usability.

- [x] **Constrain curved line overlap and midpoint proximity**
    * a. Investigate
        - Review `draw_midpoint_handle`, midpoint drag event handlers, `calculate_midpoint`, and `calculate_curve_points` in `connection_manager.py`.
        - Identify how the midpoint handle is created, how its position is updated during dragging, and how the curve is redrawn.
    * b. Implement Minimum Distance Constraint (User Interaction)
        - When the user starts dragging a midpoint handle, capture and store the original valid position.
        - During drag and especially on release, check the distance between the new midpoint and each node (`from_circle`, `to_circle`).
        - If the midpoint is too close (define a threshold, e.g., 20 pixels), revert the handle and curve to the original position and provide user feedback if possible.
        - Only allow the curve to update if the constraint is satisfied.
    * c. Adapt Existing Functionality
        - Prefer adapting the handle drag/release logic and curve update logic rather than rewriting from scratch.
        - Ensure changes are compatible with how `update_connection_curve`, `draw_midpoint_handle`, and related UI logic work.
    * d. Test Incrementally
        - After implementing, manually test dragging and releasing midpoint handles near nodes, including edge cases.
        - Run all unit tests to ensure no regressions.
    * e. Pitfalls & Warnings
        - Be careful not to break existing connection rendering or handle movement.
        - Watch for edge cases where nodes are very close together or overlapping, and ensure the UI remains responsive.
        - Avoid situations where the handle becomes "stuck" or the user cannot recover from an invalid drag.
    * f. Hard Stop
        - Pause for review before proceeding to the next constraint.

- [x] **Enforce minimum angle separation at nodes**
    * a. Investigate
        - Review `calculate_connection_entry_angle` and connection update logic in `connection_manager.py`.
        - Understand how entry angles are determined for each connection at both endpoint nodes.
    * b. Implement Angle Separation Constraint (User-Guided)
        - Create a helper function that, given a node and a connection, checks if the entry angle between the adjusted curve and any other connection at that node is within 2 degrees.
        - Use this helper for both endpoints of the connection being adjusted when the user drags the midpoint handle.
        - If the constraint is violated for either endpoint, change the curve red. Change it back to black when the angle is greater than 3 degrees
        - Do not attempt to fix the midpoint automatically; rely on the user to move the handle until the warning disappears.
    * c. Adapt Existing Functionality
        - Integrate this logic into the midpoint handle drag/release workflow, reusing or extending existing helper functions.
        - Ensure changes are compatible with `update_connection_curve` and UI update logic.
    * d. User will Test Incrementally
        - Test by dragging and releasing midpoint handles near other connections at both endpoints, especially with multiple connections at similar angles.
    * e. Pitfalls & Warnings
        - Carefully handle edge cases where the constraint cannot be satisfied due to geometry.
        - Make use of the connection order to work out which other entry angles need to be calculated. It may be possible to discount some if there are many connections on the circle, as only the one before are valid candidates for the closest angle.
        - Remember this check needs to happen at both endpoints if a midpoint is being dragged.
        - Alternate between red and black continuously as required.
    * f. Hard Stop
        - Pause for review before proceeding.

- [x] **Node placement distance constraint**
    * a. Investigate
        - Review node creation logic in `canvas_app.py` and `circle_manager.py`.
        - Identify where new node coordinates are set and connections are proposed.
    * b. Implement Distance Assessment
        - When a new node is created, calculate its distance to the nearest node it will connect to.
        - If too close (define threshold), move the node further away, ideally along the vector from the average position of all connected nodes.
    * c. Adapt Existing Functionality
        - Modify node placement logic, not connection logic, to enforce this constraint.
    * d. Test Incrementally
        - Test node creation near existing nodes.
        - Run all unit tests.
    * e. Pitfalls & Warnings
        - Avoid moving nodes outside the visible canvas.
        - Ensure the UI updates correctly after repositioning.
    * f. Hard Stop
        - Pause for review before proceeding.

- [x] **Prevent connections to enclosed nodes**
    * a. Investigation Results:
        - Enclosed nodes are identified in `boundary_manager.py` using the `update_enclosure_status()` method, which sets `circle['enclosed'] = True/False`
        - The connection validation happens primarily in `interaction_handler.py` during the `confirm_selection()` method when the user presses 'y'
        - The `_update_enclosure_status()` method in `CanvasApplication` is called as a trigger point after modifying connections
        - Before new nodes are finalized (in `confirm_selection`), we need to add validation for enclosed status
        
    * b. Implement Check with Specific Logic:
        - Add a new helper method `has_enclosed_nodes(circle_ids)` in `CanvasApplication` that checks if any node in the list is enclosed
        - In `confirm_selection()` just before adding connections, check if any selected circle is enclosed:
          ```python
          if self.app.has_enclosed_nodes(self.app.selected_circles):
              # Show warning message to user:
              # Use either show_hint_text() or show_hint_text() if possible, copy from existing implementations elsewhere in the app.
              # Cancel the current placement (similar to pressing Escape)
              self.cancel_selection(None)
              return
          ```
      
    * c. Technical Considerations:
        - Use the existing enclosed status tracking rather than recalculating
        - For consistent user experience, avoid allowing selection of enclosed nodes from the start
        - The enclosure status is updated after each connection change, so timing of checks is critical
        
    * f. Implementation Approach:
        1. First implement the basic validation and cancellation logic
        2. Then add the feedback message
        3. Finally implement the selection restriction logic
        4. Test each component independently before integration
    
    * g. Expected User Experience:
        - User tries to connect a new circle to an enclosed node → Warning appears and placement is canceled

- **General Suggestions:**
    - Commit after each successful step.
    - Write or update unit tests for each constraint.
    - Document any new helper functions or logic.
    - Communicate with the team if you encounter unexpected complexity.

- [ ] **Fix and Enhance Unit Tests:**
    * Update test expectations in `test_color_manager.py` to match the new algorithm behavior.
    * Include tests for various graph configurations:
        - Linear chains
        - Cycles (odd and even length)

- [ ] **Document Algorithm and Implementation:**
    * Add detailed comments explaining the color reassignment strategy in `color_manager.py`.

## Future Phases (Placeholder)

*(Space for planning future phases beyond Phase 16)*