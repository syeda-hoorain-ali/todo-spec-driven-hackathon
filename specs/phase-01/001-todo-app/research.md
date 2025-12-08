# Research Document: 001-todo-app

## Decision: Python Console Application Architecture
**Rationale**: For a simple in-memory todo console application, we'll use a layered architecture with clear separation between CLI parsing, business logic, and data management. This follows Python best practices for console applications.

**Alternatives considered**:
- Simple procedural script (rejected - not maintainable)
- Full MVC framework (rejected - overkill for simple console app)
- Layered architecture (selected - good separation of concerns)

## Decision: Rich Library for Terminal UI
**Rationale**: Rich provides excellent formatting capabilities for console applications and is the current best practice for Python terminal UIs. It allows for tables, colors, and rich formatting that will make the todo list more user-friendly.

**Alternatives considered**:
- Plain print statements (rejected - no visual distinction)
- Colorama for colors (rejected - limited features)
- Rich library (selected - comprehensive terminal formatting)

## Decision: Argparse for Command Parsing
**Rationale**: Argparse is Python's standard library solution for command-line parsing and is well-suited for this application. It provides help text generation and proper argument validation.

**Alternatives considered**:
- sys.argv manual parsing (rejected - error-prone)
- Click library (rejected - adds dependency, not needed for simple commands)
- Argparse (selected - standard library, sufficient features)

## Decision: uv Package Management
**Rationale**: Per the constitution, we must use uv as the exclusive package manager for Python dependencies. This requires creating a pyproject.toml file with proper dependencies.

**Resolution**: Yes, uv is required for this Python console application per the constitution.

## Decision: pytest for Testing Framework
**Rationale**: pytest is the standard testing framework for Python and integrates well with TDD practices. It's more feature-rich than unittest and has better syntax.

**Alternatives considered**:
- unittest (rejected - more verbose syntax)
- pytest (selected - industry standard, great for TDD)
- nose (rejected - deprecated)

## Decision: Project Structure
**Rationale**: Following Python packaging best practices with a proper package structure that includes a main module and separate modules for different concerns.

```
src/phase-01/todo_app/
├── __init__.py
├── main.py
├── models/
│   ├── __init__.py
│   └── task.py
├── managers/
│   ├── __init__.py
│   └── task_manager.py
├── cli/
│   ├── __init__.py
│   └── cli_interface.py
└── ui/
    ├── __init__.py
    └── renderer.py
```

## Decision: In-Memory Data Storage Pattern
**Rationale**: For an in-memory application, we'll use a simple Python list/dict structure managed by the TaskManager class. This meets the specification requirements without unnecessary complexity.

**Implementation**: Use a dictionary with task IDs as keys for O(1) lookup, with auto-incrementing ID generation.