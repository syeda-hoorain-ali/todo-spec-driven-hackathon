# MCP Server for Todo App

This is an MCP (Model Context Protocol) server that enables AI agents to interact with task management functionality through standardized tools. The server authenticates AI agents using JWT tokens, ensures user isolation, and provides operations for creating, reading, updating, deleting, and completing tasks stored in a Neon PostgreSQL database.

## Features

- **Task Management**: Create, read, update, delete, and complete tasks
- **Authentication**: JWT token-based authentication for AI agents
- **User Isolation**: Ensures users can only access their own tasks
- **Advanced Features**: Support for priorities, categories, due dates, recurring tasks, and search/filtering
- **Database**: Neon PostgreSQL for reliable data storage

## Tools Available

- `add_task`: Create a new task
- `list_tasks`: Retrieve tasks with filtering options
- `complete_task`: Mark a task as complete
- `delete_task`: Remove a task
- `update_task`: Modify task details

## Getting Started

1. Install dependencies: `uv sync`
2. Set up environment variables (see `.env.example`)
3. Run the server: `uv run -m --with mcp src.mcp_server.main`
4. Run the server in stdio: `uv run -m --with mcp src.mcp_server.main --stdio`

## Environment Variables

- `DATABASE_URL`: Connection string for Neon PostgreSQL database
- `JWT_SECRET_KEY`: Secret key for JWT token verification
- `JWT_ALGORITHM`: Algorithm used for JWT token encoding (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes

## Architecture

The server follows clean architecture principles with separation of concerns:

- **Main**: Entry point and server configuration
- **Auth**: JWT authentication utilities
- **Database**: Neon DB connection and session management
- **Models**: Task data models using SQLModel
- **Tools**: MCP tools implementation
- **Config**: Server configuration

## MCP Protocol

This server implements the Model Context Protocol to allow AI agents to interact with the task management system in a standardized way.
