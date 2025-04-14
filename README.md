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

If running with runtime logging: python log_function_calls.py

To analyse the results*: python analyze_call_logs.py

(* if missing pandas/matplotlib, open a terminal as admin, then: pip install pandas matplotlib)

Install coverage if missing: pip install coverage (as an admin)

Run: python -m tests.run_coverage (normal user)

This runs all tests with coverage management and produces a report. Read tests/README.md for more detail.

## Planning

New work items should be itemized and preceded by an empty checkbox (`- [ ]`). When engaging in a new coding session to implement new features and improvements, follow the requirements in sequential order starting at the first unmarked checkbox. Once the feature and corresponding unit tests are written or updated to the required specification, mark the checkbox as complete ([x]) to track progress. Always remember to complete this step.

If new files are introduced, or if files are removed, update the '## Project Structure' section below accordingly.

**Introducing New Work Phases:**

When the current phase's objectives are complete or a new major area of work is identified, introduce a new phase at the end of this ReadMe file. Follow the following format:

1.  **Add a Phase Heading:** Use a level 3 Markdown heading with the format `### Phase [Number]: [Brief, Descriptive Title]`. Increment the phase number sequentially.
2.  **Write a Summary:** Immediately below the heading, add a short paragraph summarizing the overall goal or focus of this new phase. Explain *why* this work is being undertaken.
3.  **Structure Work Items:** List the specific tasks for the phase using the standard format:
    *   Start each major task with `- [ ] **Task Description:**`. Use bold text for the main task description.
    *   Use nested bullet points (`    * Sub-task or detail`) for breaking down the main task or adding specific implementation notes.

## Project Structure

The project is organized into the following key files and directories:

*   `README.md`: The current file. This outlines the goals of the project and can be updated as required, e.g. when planning.
*   `canvas_app.py`: The main application class that initializes the UI and managers.
*   `ui_manager.py`: Handles UI elements like buttons, hint text, and the debug overlay.
*   `circle_manager.py`: Manages circle data (creation, storage, retrieval, removal).
*   `connection_manager.py`: Manages connections between circles, including drawing lines, handling curves, and midpoint interactions.
*   `interaction_handler.py`: Processes user input events (clicks, drags, key presses) and manages application mode transitions.
*   `color_manager.py`: Implements the logic for assigning colors based on priority and resolving conflicts between connected circles.
*   `color_utils.py`: Provides utility functions for mapping color priorities to names and finding available priorities.
*   `app_enums.py`: Defines enumerations used across the application, such as `ApplicationMode`.
*   `boundary_manager.py`: Identifies outer boundary nodes and updates enclosure status.
*   `function_logger.py`: Instruments modules to log function calls for debugging and analysis.
*   `log_function_calls.py`: Runs the application with function call logging enabled.
*   `analyze_call_logs.py`: Analyzes function call logs to generate insights.
*   `tests/`: Contains all unit and integration tests:
    * `test_app_enums.py`: Tests for application enum definitions.
    * `test_boundary_manager.py`: Tests for boundary detection and enclosure status.
    * `test_canvas_app.py`: Tests for the main canvas application class.
    * `test_circle_manager.py`: Tests for circle creation, removal, and data management.
    * `test_color_manager.py`: Tests for color assignment and conflict resolution logic.
    * `test_color_utils.py`: Tests for color utility functions.
    * `test_connection_manager.py`: Tests for connection creation, curve management, and angle calculations.
    * `test_integration.py`: Tests for interactions between multiple components and workflows.
    * `test_interaction_handler.py`: Tests for user input handling, mode transitions, and drag/drop logic.
    * `test_ui_manager.py`: Tests for UI element management and display updates.
    * `test_utils.py`: Contains testing utilities and mock objects like `MockAppTestCase`.

### Phases 1-7 Summary

The initial development phases (1-7) established the core functionality of the canvas application. This included setting up the Tkinter UI, implementing basic circle drawing and random coloring on click, adding data storage for circle properties (ID, coordinates, color, connections), and introducing a mechanism to connect circles. A selection mode was implemented, allowing users to place a circle and then select existing circles to connect to, confirming with the 'y' key. An "adjust" mode was added to allow moving circles via drag-and-drop and removing circles via right-click. Significant refactoring occurred, including centralizing event binding management based on application modes (CREATE, ADJUST, SELECTION), improving mode transitions, enhancing UI feedback (button text, hint text, canvas background color changes), and consolidating circle removal logic.

### Phase 8-9: Summary

Phases 8 and 9 focused on implementing deterministic coloring based on the Four Color Theorem, followed by optimization and refactoring. A color priority system (1=yellow, 2=green, 3=blue, 4=red) was established with utility functions to convert between priorities and color names. The application now assigns colors based on connections—when two connected circles have the same color, a conflict resolution algorithm assigns the lowest available priority color to ensure connected circles never share the same color. A placeholder for advanced network color reassignment was added for cases when all lower priorities are used. The codebase was then optimized by removing redundant color fields, since colors are now derived directly from priorities. Utility functions were extracted to a separate module to improve reusability and testability. Comprehensive unit tests were added for all the new functionality, ensuring the coloring logic works correctly across various scenarios.

### Phase 10-11: Summary

Phase 10 enhanced connections with curved lines using Tkinter's smoothing, adding draggable midpoints to adjust curve shapes. Displacement vectors store curve offsets, maintained when circles move. Unit tests verified curve behavior in various scenarios.

Phase 11 expanded integration tests (`test_integration.py`) to cover complex component interactions. Tests were added for dragging circles and midpoints, ensuring coordinate and connection updates. Removal cascade tests were enhanced to verify neighbor updates and color conflict checks. New tests validated color conflict resolution during connections, the complete reset functionality of clearing the canvas, and the side effects of mode transitions (e.g., midpoint handle visibility, hint text display, background color changes).

### Phase 13-15: Summary

Phase 13 established a method to determine the clockwise order of connections around each circle, storing this in ordered_connections (connection_manager.py). This is necessary functionality for the 'Right-hand' rule commonly used in planar graphs when establishing the 'outer face'.

Phase 14 introduced the ability to distinguish between circles on the outer boundary and those enclosed within faces. The `enclosed` attribute was added to circle data, and the `_update_enclosure_status` method in `CanvasApplication` identifies boundary nodes on the 'outer face' using a traversal algorithm. The traversal relies on the clockwise `ordered_connections` list for each circle, ensuring accurate boundary detection even with curved connections. Tests were added to validate the enclosure status under various graph configurations.

Phase 15 ensured a consistent starting point for the outer face traversal by introducing two fixed nodes (Node A and Node B) connected by a fixed edge. These nodes are created at initialization and cannot be moved or removed. Proximity restrictions prevent placing new nodes or dragging midpoint handles into a restricted zone near the fixed nodes. The `_update_enclosure_status` method was updated to always start traversal from Node A. Tests were updated and added to verify the behavior of fixed nodes, proximity restrictions, and traversal logic.

### Phase 16: Update unit tests

Phase 13-15 took more development effort that originally anticipated, and the unit tests have drifted out of alignment.

- [x] **Conduct Test-Code Alignment Analysis:**
    * Systematically compare each application module with its corresponding test module
    * Create a detailed inventory of outdated tests, broken tests, and missing test coverage
    * Prioritize critical areas affected by recent changes (ordered_connections, boundary traversal, fixed nodes)
    * Determine which tests can be repaired versus which need complete rewrites

- [x] **Update Boundary Manager Tests:**
    * Enhance test_boundary_manager.py to properly test the new boundary traversal algorithm
    * Add tests for edge cases (disconnected components, single nodes, linear chains)
    * Create tests for boundary detection with various curve offsets that might affect angle calculations
    * Test boundary traversal with reused edges and revisited nodes

- [x] **Enhance Connection Manager Tests:**
    * Add tests for ordered_connections calculation and clockwise sorting logic
    * Create tests for connection angle calculations with and without curve offsets
    * Test midpoint handle positioning with relation to boundary traversal
    * Ensure connection updates properly trigger ordered connection recalculation

- [x] **Update Fixed Node Tests:**
    * Add tests for initialization and properties of fixed nodes
    * Verify fixed nodes cannot be moved or removed
    * Test proximity restrictions for circle placement near fixed nodes
    * Validate that fixed connections cannot be modified

- [x] **Enhance Integration Tests:**
    * Update existing test workflows to account for fixed nodes and proximity restrictions
    * Create complex test scenarios combining boundary detection, ordered connections, and user interactions
    * Test proper enclosure detection in nested graph configurations
    * Verify that mode transitions work correctly with updated functionality

- [x] **Update TestUtils and MockAppTestCase:**
    * Enhance the MockAppTestCase to properly initialize fixed nodes
    * Add helper methods for testing boundary detection
    * Create utilities for testing angle calculations and ordered connections
    * Update test circle creation to include the enclosure status field

- [x] **Implement Test Coverage Analysis:**
    * Set up coverage measurement for the test suite
    * Generate visual coverage reports to identify gaps
    * Ensure critical logic paths in boundary detection are well-tested
    * Add tests for any identified coverage gaps

- [x] **Review and Document Test Improvements:**
    * Document test patterns or edge cases for future reference
    * Create diagrams or visual aids to explain complex test scenarios
    * Update any test documentation to reflect new application behavior
    * Ensure all test files follow the same naming conventions and patterns

- [ ] **Enhance UI Manager Tests (61% coverage):**
    * Test visualization of angles and connection paths in debug display
    * Test UI state changes during different modes (colors, text, button states)
    * Verify button state management during mode transitions
    * Test hint text and debug overlay updating in various scenarios

- [ ] **Improve Color Manager Tests (71% coverage):**
    * Add tests for complex color conflict scenarios with K4 complete graphs
    * Test network reassignment when all priorities are used in a subgraph
    * Test color reassignment with fixed node color constraints
    * Verify proper color updates when connections are added or removed

- [ ] **Complete Boundary Manager Edge Cases (70% coverage):**
    * Test nested boundaries with "islands" inside graphs
    * Test boundary detection with overlapping faces and shared edges
    * Verify recovery from invalid ordered_connections edge cases
    * Test performance with large graph structures

- [ ] **Extend Interaction Handler Tests (83% coverage):**
    * Test complex user interactions with drag operations near canvas edges
    * Test interactions with fixed nodes and proximity limits
    * Test behavior when interacting with partially formed structures
    * Verify mode switching during active operations (e.g., drag during mode switch)

### Phase 17: Advanced Color Network Reassignment

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

# 4colour Canvas Application

A graph-based canvas application demonstrating the four color theorem through interactive visualization.

## Features and Progress

### Core Functionality
- [x] Basic canvas application setup
- [x] Fixed reference nodes
- [x] Circle creation and management
- [x] Connection management between circles
- [x] Color assignment based on the four color theorem
- [x] Boundary and enclosure detection

### User Interface
- [x] Create mode - add new circles
- [x] Selection mode - connect circles
- [x] Adjust mode - move circles and curve connections
- [x] Debug overlay
- [x] UI mode transitions

### Graph Operations
- [x] Automatic color conflict resolution
- [x] Connection creation with click and select
- [x] Connection curve adjustments
- [x] Circle removal with proper cleanup
- [x] Ordered connections for boundary traversal

### Testing
- [x] Canvas application tests
- [x] UI Manager tests - improved from 61% to 95% coverage
- [x] Circle Manager tests 
- [x] Connection Manager tests
- [x] Color Manager tests - improved from 71% to 94% coverage
- [x] Boundary Manager tests
- [x] Integration tests for component interactions
- [x] Helper utilities for testing

## Phase 16 Improvements
- [x] Enhanced test utilities for boundary detection and angle calculations
- [x] Improved UI Manager tests with comprehensive coverage
- [x] Complete tests for Color Manager including complex scenarios
- [x] Comprehensive Boundary Manager edge case tests
- [x] Additional integration tests to verify cross-component interactions
- [ ] Code refactoring based on test coverage analysis
- [ ] Documentation improvements

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/yourusername/4colour.git
cd 4colour
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python canvas_app.py
```

## Testing

Run the test suite:

```bash
python -m unittest discover tests
```

Run coverage analysis:

```bash
python -m tests.run_coverage
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request
