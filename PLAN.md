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

- [ ] **Enforce minimum angle separation at nodes**
    * a. Investigate
        - Review `calculate_connection_entry_angle`, `update_ordered_connections`, and midpoint handle adjustment/redraw logic in `connection_manager.py`.
        - Understand how entry angles are determined for each connection at both endpoint nodes.
    * b. Implement Angle Separation Constraint (Continuous Redraw After Handle Release)
        - After the midpoint handle is released, check both endpoint nodes.
        - For each node, compare the entry angle of the newly adjusted curve with all other connections at that node.
        - If the entry angle between the new curve and any other connection is within 2 degrees, begin an adjustment loop:
            - Move the midpoint handle position along the vector normal (perpendicular) to the line connecting the two endpoint nodes, in small increments.
            - After each adjustment, immediately redraw the handle and curve so the user sees the handle's position updating in real time.
            - Repeat this process rapidly until the constraint is satisfied for both nodes or a maximum number of iterations is reached.
        - If the constraint cannot be satisfied after a reasonable number of attempts, revert to the previous valid position and provide user feedback if possible.
        - The handle must remain visible and update continuously throughout this process.
    * c. Adapt Existing Functionality
        - Integrate this logic into the midpoint handle release workflow, reusing or extending existing helper functions.
        - Ensure changes are compatible with `update_connection_curve` and UI update logic.
    * d. Test Incrementally
        - Test by releasing midpoint handles near other connections at both endpoints, especially with multiple connections at similar angles.
        - Run all unit tests.
    * e. Pitfalls & Warnings
        - Avoid infinite or excessively long adjustment loops.
        - Ensure the UI remains responsive and the handle does not "jump" erratically.
        - Carefully handle edge cases where the constraint cannot be satisfied.
    * f. Hard Stop
        - Pause for review before proceeding.

- [ ] **Node placement distance constraint**
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

- [ ] **Prevent connections to enclosed nodes**
    * a. Investigate
        - Review how enclosed nodes are identified (likely in `boundary_manager.py` or related logic).
        - Check where new connections are validated.
    * b. Implement Check
        - Before finalizing a new node and its connections, check if any target node is enclosed.
        - If so, delete the new node and its connections immediately.
    * c. Adapt Existing Functionality
        - Integrate this check into the node creation workflow.
    * d. Test Incrementally
        - Test by attempting to connect to enclosed nodes.
        - Run all unit tests.
    * e. Pitfalls & Warnings
        - Ensure deletion is clean (no orphaned references).
        - Avoid false positives—only block truly enclosed nodes.
    * f. Hard Stop
        - Pause for review before proceeding.

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