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
        - Review `calculate_connection_entry_angle` and connection update logic in `connection_manager.py`.
        - Understand how entry angles are determined for each connection at both endpoint nodes.
    * b. Implement Angle Separation Constraint (User-Guided)
        - Create a helper function that, given a node and a connection, checks if the entry angle between the adjusted curve and any other connection at that node is within 2 degrees.
        - Use this helper for both endpoints of the connection being adjusted when the user drags the midpoint handle.
        - If the constraint is violated for either endpoint, display a warning hint to the user (e.g., "Warning: Connection angle too close to another. Adjust the midpoint until the warning clears.").
        - Do not attempt to fix the midpoint automatically; rely on the user to move the handle until the warning disappears.
    * c. Adapt Existing Functionality
        - Integrate this logic into the midpoint handle drag/release workflow, reusing or extending existing helper functions.
        - Ensure changes are compatible with `update_connection_curve` and UI update logic.
    * d. Test Incrementally
        - Test by dragging and releasing midpoint handles near other connections at both endpoints, especially with multiple connections at similar angles.
        - Run all unit tests.
    * e. Pitfalls & Warnings
        - Ensure the warning hint is clear and disappears as soon as the constraint is satisfied.
        - Avoid UI flicker or excessive warning messages.
        - Carefully handle edge cases where the constraint cannot be satisfied due to geometry.
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