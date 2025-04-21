# 4colour - Visual Four Colour Theorem Implementation

This project provides an interactive visualization and implementation of the Four Colour Theorem, demonstrating that any planar graph can be coloured using at most four colours such that no adjacent nodes share the same color. [Four Colour Theorem (Wikipedia)](https://en.wikipedia.org/wiki/Four_color_theorem) - Background on the maths that this project demonstrates.

## Acknowledgments

This project utilizes the concept of **Kempe chains**, a mathematical technique introduced by Alfred Kempe in the context of graph colouring and the four-color theorem. Special thanks to Alfred Kempe for his contributions to mathematics, which have inspired this work.

Thanks also to the creators and maintainers of the following tools and services:

- **Python**: My first time using it. I like it! I used v3.13.3.
- **GitHub Copilot**: For its cost-effective AI-assisted coding subscription service.
- **Visual Studio Code**: The IDE I use daily for work and now also for this side project!
- **Roo Code**: For its effective VS Code extension that enhances the AI-assisted coding experience.
- **Claude Sonnet 3.7**, **GPT 4.1**, **o3 mini** and **Gemini 2.5 Pro** provided by Anthropic, OpenAI, and Google. These LLMs really did the bulk of the coding. I had only modest expectations of these tools, and while in practice one *"create a method that..."* was usually followed by five "*I now have a bug that..."* statements, I know I could not have got this working without their astonishing capabilities.

## Running the App

You can either clone the repo and run it with ```python canvas.app```
or download a Windows 64-bit executable here: https://github.com/bedalus/4colour/releases/tag/release

The Windows 64-bit executable was compiled using nuitka: https://nuitka.net/user-documentation/

Tkinter isn't supported yet for compilation using python 3.13 so I went back to 3.12, i.e.

```PowerShell
py.exe -3.12 -m nuitka canvas_app.py --mode=onefile --enable-plugin=tk-inter --follow-imports --include-package-data=package_name
```

## How It Works

**tl;dr**: Just play with it!

The app can be maximised to fill the available screen space if needed (or drag the window border).

Left-click to place a node on the canvas. Two are already present and connected together.

After placing your node, click on one or more nodes to select them (they can be clicked a second time to deselect them). All your selected nodes are underlined. When ready, press the 'y' key on your keyboard, and the connections will be drawn. You are not allowed to create a node within the interior, or try to create a connection to an enclosed node. This reflects that all possible planar graphs can be incrementally constucted.

Click the button near the top to enter 'Adjust' mode. The last node created can be moved, connections can be adjusted by their midpoint handle, if you need to bend one around a corner. To produce a valid graph, the connections (aka edges) must not overlap. If the entry angle of two connections on the same node is too close, one of the connections will turn red to help indicate the issue.

If a new node is connected to others that span the four available colours (yellow, green, blue, red) then the canvas automatically switches into 'Adjust' mode (so you can tweak the node position and curve the connections). The usual toggle button is replaced by a 'Fix' button for fixing the graph. Kempe chains are used to reorder existing colours to make one available where the new node has been placed, making it possible to retain the 'four colouring'.

It seemed to me that it would be a good idea to make sure the overall graph colouring stayed balanced between the colours. I'd already programmed 'outer face' or boundary node detection to help with the UI, and later realised I could also use it in the balancing mechanism. Basically, after the graph is fixed, the *most* used colour on the graph's outer face is exchanged with whichever other colour is the *least* used in the entire graph. This seems counter-intuative at first, but the outer-face generally constitutes a large proportion of any graph as it grows incrementally. Swapping the most used outer-face nodes with the least used overall helps prevent overuse of any single colour. This should help reduce Kempe chain complexity and result in more efficient processing. So if you click the 'Fix' button and see the entire graph apparantly reshuffled, this is why.

Near the top of canvas_app.py there are some constants you might want to adjust:
- PROXIMITY_LIMIT = 75  # Increased proximity limit (was 50)
- self.root.geometry("800x600")
- self.canvas_width = 800
- self.canvas_height = 600
- self.circle_radius = 10
- self.midpoint_radius = 5  # Size of the midpoint handle

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
- Write unit tests for all new features or changes. Include documentation for running the unit tests in a top level folder called 'tests'.

## Project-Specific Rules
- Use `snake_case` for variables and functions.
- Use `PascalCase` for classes.
- Ensure all code passes linting and formatting checks before committing.
- Use lowercase names for folders.

## Planning

Use the PLAN.md file for all planning and tracking. Use this file for summaries when work phases are completed.

## Project Structure

The project is organised into the following key files and directories:

*   `README.md`: Current file. Project goals, summaries of initial development phases
*   `LICENSE.md`: Licensing terms for the project.
*   `PLAN.md`: Development planning and tracking
*   `canvas_app.py`: Main application class with event delegation
*   `app_enums.py`: Application enumerations like ApplicationMode
*   `ui_manager.py`: UI element management and visualization
*   `circle_manager.py`: Circle data operations and lifecycle
*   `connection_manager.py`: Connection management, curve calculation, and angle validation
*   `interaction_handler.py`: User input processing, drag operations, and mode transitions
*   `color_manager.py`: VCOLOR assignment operations
*   `color_utils.py`: VCOLOR utility functions and priority mappings
*   `boundary_manager.py`: Boundary node identification and enclosure status
*   `fix_VCOLOR.py`: VCOLOR node management and conflict resolution ('V' is the Roman Numeral for 5)
*   `function_logger.py`, `log_function_calls.py`, `analyze_call_logs.py`: Debugging tools

### Component Relationships

*   `canvas_app.py` serves as the main controller, delegating to specialised managers
*   The Managers focus on specific domains (UI, circles, connections, colours, boundaries)
*   `interaction_handler.py` processes user input and coordinates with managers
*   `app_enums.py` provides consistent mode definitions across components
*   `fix_VCOLOR.py` centralizes colour conflict resolution logic

# Development Phases

Pushed directly to main with frequent fixups and rebasing. If you're the sort of person who enjoys histories, I apologise.
**Top tip**: Do not perform a global find-and-replace without first making a commit you can revert back to! 

## Phase Summaries

### Phases 1-7 Summary

The initial development phases established core functionality: Tkinter UI, circle drawing with colouring, data storage, connection mechanisms, selection mode for connecting circles, adjust mode for moving/removing circles, and event binding management with improved mode transitions and UI feedback.

## Phase 8-9: Summary

These phases implemented deterministic colouring based on the Four Colour Theorem with a priority system (1=yellow, 2=green, 3=blue, 4=red), conflict resolution, and codebase optimization.

### Phase 10-11: Summary

Phase 10 added curved connections with draggable midpoints using displacement vectors. Phase 11 expanded integration tests covering interactions between components, including drag behavior, removal cascades, colour conflict resolution, and mode transition side effects.

### Phase 13-15: Summary

Phase 13 implemented clockwise connection ordering. Phase 14 added boundary detection to distinguish between outer and enclosed circles. Phase 15 introduced fixed nodes for consistent traversal starting points and proximity restrictions.

### Phase 16: Summary

Phase 16 centralised all colour node logic and state into the new `fix_VCOLOR.py` module, with `ColorManager` and related classes delegating colour node operations. This refactor improved modularity and prepared the codebase for the main feature.

### Phase 17: Summary

Phase 17 focused on improving the colour reassignment system for complex graphs by introducing a queue-driven approach to resolving colour nodes and implementing Kempe chain swaps. The process ensures that all nodes can be coloured using only four colours, and includes an additional step to balance colour usage by swapping the most and least used colours across the graph. This iterative method enhances both the robustness and efficiency of the colouring algorithm.