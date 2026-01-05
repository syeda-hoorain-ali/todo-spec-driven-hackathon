---
id: "0010"
title: "Backend-MCP Server Connection Fix in Docker"
stage: "tasks"
date: "2026-01-04"
surface: "agent"
model: "qwen3-code-plus"
feature: "docker-containerization"
branch: "phase-04/001-docker-containerization"
user: "developer"
command: "fix backend-mcp connection in docker"
labels:
  - "docker"
  - "containerization"
  - "mcp-server"
  - "backend"
  - "networking"
files:
  - "phase-04/compose.yaml"
  - "phase-04/backend/.env"
  - "phase-04/backend/src/config/settings.py"
tests: []
links:
  SPEC: null
  TICKET: null
  ADR: null
  PR: null
---

# Backend-MCP Server Connection Fix in Docker

## Summary

Fixed the backend service startup failure in Docker containers by correcting the MCP server URL configuration. The backend was failing to connect to the MCP server during initialization because it was using `localhost` instead of the service name in the Docker network.

## Analysis

### Problem
- Backend container was failing to start with connection timeout errors to MCP server
- Error occurred during application startup when trying to connect to MCP server
- Root cause: Backend was configured to connect to `http://localhost:8080` instead of using the Docker service name

### Solution
- Added `MCP_SERVER_URL="http://mcp-server:8080"` to the backend's .env file
- This allows the backend container to properly connect to the MCP server container using the service name in the Docker network

## Implementation

### Changes Made

1. **Backend Environment Configuration**:
   - Updated `phase-04/backend/.env` to include `MCP_SERVER_URL="http://mcp-server:8080"`

2. **Docker Compose Configuration**:
   - Verified that `compose.yaml` has proper service dependencies (`backend` waits for `mcp-server` to be healthy)
   - Confirmed all services are on the same network for proper communication

### Verification
- All services now start successfully: MCP server, backend, and frontend
- Backend logs show "Application startup complete" without connection errors
- MCP server logs show successful connections from the backend container
- Docker containers show healthy status

## Outcome

The containerized Todo Chatbot application now runs successfully with all services communicating properly. The backend connects to the MCP server during startup without errors, resolving the initialization failure that was occurring previously.

## Evaluation

The fix successfully resolved the Docker containerization issue by addressing the network configuration problem between services. The application is now properly containerized with all services running and communicating correctly in the Docker environment.