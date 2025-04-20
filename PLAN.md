# Project Plan: 4colour - Remaining Tasks (Phase 16 onwards)

This document outlines the remaining tasks for the 4colour project, focusing on completing Phase 16 and any subsequent work. Check the README.md document for previous work phase summaries.

Work items use checkboxes (`- [ ]`) and should be completed in sequential order. Mark tasks complete (`- [x]`) when both implementation and tests are finished. Update the Project Structure section when files change.

When adding new phases:
1. Use level 3 heading: `### Phase [Number]: [Brief Title]`
2. Include a summary paragraph explaining the goal
3. List tasks with main items in bold and nested bullet points for subtasks

## Phase 16: Centralize Red Node Logic

- [ ] **Isolate Red Node Logic into `fix_red.py`**
    * **Goal**: Create a dedicated module (`fix_red.py`) and move all existing red node management logic into it *without altering any current behavior*. This refactoring step prepares for future algorithm enhancements (Phase 17).
    * **Why**: Centralizes red node logic, improving modularity, maintainability, and separation of concerns.
    * **Critical Constraint**: **Absolutely NO functional changes** are permitted in this phase. The application's behavior regarding red node detection, handling, UI interaction (e.g., "Fix Red" button, mode transitions), and resolution must remain *identical* after this refactoring. This is purely a code relocation task.
    * **Steps**:
        1. **Identify & Document API**:
            - Thoroughly review `color_manager.py`, `interaction_handler.py`, `ui_manager.py`, and any other relevant files to locate *all* code related to red node handling (detection, state management, UI triggers, resolution attempts).
            - Precisely document the existing Application Programming Interface (API): method signatures, parameters, return values, and any side effects of the current red node logic.
        2. **Create `fix_red.py**:
            - Create the new file `c:\Users\david.savage\Source\4colour\fix_red.py`.
            - Define classes/functions within this new module.
        3. **Replicate API & Relocate Logic**:
            - Implement methods in `fix_red.py` that *exactly* match the documented API from Step 1.
            - Carefully move the identified red node logic from its original locations into the corresponding methods in `fix_red.py`.
        4. **Integrate via Delegation (Proxy Pattern)**:
            - In the original locations (e.g., `ColorManager`), instantiate the new red node handling class from `fix_red.py`.
            - Modify the original methods to simply delegate their calls to the corresponding methods in the new `fix_red.py` instance. Ensure the parameters and return values are passed through without modification.
            - **Crucially, do not change how other parts of the application (especially UI components) interact with the classes that *originally* contained the red node logic (e.g., `ColorManager`, `InteractionHandler`).** They should remain unaware of the internal delegation.
        5. **Verification**:
            - Test all application workflows, particularly those involving the creation and potential resolution of red nodes, to rigorously confirm that behavior is absolutely unchanged from before the refactoring.

## Phase 17: Advanced Color Network Reassignment

The goal of this phase is to enhance the 'fix red' system for complex graph scenarios. This phase will only begin after Phase 16 is fully completed and tested.

- [ ] **Fix Red Algorithm Improvements**
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