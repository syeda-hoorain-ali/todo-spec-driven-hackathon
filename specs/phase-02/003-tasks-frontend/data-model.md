# Data Model: Task Management Frontend

## Task Entity

**Definition**: Represents a user's to-do item with properties for tracking, scheduling, and recurrence.

**Fields**:
- `id`: number - Unique identifier for the task
- `title`: string (required, max 255 chars) - The main task description/title
- `description`: string (optional, max 1000 chars) - Detailed description of the task
- `completed`: boolean - Whether the task is completed or pending
- `user_id`: number - The ID of the user who owns this task
- `created_at`: string (ISO 8601 datetime) - When the task was created
- `updated_at`: string (ISO 8601 datetime) - When the task was last updated
- `due_date`: string (optional, ISO 8601 datetime) - When the task is due
- `reminder_time`: string (optional, ISO 8601 datetime) - When to send a reminder
- `is_recurring`: boolean - Whether this task repeats
- `recurrence_pattern`: 'daily' | 'weekly' | 'monthly' | 'yearly' (optional) - How often the task repeats
- `recurrence_interval`: number (optional) - Interval for recurrence (e.g., every 2 weeks)
- `next_occurrence`: string (optional, ISO 8601 datetime) - When the next occurrence is due
- `recurrence_end_date`: string (optional, ISO 8601 datetime) - When recurrence should stop
- `max_occurrences`: number (optional) - Maximum number of occurrences to create

**Validation Rules**:
- `title` is required and must be between 1-255 characters
- `description` can be up to 1000 characters if provided
- `reminder_time` must be before `due_date` if both are provided
- `recurrence_interval` must be a positive integer if `is_recurring` is true
- `max_occurrences` must be a positive integer if provided

**State Transitions**:
- `pending` → `completed`: When user marks task as complete
- `completed` → `pending`: When user unmarks task as complete

## Task Form Data Structure

**For Task Creation**:
- `title`: string (required)
- `description`: string (optional)
- `completed`: boolean (default: false)
- `due_date`: string (optional, ISO 8601 datetime)
- `reminder_time`: string (optional, ISO 8601 datetime)
- `is_recurring`: boolean (default: false)
- `recurrence_pattern`: 'daily' | 'weekly' | 'monthly' | 'yearly' (optional)
- `recurrence_interval`: number (optional, default: 1)
- `recurrence_recurrence_end_date`: string (optional, ISO 8601 datetime)
- `max_occurrences`: number (optional)

**For Task Update**:
- `title`: string (optional)
- `description`: string (optional)
- `completed`: boolean (optional)
- `due_date`: string (optional)
- `reminder_time`: string (optional)

## Filter and Search Parameters

**Request Parameters**:
- `skip`: number (optional, default: 0) - Number of tasks to skip for pagination
- `limit`: number (optional, default: 100, max: 100) - Maximum number of tasks to return
- `keyword`: string (optional) - Search keyword to filter tasks by title or description
- `completed`: boolean (optional) - Filter tasks by completion status
- `date_from`: string (optional, ISO 8601 datetime) - Filter tasks created after this date
- `date_to`: string (optional, ISO 8601 datetime) - Filter tasks created before this date

**Response Structure**:
- `tasks`: Task[] - Array of task objects
- `count`: number - Total number of tasks matching the filter criteria

## API Response Types

**Task List Response**:
```typescript
{
  tasks: Task[];
  count: number;
}
```

**Single Task Response**:
```typescript
{
  message: string; // For delete operations
}
```

**Error Response**:
```typescript
{
  detail: string; // Error message from API
}
```
