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

## Running with Docker

You can run the MCP server and its required PostgreSQL database using Docker Compose. This setup uses Python 3.12 and installs all dependencies in a virtual environment using `uv` for reproducible builds.

### Requirements

- Docker and Docker Compose installed on your system
- (Optional) A `.env` file with the required environment variables (see `.env.example`)

### Environment Variables

The following environment variables are required for the MCP server to run (set in your `.env` file or directly in the compose file):

- `DATABASE_URL`: PostgreSQL connection string (the default database is provided by the `postgres-db` service)
- `JWT_SECRET_KEY`: Secret key for JWT authentication
- `JWT_ALGORITHM`: Algorithm for JWT (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes

The `postgres-db` service uses:
- `POSTGRES_DB`: Database name (default: `mcp`)
- `POSTGRES_USER`: Database user (default: `mcpuser`)
- `POSTGRES_PASSWORD`: Database password (default: `mcppassword`)

### Build and Run

1. (Optional) Copy `.env.example` to `.env` and fill in your secrets and configuration.
2. Build and start the services:

   ```sh
   docker compose up --build
   ```

   This will start both the MCP server and a PostgreSQL database.

### Ports

- MCP server HTTP API: [localhost:8080](http://localhost:8080)
- PostgreSQL: localhost:5432 (for direct DB access if needed)

### Notes

- The MCP server depends on the `postgres-db` service and will wait for it to be ready.
- Persistent database storage is configured via a Docker volume (`postgres_data`).
- The MCP server runs as a non-root user for improved security.
- If you need to customize the database connection, update the `DATABASE_URL` in your `.env` file accordingly.
