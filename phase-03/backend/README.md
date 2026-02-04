# Secured Todo API Backend with AI Chatbot

This is a secured REST API backend for a todo application built with FastAPI, Python, and SQLModel. The API integrates with Better Auth for frontend authentication by verifying JWT tokens using a shared secret, ensuring user isolation where each user can only access their own tasks.

The application also features an AI chatbot with MCP (Model Context Protocol) integration that allows users to manage their tasks through natural language conversations.

## API Endpoints

### Authentication
All endpoints require a valid JWT token in the Authorization header. The token should be provided as a Bearer token.

### Base URL
```
/api/{user_id}/
```

### Task Endpoints

#### GET /api/{user_id}/tasks
List all tasks for the authenticated user with optional search and filter capabilities.

**Query Parameters:**
- `skip` (integer, optional): Number of tasks to skip for pagination (default: 0)
- `limit` (integer, optional): Maximum number of tasks to return (default: 100, max: 100)
- `keyword` (string, optional): Search keyword to filter tasks by title or description
- `completed` (boolean, optional): Filter tasks by completion status (true for completed, false for pending)
- `date_from` (datetime, optional): Filter tasks created after this date (ISO 8601 format)
- `date_to` (datetime, optional): Filter tasks created before this date (ISO 8601 format)

**Response:**
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
      "updated_at": "2023-12-01T10:00:00Z"
    }
  ],
  "count": 1
}
```

#### POST /api/{user_id}/tasks
Create a new task for the authenticated user.

**Request Body:**
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

**Response:**
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

#### GET /api/{user_id}/tasks/{id}
Get a specific task by ID for the authenticated user.

**Response:**
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

#### PUT /api/{user_id}/tasks/{id}
Update an existing task for the authenticated user.

**Request Body:**
```json
{
  "title": "Updated task title (optional)",
  "description": "Updated task description (optional)",
  "completed": false,
  "due_date": "2023-12-31T10:00:00Z (optional)",
  "reminder_time": "2023-12-30T10:00:00Z (optional)"
}
```

**Response:**
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

#### DELETE /api/{user_id}/tasks/{id}
Delete a specific task for the authenticated user.

**Response:**
```json
{
  "message": "Task deleted successfully"
}
```

#### PATCH /api/{user_id}/tasks/{id}/complete
Toggle the completion status of a task for the authenticated user.

**Response:**
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

## Search and Filter Parameters

The GET /api/{user_id}/tasks endpoint supports the following search and filter parameters:

### Keyword Search
- **Parameter**: `keyword`
- **Type**: String
- **Description**: Searches for tasks where the keyword appears in either the title or description (case-insensitive)

### Status Filter
- **Parameter**: `completed`
- **Type**: Boolean
- **Description**: Filters tasks by completion status
  - `true`: Returns only completed tasks
  - `false`: Returns only pending tasks
  - Not specified: Returns both completed and pending tasks

### Date Range Filter
- **Parameter**: `date_from`
- **Type**: Datetime (ISO 8601 format)
- **Description**: Filters tasks created after the specified date

- **Parameter**: `date_to`
- **Type**: Datetime (ISO 8601 format)
- **Description**: Filters tasks created before the specified date

### Pagination
- **Parameter**: `skip`
- **Type**: Integer
- **Description**: Number of tasks to skip (for pagination)

- **Parameter**: `limit`
- **Type**: Integer
- **Description**: Maximum number of tasks to return (default: 100)

## Advanced Features

### Due Dates and Reminders
Tasks can include due dates and reminder times for better time management:

- **due_date**: The date and time when the task is due (ISO 8601 format)
- **reminder_time**: The date and time when a reminder should be sent (ISO 8601 format, must be before due_date)

### Recurring Tasks
Tasks can be configured to repeat automatically with various patterns:

- **is_recurring**: Boolean flag to indicate if the task repeats
- **recurrence_pattern**: One of `daily`, `weekly`, `monthly`, or `yearly`
- **recurrence_interval**: How often to repeat (e.g., every 2 weeks)
- **next_occurrence**: When the next occurrence is due
- **end_date**: When recurrence should stop
- **max_occurrences**: Maximum number of occurrences to create

## Authentication and Authorization

- All endpoints require a valid JWT token in the Authorization header
- The token user ID must match the user_id in the URL path
- Users can only access, modify, or delete their own tasks
- Unauthorized access attempts return HTTP 401 or 403 status codes

## Error Handling

- `400 Bad Request`: Invalid request data (e.g., empty title, title too long)
- `401 Unauthorized`: Invalid or missing JWT token
- `403 Forbidden`: Token user doesn't match URL user_id
- `404 Not Found`: Task not found
- `500 Internal Server Error`: Server-side error during processing

## Environment Variables

The application requires the following environment variables:

- `DATABASE_URL`: Database connection string
- `BETTER_AUTH_SECRET`: Secret key for JWT token verification
- `JWT_ALGORITHM`: Algorithm used for JWT tokens (default: HS256)

## AI Chatbot with MCP Integration

The application includes an AI chatbot that allows users to manage their tasks through natural language conversations. The chatbot uses MCP (Model Context Protocol) to connect to task management tools.

### Architecture

- **Main API Server**: Runs on port 8000, handles all regular API requests including the `/api/chat` endpoint
- **MCP Server**: Runs on port 8001, provides task management tools accessible via HTTP endpoints
- **Agent Integration**: The chatbot agent connects to the MCP server to perform task operations

### Chat Endpoints

#### POST /api/chat
Send a message to the AI chatbot and receive a response with task management capabilities.

**Request Body:**
```json
{
  "message": "Create a task to buy groceries",
  "conversation_id": 123,  // Optional - if not provided, creates new conversation
  "user_timezone": "UTC"   // Optional
}
```

**Response:**
```json
{
  "conversation_id": 123,
  "response": "I've created a task: 'buy groceries'",
  "tool_calls": [],  // List of MCP tool calls made
  "timestamp": "2025-12-21T10:00:00Z"
}
```

### MCP Server Endpoints

#### POST /mcp/call_tool
Internal endpoint used by the agent to call specific tools.

**Request Body:**
```json
{
  "method": "create_task",
  "params": {
    "user_id": "user_123",
    "title": "Task title",
    "description": "Task description"
  }
}
```

## Running the Application

The application requires running both the main API server and the MCP server:

```bash
# Install dependencies
uv install

# Method 1: Run both servers simultaneously
uv run python start_servers.py

# Method 2: Run main API server only (MCP server must be started separately)
uv run python start_servers.py --api-only

# Method 3: Run MCP server only
uv run python start_servers.py --mcp-only

# Method 4: Run using uvicorn directly (requires separate MCP server)
uv run uvicorn src.main:app --reload
```

## Running Tests

```bash
# Test the MCP server functionality
uv run python test_mcp_server.py

# Test the complete chatbot integration
uv run python test_comprehensive_chatbot.py

# Run all tests
uv run pytest

# Run unit tests
uv run pytest tests/unit/

# Run integration tests
uv run pytest tests/integration/
```
