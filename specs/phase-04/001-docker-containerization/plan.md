# Implementation Plan: Docker Containerization for Todo Chatbot Application

**Branch**: `phase-04/001-docker-containerization` | **Date**: 2026-01-01 | **Spec**: [spec.md](/specs/phase-04/001-docker-containerization/spec.md)
**Input**: Feature specification from `/specs/phase-04/001-docker-containerization/spec.md`
**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Docker containerization of the Todo Chatbot application (frontend, backend, and MCP server components) with AI-assisted Dockerfile creation using Docker AI Agent (Gordon). The approach involves setting up proper Python virtual environments using uv, creating optimized multi-stage Docker builds, and deploying with Kubernetes.

## Technical Context

**Language/Version**: Python 3.12, Node.js 24.11.1
**Primary Dependencies**: Docker, Docker AI Agent (Gordon), uv, FastAPI, Next.js, Python MCP Server
**Storage**: N/A (containerized application)
**Testing**: Docker container validation, inter-service communication tests
**Target Platform**: Linux containers for Kubernetes deployment
**Project Type**: Web application (frontend/backend/MCP server)
**Performance Goals**: Docker images under 200MB frontend, 150MB backend; containers start within 30 seconds
**Constraints**: All containers must run with non-root users for security; use specific pinned base image versions
**Scale/Scope**: Single application with three containerized services for local development and production deployment

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

All components must follow security best practices by running as non-root users and using pinned base image versions. Container images must be optimized for size and security.

## Project Structure

### Documentation (this feature)
```text
specs/phase-04/001-docker-containerization/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)
```text
phase-04/
├── frontend/
│   ├── Dockerfile
│   ├── .dockerignore
│   └── package.json
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── pyproject.toml
│   └── .venv/
├── mcp_server/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── pyproject.toml
│   └── .venv/
└── docker-compose.yml
```

**Structure Decision**: Web application with three services (frontend Next.js, backend FastAPI, MCP server Python) with separate virtual environments managed by uv in backend and MCP server directories.

## Phase 0: Outline & Research

### MCP Server Environment Setup
- Decision: Use uv for Python environment management in MCP server
- Rationale: Consistency with overall Python dependency management approach using uv
- Alternatives considered: Standard venv/pip vs uv (selected uv for faster dependency resolution)

### Backend Environment Setup
- Decision: Use uv for Python environment management in backend
- Rationale: Consistency across Python services and improved performance
- Alternatives considered: Standard venv/pip vs uv (selected uv for faster dependency resolution)

### Frontend Dependencies
- Decision: Use standard npm for frontend dependency management
- Rationale: Next.js standard practice and compatibility
- Alternatives considered: yarn/pnpm vs npm (selected npm for simplicity)

## Phase 1: Design & Contracts

### Python Environment Setup Commands

For both MCP server and backend directories:

1. **Create virtual environment:**
   ```bash
   uv venv
   ```

2. **Activate virtual environment:**
   ```bash
   # On Linux/macOS:
   source .venv/bin/activate
   # On Windows:
   source .venv/Scripts/activate
   ```

3. **Install dependencies:**
   ```bash
   uv sync
   ```

For backend specifically:
1. **Navigate to backend directory:** `cd phase-04/backend`
2. **Create virtual environment:** `uv venv`
3. **Activate it:** `source .venv/Scripts/activate`
3. **Install backend dependencies from pyproject.toml:** `uv sync`

For MCP server specifically:
1. **Navigate to MCP server directory:** `cd phase-04/mcp_server`
2. **Create virtual environment:** `uv venv`
3. **Activate it:** `source .venv/Scripts/activate`
3. **Install MCP server dependencies from pyproject.toml:** `uv sync`

For frontend specifically:
1. **Navigate to frontend directory:** `cd phase-04/frontend`
2. **Install frontend dependencies from package.json:** `npm install`
3. **Verify installation and check for any issues:** `npm audit`
4. **Build the frontend application (optional, for verification):** `npm run build`

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Multiple Python services with separate virtual environments | Security isolation and dependency management | Sharing a single environment could cause conflicts |
