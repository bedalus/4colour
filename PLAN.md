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

- [ ] **Refactor Red Node Management**
    *   Replace the direct instance variables (`red_node_id`, `next_red_node_id`) with a structured `RedNodeManager` class
    *   Create a `RedNodeQueue` that maintains an ordered list of red nodes needing attention
    *   Implement methods for adding, removing, and prioritizing red nodes
    *   Add state tracking to distinguish between different types of red node problems
    *   Create a clear API for other components to interact with red nodes:
        * `add_red_node(node_id, reason)`: Adds a node to the queue with context
        * `get_current_red_node()`: Returns the current node to be fixed
        * `advance_to_next_red_node()`: Moves to the next node in the queue
        * `has_red_nodes()`: Check if any red nodes need attention
    *   Update all references in color_manager.py to use the new API
    *   Adapt interaction_handler.py:
        * Update `switch_to_red_fix_mode()` to use the RedNodeManager
        * Modify drag event handling to consider red node state
        * Update the button enablement logic based on red node queue status
    *   Adapt ui_manager.py:
        * Modify the clear_canvas method to reset the red node queue
        * Update debug information display to show red node queue status
        * Create visualization helpers for red nodes and their connected components
    *   Add comprehensive logging to track red node state transitions

## Future Phases (Placeholder)

- [ ] **Document Algorithm and Implementation:**
    *   Add detailed comments explaining the color reassignment strategy in `color_manager.py`.
    *   The goal of the commentary should be to prove that the algorithm will always be successful in reconfiguring the graph to use only four colours.
    *   ...