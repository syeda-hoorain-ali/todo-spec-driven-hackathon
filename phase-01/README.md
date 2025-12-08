# Todo App

A Python console todo application with in-memory storage.

## Features

- Add, view, complete, delete, and update tasks
- Filter and sort tasks by various criteria
- Set priorities and tags for tasks
- Set due dates and recurrence patterns
- Rich terminal interface with color-coded output

## Requirements

- Python 3.8+
- uv (for package management)

## Installation

1. Install uv if you don't have it:
   ```bash
   pip install uv
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Run the application:
   ```bash
   uv run todo --help
   ```

## Usage Examples

### Adding Tasks
```bash
# Add a simple task
todo add "Buy groceries"

# Add a task with description
todo add "Buy groceries" "Milk, bread, eggs"

# Add a task with priority and tags
todo add "Complete project" --priority high --tags "work,urgent"

# Add a task with due date
todo add "Submit report" --due-date 2025-12-31 --priority high
```

### Listing Tasks
```bash
# List all pending and in-progress tasks
todo list

# List all tasks (including completed)
todo list --all

# List tasks filtered by status
todo list --status complete

# List tasks filtered by priority
todo list --priority high

# List tasks sorted by priority
todo list --sort priority

# List tasks sorted by title (reverse order)
todo list --sort title --reverse
```

### Managing Task Status
```bash
# Mark a task as complete
todo complete 1

# Mark a task as incomplete (pending)
todo incomplete 2
```

### Updating Tasks
```bash
# Update task title
todo update 1 "New title"

# Update task priority
todo update 1 --priority low

# Update multiple fields at once
todo update 1 "Updated title" "Updated description" --priority high --tags "important,work"
```

### Deleting Tasks
```bash
# Delete a task
todo delete 1
```

### Searching and Filtering
```bash
# Search tasks by keyword in title or description
todo search "groceries"

# Search with case sensitivity
todo search "GROCERIES" --case-sensitive
```

### Help
```bash
# Show help for all commands
todo --help

# Show help for a specific command
todo add --help
```

### Interactive Mode
```bash
# Start the interactive mode
todo interactive

# In interactive mode, you can run commands without the 'todo' prefix:
# - add "Task title"
# - list
# - complete 1
# - update 1 "New title"
# - delete 1
# - search "keyword"
# - help
# - exit (or quit)
```

## Exit Codes

- 0: Success
- 1: General error or task not found
- 2: Unexpected error
- 3: File not found error
- 4: Permission denied error
- 130: Operation cancelled by user (Ctrl+C)

## Development

To run tests:
```bash
uv run pytest
```

To run with development dependencies:
```bash
uv run --with pytest pytest tests/
```

To run tests for a specific user story:
```bash
uv run pytest tests/test_user_story_1.py
```
