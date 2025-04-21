# Project Plan: 4colour - Remaining Tasks (Phase 17 onwards)

This document outlines the remaining tasks for the 4colour project, focusing on completing Phase 17 and any subsequent work. Check the README.md document for summaries of previous work phases.

Work items use checkboxes (`- [ ]`) and should be completed in sequential order. Mark tasks complete (`- [x]`) when both implementation and tests are finished. Update the Project Structure section when files change.

When adding new phases:
1. Use level 3 heading: `### Phase [Number]: [Brief Title]`
2. Include a summary paragraph explaining the goal
3. List tasks with main items in bold and nested bullet points for subtasks

## Phase 17: Advanced Colour Network Reassignment

The goal of this phase is to enhance the Kempe system for complex graph scenarios.

- [x] **VCOLOR-Node exchange algorithm: Kempe Chain Improvements and constraints**
    *   Kick off trigger will be when placing a new node creates a conflict resulting in a priority 5 'VCOLOR-node'.
    *   Use Kempe chain to decide on some pairing of yellow, green, blue or red suitable for colour exchange.
    *   If the 'VCOLOR-node' can now be recoloured to use one of the four colours, then the algorithm is finished. If not, it should call itself again (be careful of infinite recursion). UPDATE: recursion not needed in the end.
    *   Finally, check which is the most used colour on the border nodes (the graph's outer face). Perform an exchange between that colour and whichever other colour is the least used in the entire graph (using colour priority for ties). This should help keep the colour distribution even.

## Phase 18

- [x] **Document Algorithm and Implementation:**
    *   Add detailed comments explaining the colour reassignment strategy in reassign_color_network (`fix_VCOLOR.py`).
    *   The goal of the commentary should be to prove that the algorithm will always be successful in reconfiguring the graph to use only four colours.

## End

- [x] **Self Assessment**
    *   Turned out alright on the night.
    *   Might as well keep this file, shows how I kept tasks organised.
