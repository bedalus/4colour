# Contribution Guidelines

NOTE: These guidelines apply only to code in the 4colour repo.

## Coding Standards
- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python or equivalent standards for other languages.
- Use meaningful variable and function names.
- Write modular, reusable, and succinctly documented code. To avoid clutter, do not document self-explanatary code.

## General Rules
- Always include comments for complex logic.
- Avoid hardcoding values; use configuration files or constants.
- Write unit tests for all new features or changes. Include documentation for running the unit tests in a top level folder called 'tests'

## Project-Specific Rules
- Use `snake_case` for variables and functions.
- Use `PascalCase` for classes.
- Ensure all code passes linting and formatting checks before committing.
- Use lowercase names for folders.

## Commit Messages
- Use descriptive commit messages.
- Follow the format: `<type>: <short description>` (e.g., `feat: add user authentication`).

## Planning

### Coding Plan

The initial phase focuses on creating the user interface using `tkinter`.

1.  **Setup Tkinter Window:**
    *   Create the main application window.
    *   Set the window title and initial size.
2.  **Create Canvas Widget:**
    *   Add a `tkinter.Canvas` widget to the main window.
    *   Configure the canvas dimensions and background color.
3.  **Implement Drawing on Click:**
    *   Bind mouse click events to the canvas.
    *   Implement simple functions to draw a small circle on the canvas wherever the user has clicked.
4.  **Add Canvas Resizing Controls:**
    *   Create '+' and '-' buttons.
    *   Position the buttons in the top-left corner (potentially overlaying the canvas or in a separate frame).
    *   Implement functions bound to these buttons to increase/decrease the canvas widget's dimensions by a sensible increment (e.g., 50 pixels).
    *   Ensure existing drawings are handled appropriately on resize (e.g., cleared or redrawn).
