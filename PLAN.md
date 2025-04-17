# Project Plan: 4colour - Remaining Tasks (Phase 16 onwards)

This document outlines the remaining tasks for the 4colour project, focusing on completing Phase 16 and any subsequent work.

## Phase 16: Advanced Color Network Reassignment (Remaining Tasks)

The goal of this phase is to enhance the color management system for complex graph scenarios and improve usability.

- [ ] **Prevent excessive curvature of connections:**
    * Curved lines are allowed, but should be constrained to help prevent overlaps.
    * Do not allow the midpoint too close to either of its attached nodes.
    * If connections at either connected node are within 2 degrees, automatically adjust the midpoint to increase the angle of separation to at least 3 degrees.
    * When the user creates a new node, assess the distance to the closest node that the user wants to connect too, and if it is too close, move the node further away from the average position of all the connected nodes.
    * DO NOT ALLOW the user to place a node that is connected to any enclosed node. If so, delete the new node and its connections.

- [ ] **Fix and Enhance Unit Tests:**
    * Update test expectations in `test_color_manager.py` to match the new algorithm behavior.
    * Include tests for various graph configurations:
        - Linear chains
        - Cycles (odd and even length)

- [ ] **Document Algorithm and Implementation:**
    * Add detailed comments explaining the color reassignment strategy in `color_manager.py`.

## Future Phases (Placeholder)

*(Space for planning future phases beyond Phase 16)*