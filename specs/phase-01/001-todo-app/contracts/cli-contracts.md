# CLI Contracts: 001-todo-app

## Command Structure

The application will be invoked as `todo` with various subcommands.

## Command Definitions

### `todo add`
**Description**: Add a new task to the todo list

**Arguments**:
- `title` (required): Task title (string, max 200 chars)
- `description` (optional): Task description (string, max 1000 chars)

**Options**:
- `--priority` (optional): Task priority (values: "low", "medium", "high", default: "medium")
- `--due-date` (optional): Due date in YYYY-MM-DD format
- `--tags` (optional): Comma-separated list of tags (max 10 tags, each max 50 chars)

**Exit Codes**:
- 0: Task added successfully
- 1: Invalid arguments or validation error
- 2: System error

**Examples**:
```bash
todo add "Buy groceries"
todo add "Complete project" --priority high --due-date 2025-12-15
todo add "Team meeting" --priority medium --tags work,meeting
```

**Output**:
```
Task #123 added successfully:
- Title: Buy groceries
- Status: pending
- Priority: medium
- Created: 2025-12-08
```

### `todo list`
**Description**: List all tasks in the todo list

**Options**:
- `--status` (optional): Filter by status (values: "pending", "in-progress", "complete")
- `--priority` (optional): Filter by priority (values: "low", "medium", "high")
- `--sort` (optional): Sort by criteria (values: "date", "priority", "title", default: "date")
- `--all` (optional): Show all tasks (including completed)

**Exit Codes**:
- 0: Tasks listed successfully
- 2: System error

**Examples**:
```bash
todo list
todo list --status pending
todo list --priority high --sort priority
```

**Output**:
```
TODO LIST
┌─────┬──────────────────┬────────┬──────────────┬─────────┐
│ ID  │ Title            │ Status │ Priority     │ Due     │
├─────┼──────────────────┼────────┼──────────────┼─────────┤
│ 1   │ Buy groceries    │ ✓      │ medium       │ -       │
│ 123 │ Complete project │ ◯      │ high         │ 12/15   │
└─────┴──────────────────┴────────┴──────────────┴─────────┘
```

### `todo complete`
**Description**: Mark a task as complete

**Arguments**:
- `task_id` (required): ID of the task to mark complete (integer)

**Exit Codes**:
- 0: Task marked complete successfully
- 1: Invalid task ID or task not found
- 2: System error

**Examples**:
```bash
todo complete 123
```

**Output**:
```
Task #123 marked as complete
```

### `todo delete`
**Description**: Delete a task from the list

**Arguments**:
- `task_id` (required): ID of the task to delete (integer)

**Exit Codes**:
- 0: Task deleted successfully
- 1: Invalid task ID or task not found
- 2: System error

**Examples**:
```bash
todo delete 123
```

**Output**:
```
Task #123 deleted successfully
```

### `todo update`
**Description**: Update properties of an existing task

**Arguments**:
- `task_id` (required): ID of the task to update (integer)
- `title` (optional): New task title (string, max 200 chars)
- `description` (optional): New task description (string, max 1000 chars)

**Options**:
- `--priority` (optional): New priority (values: "low", "medium", "high")
- `--due-date` (optional): New due date in YYYY-MM-DD format
- `--status` (optional): New status (values: "pending", "in-progress", "complete")

**Exit Codes**:
- 0: Task updated successfully
- 1: Invalid arguments, task ID, or validation error
- 2: System error

**Examples**:
```bash
todo update 123 "Updated title"
todo update 123 --priority high --due-date 2025-12-20
```

**Output**:
```
Task #123 updated successfully:
- Title: Updated title
- Priority: high
- Due: 2025-12-20
```

### `todo search`
**Description**: Search tasks by keyword in title or description

**Arguments**:
- `keyword` (required): Search keyword (string)

**Options**:
- `--case-sensitive` (optional): Perform case-sensitive search (default: case-insensitive)

**Exit Codes**:
- 0: Search completed successfully
- 2: System error

**Examples**:
```bash
todo search groceries
todo search "project" --case-sensitive
```

**Output**:
```
SEARCH RESULTS FOR "groceries"
┌─────┬──────────────────┬────────┬──────────────┬─────────┐
│ ID  │ Title            │ Status │ Priority     │ Due     │
├─────┼──────────────────┼────────┼──────────────┼─────────┤
│ 1   │ Buy groceries    │ ✓      │ medium       │ -       │
│ 45  │ Weekly groceries │ ◯      │ low          │ -       │
└─────┴──────────────────┴────────┴──────────────┴─────────┘
```

### `todo help`
**Description**: Display help information for all commands

**Arguments**: None

**Exit Codes**:
- 0: Help displayed successfully

**Examples**:
```bash
todo help
todo help add
```

**Output**:
```
TODO APP - Command Line Interface

Usage: todo <command> [options]

Commands:
  add       Add a new task
  list      List all tasks
  complete  Mark a task as complete
  delete    Delete a task
  update    Update a task
  search    Search tasks by keyword
  help      Show this help message

Examples:
  todo add "Buy groceries"
  todo list --status pending
  todo complete 1
```

## Error Handling Contracts

### Validation Errors
- **Invalid title**: "Error: Title cannot exceed 200 characters"
- **Invalid description**: "Error: Description cannot exceed 1000 characters"
- **Invalid status**: "Error: Status must be one of: pending, in-progress, complete"
- **Invalid priority**: "Error: Priority must be one of: low, medium, high"
- **Invalid task ID**: "Error: Task with ID <id> not found"
- **Invalid date format**: "Error: Date format must be YYYY-MM-DD"

### System Errors
- **General error**: "Error: An unexpected error occurred. Please try again."
- **File error**: "Error: Unable to access task data."

## Exit Codes Standard
- 0: Success
- 1: User error (validation, invalid input, etc.)
- 2: System error (file access, unexpected exception, etc.)
- 3: Configuration error
- 4: Permission error