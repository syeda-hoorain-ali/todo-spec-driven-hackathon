# Taskflow Application - Docker Containerization

This project contains a complete Taskflow application with three main components:
- **Frontend**: Next.js application
- **Backend**: FastAPI server
- **MCP Server**: Python MCP server

All components are containerized using Docker and can be run together using Docker Compose.

## Prerequisites

- Docker Desktop (with Docker Compose)
- At least 4GB of RAM for smooth operation

## Quick Start

1. Clone the repository
2. Navigate to this directory: `cd phase-04`
3. Copy the example environment files and customize them:

```bash
# Copy example files for each service
cp frontend/.env.example frontend/.env
cp backend/.env.example backend/.env
cp mcp_server/.env.example mcp_server/.env
```

4. Edit the `.env` files with your actual configuration values
5. Start all services:

```bash
docker-compose -f compose.yaml up --build
```

The applications will be available at:
- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs
- MCP Server: http://localhost:8080

## Environment Configuration

Each service has an `.env.example` file that shows the required environment variables. Copy these to `.env` and fill in your values:

- `frontend/.env` - Frontend configuration
- `backend/.env` - Backend API configuration
- `mcp_server/.env` - MCP server configuration

## Docker Compose

The main compose file (`compose.yaml`) includes:
- Frontend service (Next.js) on port 3000
- Backend service (FastAPI) on port 8000
- MCP server on port 8080
- PostgreSQL database on port 5432
- Health checks for all services
- Proper service dependencies

## Docker Images

All services use optimized multi-stage Docker builds:
- Frontend: node:24.11.1-alpine
- Backend: python:3.12.6-alpine
- MCP Server: python:3.12.6-alpine

All containers run as non-root users for security.

## Image Optimization

Dockerfiles are optimized to:
- Use multi-stage builds to separate build and runtime dependencies
- Remove build tools from final images to reduce size
- Use minimal base images (Alpine Linux)
- Implement proper health checks
- Run as non-root users
