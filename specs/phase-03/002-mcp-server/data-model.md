# Data Model for MCP Server Implementation

## Task Entity

**Description**: Represents a user's todo item with comprehensive attributes for task management.

**Fields**:
- `id` (int, primary key, auto-increment): Unique identifier for the task
- `user_id` (str): ID of the user who owns this task (for user isolation)
- `title` (str): Title of the task (required, min 1, max 255 characters)
- `description` (str, optional): Detailed description of the task (max 1000 characters)
- `completed` (bool): Whether the task is completed (default: False)
- `category` (str, optional): Category for the task (default: "other", max 50 characters)
- `priority` (str, optional): Priority level of the task (default: "medium", max 20 characters)
- `due_date` (datetime, optional): Date when the task is due
- `reminder_time` (datetime, optional): Time for task reminder notification
- `is_recurring` (bool): Whether the task is recurring (default: False)
- `recurrence_pattern` (str, optional): Pattern for recurring tasks (max 50 characters)
- `recurrence_interval` (int, optional): How often to repeat (e.g., every 2 weeks)
- `next_occurrence` (datetime, optional): When the next occurrence is due
- `recurrence_end_date` (datetime, optional): When recurrence ends
- `max_occurrences` (int, optional): Max number of occurrences
- `created_at` (datetime): Timestamp when the task was created (auto-generated)
- `updated_at` (datetime): Timestamp when the task was last updated (auto-generated)

**Validation Rules**:
- `title` is required and must be between 1-255 characters
- `user_id` is required and must match authenticated user
- `category` must be max 50 characters if provided
- `priority` must be max 20 characters if provided
- `due_date` must be in the future if provided
- `reminder_time` must be before due_date if both are provided
- `recurrence_pattern` must be max 50 characters if provided
- `recurrence_interval` must be a positive integer if provided
- `max_occurrences` must be a positive integer if provided

**State Transitions**:
- `completed` can transition from False to True (complete_task operation)
- `completed` can transition from True to False (uncomplete_task operation)
- All other fields can be modified via update_task operation

## User Entity

**Description**: Represents an authenticated user identified by user_id extracted from JWT token.

**Fields**:
- `user_id` (str): Unique identifier for the user (from JWT token)
- `email` (str, optional): User's email address (for reference only)
- `created_at` (datetime): Timestamp when user was first seen

**Validation Rules**:
- `user_id` is required and must be validated against JWT token
- User isolation: Only tasks belonging to the authenticated user_id can be accessed

## MCP Tool Request/Response Models

### AddTaskRequest
- `user_id` (str): ID of the user creating the task
- `title` (str): Title of the task (required, min 1, max 255 characters)
- `description` (str, optional): Description of the task (max 1000 characters)
- `completed` (bool, optional): Whether the task is completed (default: False)
- `category` (str, optional): Category for the task (max 50 characters, default: "other")
- `priority` (str, optional): Priority level (max 20 characters, default: "medium")
- `due_date` (str, optional): Due date in ISO format
- `reminder_time` (str, optional): Reminder time in ISO format
- `is_recurring` (bool, optional): Whether the task is recurring (default: False)
- `recurrence_pattern` (str, optional): Recurrence pattern (max 50 characters)
- `recurrence_interval` (int, optional): How often to repeat (e.g., every 2 weeks)
- `next_occurrence` (str, optional): When the next occurrence is due (ISO format)
- `recurrence_end_date` (str, optional): When recurrence ends (ISO format)
- `max_occurrences` (int, optional): Max number of occurrences

### ListTasksRequest
- `user_id` (str): ID of the user whose tasks to retrieve
- `status` (str, optional): Filter by completion status ("all", "pending", "completed")
- `priority` (str, optional): Filter by priority level
- `category` (str, optional): Filter by category
- `search` (str, optional): Search keyword for title/description
- `sort_by` (str, optional): Sort field ("due_date", "priority", "title", "created_at")
- `sort_order` (str, optional): Sort direction ("asc", "desc")

### TaskResponse
- `id` (int): Unique identifier for the task
- `user_id` (str): ID of the user who owns this task
- `title` (str): Title of the task
- `description` (str, optional): Description of the task
- `completed` (bool): Whether the task is completed
- `category` (str, optional): Category for the task
- `priority` (str, optional): Priority level of the task
- `due_date` (str, optional): Due date in ISO format
- `reminder_time` (str, optional): Reminder time in ISO format
- `is_recurring` (bool): Whether the task is recurring
- `recurrence_pattern` (str, optional): Recurrence pattern
- `recurrence_interval` (int, optional): How often to repeat
- `next_occurrence` (str, optional): When the next occurrence is due (ISO format)
- `recurrence_end_date` (str, optional): When recurrence ends (ISO format)
- `max_occurrences` (int, optional): Max number of occurrences
- `created_at` (str): Creation timestamp in ISO format
- `updated_at` (str): Last update timestamp in ISO format
