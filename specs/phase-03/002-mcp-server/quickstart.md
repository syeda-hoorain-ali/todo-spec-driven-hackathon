# Quickstart Guide: MCP Server for Task Management

## Overview
This guide provides instructions for setting up and running the MCP (Model Context Protocol) server that enables AI agents to manage tasks via standardized tools.

## Prerequisites
- Python 3.11+
- uv package manager
- Access to Neon PostgreSQL database
- Better Auth JWKS configuration

## Setup

### 1. Clone and Navigate
```bash
cd phase-03/mcp_server
```

### 2. Install Dependencies
```bash
uv sync
```

### 3. Environment Configuration
Create a `.env` file with the following variables:
```env
NEON_DATABASE_URL=your_neon_database_url
BETTER_AUTH_SECRET=your_better_auth_secret
JWT_ALGORITHM=EdDSA
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Initialize JWKS File
Ensure you have a `jwks.json` file in the project root containing the public keys for JWT verification.

## Running the Server

### Development
```bash
uv run src/mcp_server/main.py
```

### Production
```bash
# Using uvicorn
uv run uvicorn src.mcp_server.main:app --host 0.0.0.0 --port 8000

# Or using the built-in run method
uv run src/mcp_server/main.py
```

The server will be available at `http://localhost:8000/mcp`

## MCP Tools Available

### add_task
Creates a new task with the provided details.

**Parameters**:
- `user_id`: ID of the user creating the task
- `title`: Title of the task (required)
- `description`: Description of the task (optional)
- `priority`: Priority level (low, medium, high)
- `category`: Category for the task (optional)
- `due_date`: Due date in ISO format (optional)
- `reminder_time`: Reminder time in ISO format (optional)
- `recurrence_pattern`: Recurrence pattern (daily, weekly, monthly, yearly)

### list_tasks
Retrieves tasks with filtering and sorting options.

**Parameters**:
- `user_id`: ID of the user whose tasks to retrieve (required)
- `status`: Filter by completion status (all, pending, completed)
- `priority`: Filter by priority level
- `category`: Filter by category
- `search`: Search keyword for title/description
- `sort_by`: Sort field (due_date, priority, title, created_at)
- `sort_order`: Sort direction (asc, desc)

### complete_task
Marks a task as complete.

**Parameters**:
- `user_id`: ID of the user (required)
- `task_id`: ID of the task to complete (required)

### delete_task
Removes a task.

**Parameters**:
- `user_id`: ID of the user (required)
- `task_id`: ID of the task to delete (required)

### update_task
Modifies task details.

**Parameters**:
- `user_id`: ID of the user (required)
- `task_id`: ID of the task to update (required)
- `title`: New title for the task (optional)
- `description`: New description for the task (optional)
- `priority`: New priority level (optional)
- `category`: New category for the task (optional)
- `due_date`: New due date in ISO format (optional)
- `reminder_time`: New reminder time in ISO format (optional)

## Authentication
The server uses JWT token verification to authenticate requests. Each tool call must include a valid JWT token in the request headers to ensure proper user isolation.

## Testing
Run the test suite to verify functionality:

```bash
# Unit tests
uv run pytest tests/unit/

# Integration tests
uv run pytest tests/integration/
```

## Docker Deployment
Build and run with Docker:

```bash
# Build the image
docker build -t mcp-task-server .

# Run the container
docker run -p 8000:8000 --env-file .env mcp-task-server
```
