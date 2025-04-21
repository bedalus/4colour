# Project Plan: 4colour - Remaining Tasks (Phase 16 onwards)

This document outlines the remaining tasks for the 4colour project, focusing on completing Phase 16 and any subsequent work. Check the README.md document for previous work phase summaries.

Work items use checkboxes (`- [ ]`) and should be completed in sequential order. Mark tasks complete (`- [x]`) when both implementation and tests are finished. Update the Project Structure section when files change.

When adding new phases:
1. Use level 3 heading: `### Phase [Number]: [Brief Title]`
2. Include a summary paragraph explaining the goal
3. List tasks with main items in bold and nested bullet points for subtasks

## Phase 17: Advanced Color Network Reassignment

The goal of this phase is to enhance the Kempe system for complex graph scenarios.

- [ ] **Black-Node exchange algorithm: Kempe Chain Improvements and constraints**
    *   Kick off trigger will be when placing a new node creates a conflict resulting in a priority 5 'black-node'.
    *   Use Kempe chain to decide on some pairing of yellow, green, blue or red suitable for color exchange.
    *   If the 'black-node' can now be recolored to use one of the four colors, then the algorithm is finished. If not, it should call itself again (be careful of infinite recursion).
    *   Finally, check which is the most used color on the border nodes (the graph's outer face). Perform an exchange between that color and whichever other colour is the most used (using color priority for ties).

## Future Phases (Placeholder)

- [ ] **Document Algorithm and Implementation:**
    *   Add detailed comments explaining the color reassignment strategy in reassign_color_network (`fix_black.py`).
    *   The goal of the commentary should be to prove that the algorithm will always be successful in reconfiguring the graph to use only four colours.
