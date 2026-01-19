# API Documentation: Secured Todo API

## Base URL
```
http://localhost:8000/api/{user_id}
```

## Authentication
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## Endpoints

### Create Task
**POST** `/api/{user_id}/tasks`

Creates a new task for the authenticated user.

#### Headers
- `Authorization: Bearer <jwt_token>`

#### Path Parameters
- `user_id` (string): The ID of the user creating the task. Must match the user ID in the JWT token.

#### Request Body
```json
{
  "title": "Task title (required, max 255 chars)",
  "description": "Task description (optional, max 1000 chars)",
  "completed": false,
  "due_date": "2025-12-31T10:00:00Z (optional, ISO 8601 format)",
  "reminder_time": "2025-12-30T10:00:00Z (optional, ISO 8601 format, must be before due_date)",
  "is_recurring": false,
  "recurrence_pattern": "daily|weekly|monthly|yearly (optional, required if is_recurring is true)",
  "recurrence_interval": 1,
  "next_occurrence": "2025-12-02T10:00:00Z (optional)",
  "end_date": "2026-12-31T10:00:00Z (optional)",
  "max_occurrences": 10
}
```

#### Response
- `200 OK`: Task created successfully
- `400 Bad Request`: Invalid input (missing title, title too long, etc.)
- `403 Forbidden`: User ID in token doesn't match URL user_id
- `500 Internal Server Error`: Server error during creation

### Get Tasks
**GET** `/api/{user_id}/tasks`

Retrieves all tasks for the authenticated user with optional search and filtering.

#### Headers
- `Authorization: Bearer <jwt_token>`

#### Path Parameters
- `user_id` (string): The ID of the user whose tasks to retrieve. Must match the user ID in the JWT token.

#### Query Parameters
- `skip` (integer, optional): Number of tasks to skip for pagination (default: 0)
- `limit` (integer, optional): Maximum number of tasks to return (default: 100, max: 100)
- `keyword` (string, optional): Search keyword to filter tasks by title or description
- `completed` (boolean, optional): Filter by completion status (true/false)
- `date_from` (datetime, optional): Filter tasks created after this date (ISO 8601 format)
- `date_to` (datetime, optional): Filter tasks created before this date (ISO 8601 format)

#### Response
- `200 OK`: Tasks retrieved successfully
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Task title",
      "description": "Task description",
      "completed": false,
      "user_id": "user123",
      "created_at": "2025-12-13T10:00:00Z",
      "updated_at": "2025-12-13T10:00:00Z"
    }
  ],
  "count": 1
}
```
- `403 Forbidden`: User ID in token doesn't match URL user_id
- `422 Unprocessable Entity`: Invalid query parameters

### Get Task by ID
**GET** `/api/{user_id}/tasks/{task_id}`

Retrieves a specific task for the authenticated user.

#### Headers
- `Authorization: Bearer <jwt_token>`

#### Path Parameters
- `user_id` (string): The ID of the user. Must match the user ID in the JWT token.
- `task_id` (integer): The ID of the task to retrieve.

#### Response
- `200 OK`: Task retrieved successfully
- `403 Forbidden`: User ID in token doesn't match URL user_id
- `404 Not Found`: Task not found or doesn't belong to the user
- `422 Unprocessable Entity`: Invalid task ID

### Update Task
**PUT** `/api/{user_id}/tasks/{task_id}`

Updates an existing task for the authenticated user.

#### Headers
- `Authorization: Bearer <jwt_token>`

#### Path Parameters
- `user_id` (string): The ID of the user. Must match the user ID in the JWT token.
- `task_id` (integer): The ID of the task to update.

#### Request Body
```json
{
  "title": "Updated task title (optional, max 255 chars)",
  "description": "Updated task description (optional, max 1000 chars)",
  "completed": false,
  "due_date": "2025-12-31T10:00:00Z (optional, ISO 8601 format)",
  "reminder_time": "2025-12-30T10:00:00Z (optional, ISO 8601 format, must be before due_date)"
}
```

#### Response
- `200 OK`: Task updated successfully
- `400 Bad Request`: Invalid input (title too long, etc.)
- `403 Forbidden`: User ID in token doesn't match URL user_id
- `404 Not Found`: Task not found or doesn't belong to the user
- `422 Unprocessable Entity`: Invalid task ID or request body

### Delete Task
**DELETE** `/api/{user_id}/tasks/{task_id}`

Deletes a task for the authenticated user.

#### Headers
- `Authorization: Bearer <jwt_token>`

#### Path Parameters
- `user_id` (string): The ID of the user. Must match the user ID in the JWT token.
- `task_id` (integer): The ID of the task to delete.

#### Response
- `200 OK`: Task deleted successfully
```json
{
  "message": "Task deleted successfully"
}
```
- `403 Forbidden`: User ID in token doesn't match URL user_id
- `404 Not Found`: Task not found or doesn't belong to the user
- `422 Unprocessable Entity`: Invalid task ID

### Toggle Task Completion
**PATCH** `/api/{user_id}/tasks/{task_id}/complete`

Toggles the completion status of a task for the authenticated user.

#### Headers
- `Authorization: Bearer <jwt_token>`

#### Path Parameters
- `user_id` (string): The ID of the user. Must match the user ID in the JWT token.
- `task_id` (integer): The ID of the task to toggle.

#### Response
- `200 OK`: Task completion status toggled successfully
- `403 Forbidden`: User ID in token doesn't match URL user_id
- `404 Not Found`: Task not found or doesn't belong to the user
- `422 Unprocessable Entity`: Invalid task ID

## Advanced Features

### Due Dates and Reminders
Tasks can include due dates and reminder times for better time management:

- `due_date`: The date and time when the task is due (ISO 8601 format)
- `reminder_time`: The date and time when a reminder should be sent (ISO 8601 format, must be before due_date)

When creating or updating a task, these fields can be included in the request body to set deadlines and notifications.

### Recurring Tasks
Tasks can be configured to repeat automatically with various patterns:

- `is_recurring`: Boolean flag to indicate if the task repeats
- `recurrence_pattern`: One of `daily`, `weekly`, `monthly`, or `yearly` (required if is_recurring is true)
- `recurrence_interval`: How often to repeat (e.g., every 2 weeks)
- `next_occurrence`: When the next occurrence is due
- `end_date`: When recurrence should stop
- `max_occurrences`: Maximum number of occurrences to create

## Search and Filter Parameters

### Keyword Search
- Parameter: `keyword`
- Type: string
- Description: Searches for the keyword in both task title and description (case-insensitive)

### Status Filter
- Parameter: `completed`
- Type: boolean
- Description: Filters tasks by completion status (true for completed tasks, false for incomplete tasks)

### Date Range Filter
- Parameters: `date_from` and `date_to`
- Type: datetime (ISO 8601 format)
- Description: Filters tasks created within the specified date range

### Pagination
- Parameters: `skip` and `limit`
- Type: integer
- Description: Enables pagination of results (skip = number of items to skip, limit = max items to return)

## Error Responses

All error responses follow the format:
```json
{
  "detail": "Error message"
}
```

### Common HTTP Status Codes
- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters or body
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Access forbidden (user ID mismatch)
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Invalid parameter values
- `500 Internal Server Error`: Server error