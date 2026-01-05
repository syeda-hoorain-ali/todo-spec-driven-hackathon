# Tasks: Docker Containerization for Todo Chatbot Application

## Phase 1: Repository Preparation
- [X] T001 Create project structure for phase-04 by copying phase-03, excluding node_modules and .venv directories

## Phase 2: Python Environment Setup
- [X] T002 Set up MCP server virtual environment using uv in phase-04/mcp_server/
- [X] T003 Install MCP server dependencies using uv sync in phase-04/mcp_server/
- [X] T004 Set up backend virtual environment using uv in phase-04/backend/
- [X] T005 Install backend dependencies using uv sync in phase-04/backend/
- [X] T006 Install frontend dependencies using npm/yarn in phase-04/frontend/
- [X] T007 Stop and run /sp.git.commit_pr command - Just push on github, do NOT create pull request

## Phase 3: Foundational Tasks
- [X] T008 Verify Docker installation and check version
- [X] T009 Enable Docker AI Agent (Gordon) in Docker Desktop settings
- [X] T010 Prepare development environment for containerization

## Phase 4: User Story 1 - Complete MCP Server Containerization (Priority: P1)
- [X] T011 [P] [US1] Create Dockerfile for MCP server using Docker AI Agent in phase-04/mcp_server/
- [X] T012 [P] [US1] Add .dockerignore for MCP server in phase-04/mcp_server/
- [X] T013 [P] [US1] Build MCP server Docker image with tag todo-mcp-server:latest
- [X] T014 [P] [US1] Configure environment variables for MCP server container
- [X] T015 [US1] Test MCP server container accessibility on port 8080
- [X] T016 [US1] Verify MCP server container functionality and document any issues
- [X] T017 [P] [US1] Verify Docker AI Agent generates optimized MCP server Dockerfile following security best practices
- [X] T018 [P] [US1] Use Docker AI Agent to rate and optimize existing MCP server Dockerfile
- [X] T019 [US1] Verify suggestions from Docker AI Agent are implemented in MCP server Dockerfile
- [X] T020 [P] [US1] Verify MCP server Dockerfile implements multi-stage build (dependencies, build, production)
- [X] T021 [US1] Verify MCP server image is smaller than single-stage build and only contains necessary runtime dependencies

## Phase 5: User Story 2 - Complete Backend Containerization (Priority: P1)
- [X] T022 [P] [US2] Create Dockerfile for backend using Docker AI Agent in phase-04/backend/
- [X] T023 [P] [US2] Add .dockerignore for backend in phase-04/backend/
- [X] T024 [P] [US2] Build backend Docker image with tag todo-backend:latest
- [X] T025 [P] [US2] Configure environment variables for backend container
- [X] T026 [US2] Test backend container accessibility on port 8000
- [X] T027 [US2] Verify backend container functionality and document any issues learned from MCP server containerization
- [X] T028 [P] [US2] Verify Docker AI Agent generates optimized backend Dockerfile following security best practices
- [X] T029 [P] [US2] Use Docker AI Agent to rate and optimize existing backend Dockerfile
- [X] T030 [US2] Verify suggestions from Docker AI Agent are implemented in backend Dockerfile
- [X] T031 [P] [US2] Verify backend Dockerfile implements multi-stage build (dependencies, build, production)
- [X] T032 [US2] Verify backend image is smaller than single-stage build and only contains necessary runtime dependencies

## Phase 6: User Story 3 - Complete Frontend Containerization (Priority: P1)
- [X] T033 [P] [US3] Create Dockerfile for frontend using Docker AI Agent in phase-04/frontend/
- [X] T034 [P] [US3] Add .dockerignore for frontend in phase-04/frontend/
- [X] T035 [P] [US3] Build frontend Docker image with tag todo-frontend:latest
- [X] T036 [P] [US3] Configure environment variables for frontend container
- [X] T037 [US3] Test frontend container accessibility on port 3000
- [X] T038 [US3] Verify frontend container functionality and document any issues learned from backend containerization
- [X] T039 [P] [US3] Verify Docker AI Agent generates optimized frontend Dockerfile following security best practices
- [X] T040 [P] [US3] Use Docker AI Agent to rate and optimize existing frontend Dockerfile
- [X] T041 [US3] Verify suggestions from Docker AI Agent are implemented in frontend Dockerfile
- [X] T042 [P] [US3] Verify frontend Dockerfile implements multi-stage build (dependencies, build, production)
- [X] T043 [US3] Verify frontend image is smaller than single-stage build and only contains necessary runtime dependencies

## Phase 7: Cross-cutting Concerns
- [X] T044 [P] Configure environment variables for all containers (FR-006)
- [X] T045 [P] Ensure all containers use non-root users (FR-007)
- [X] T046 [P] Implement Docker Hardened Images (DHI) where available (FR-008)
- [X] T047 [P] Create Docker Compose configuration for local development (FR-009)
- [X] T048 [P] Ensure containers expose correct ports (frontend: 3000, backend: 8000, MCP server: 8080) (FR-010)
- [X] T049 [P] Use specific, pinned base image versions (node:24.11.1-alpine, python:3.12-slim) (FR-011)
- [X] T050 [P] Implement health checks (liveness and readiness probes) for all containers (FR-012)
- [X] T051 [P] Support environment-specific configurations for dev, staging, and production (FR-013)
- [X] T052 [P] Optimize final production images to under 200MB for frontend and 150MB for backend
- [X] T053 Verify all containers run with non-root users as verified by container inspection
- [X] T054 Verify applications maintain full functionality when running in containers as compared to local development

## Dependencies
- User Story 1 (P1) has no dependencies and can be executed first
- User Story 2 (P2) depends on User Story 1 being completed
- User Story 3 (P3) depends on User Story 2 being completed

## Parallel Execution Examples
- None - Each user story must be completed fully before moving to the next (MCP server, then backend, then frontend)

## Implementation Strategy
- MVP scope: Complete User Story 1 (complete MCP server containerization) to have a working containerized application
- Incremental delivery: Each user story builds upon the previous to deliver increasing value
