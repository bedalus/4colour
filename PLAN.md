# Project Plan: 4colour - Remaining Tasks (Phase 16 onwards)

This document outlines the remaining tasks for the 4colour project, focusing on completing Phase 16 and any subsequent work.

## Phase 16: Advanced Color Network Reassignment (Remaining Tasks)

The goal of this phase is to enhance the color management system for complex graph scenarios and improve usability.

- [ ] **Fix Red Button**
    *   First, handle swapping and/or recolouring if a new red placed has not enclosed one (possible on a single width chain with a loop at the end).
    *   Second, handle if swapping a red to the interior results in two adjacent reds.
    *   Third, fourth, fifth... etc... if required.
    *   Finally, consider doing a swap between red and whichever other colour is the least used (use greatest priority for ties).
        *   This would mean re-running the algorithm for any reds that appeared on the border.

## Future Phases (Placeholder)

- [ ] **Document Algorithm and Implementation:**
    *   Add detailed comments explaining the color reassignment strategy in `color_manager.py`.
    *   The goal of the commentary should be to prove that the algorithm will always be successful in reconfiguring the graph to use only four colours.
    *   ...