# API Contract: Task Management Service

## Overview
This document defines the API contract between the frontend task management components and the backend secured todo API.

## Base URL
```
http://localhost:8000/api/{user_id}/
```
*Note: Replace with appropriate environment-specific URL in production*

## Authentication
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer {jwt_token}
```

## Endpoints

### GET /tasks
Retrieve all tasks for the authenticated user with optional filtering.

#### Query Parameters
- `skip` (integer, optional): Number of tasks to skip for pagination (default: 0)
- `limit` (integer, optional): Maximum number of tasks to return (default: 100, max: 100)
- `keyword` (string, optional): Search keyword to filter tasks by title or description
- `completed` (boolean, optional): Filter tasks by completion status (true for completed, false for pending)
- `date_from` (datetime, optional): Filter tasks created after this date (ISO 8601 format)
- `date_to` (datetime, optional): Filter tasks created before this date (ISO 8601 format)

#### Response
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Task title",
      "description": "Task description",
      "completed": false,
      "user_id": 1,
      "created_at": "2023-12-01T10:00:00Z",
      "updated_at": "2023-12-01T10:00:00Z",
      "due_date": "2023-12-31T10:00:00Z",
      "reminder_time": "2023-12-30T10:00:00Z",
      "is_recurring": false,
      "recurrence_pattern": "daily",
      "recurrence_interval": 1,
      "next_occurrence": "2023-12-02T10:00:00Z",
      "end_date": "2024-12-31T10:00:00Z",
      "max_occurrences": 10
    }
  ],
  "count": 1
}
```

### POST /tasks
Create a new task for the authenticated user.

#### Request Body
```json
{
  "title": "Task title (required, max 255 chars)",
  "description": "Task description (optional, max 1000 chars)",
  "completed": false,
  "due_date": "2023-12-31T10:00:00Z (optional)",
  "reminder_time": "2023-12-30T10:00:00Z (optional)",
  "is_recurring": false,
  "recurrence_pattern": "daily|weekly|monthly|yearly (optional)",
  "recurrence_interval": 1,
  "next_occurrence": "2023-12-02T10:00:00Z (optional)",
  "end_date": "2024-12-31T10:00:00Z (optional)",
  "max_occurrences": 10
}
```

#### Response
```json
{
  "id": 1,
  "title": "Task title",
  "description": "Task description",
  "completed": false,
  "user_id": 1,
  "due_date": "2023-12-31T10:00:00Z",
  "reminder_time": "2023-12-30T10:00:00Z",
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z"
}
```

### GET /tasks/{id}
Get a specific task by ID for the authenticated user.

#### Response
```json
{
  "id": 1,
  "title": "Task title",
  "description": "Task description",
  "completed": false,
  "user_id": 1,
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z"
}
```

### PUT /tasks/{id}
Update an existing task for the authenticated user.

#### Request Body
```json
{
  "title": "Updated task title (optional)",
  "description": "Updated task description (optional)",
  "completed": false,
  "due_date": "2023-12-31T10:00:00Z (optional)",
  "reminder_time": "2023-12-30T10:00:00Z (optional)"
}
```

#### Response
```json
{
  "id": 1,
  "title": "Updated task title",
  "description": "Updated task description",
  "completed": false,
  "user_id": 1,
  "due_date": "2023-12-31T10:00:00Z",
  "reminder_time": "2023-12-30T10:00:00Z",
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T11:00:00Z"
}
```

### DELETE /tasks/{id}
Delete a specific task for the authenticated user.

#### Response
```json
{
  "message": "Task deleted successfully"
}
```

### PATCH /tasks/{id}/complete
Toggle the completion status of a task for the authenticated user.

#### Response
```json
{
  "id": 1,
  "title": "Task title",
  "description": "Task description",
  "completed": true,
  "user_id": 1,
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T11:00:00Z"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Error details"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Access forbidden"
}
```

### 404 Not Found
```json
{
  "detail": "Task not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```
