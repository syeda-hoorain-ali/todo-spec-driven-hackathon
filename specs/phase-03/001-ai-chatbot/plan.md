# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `phase-03/001-ai-chatbot` | **Date**: 2025-12-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/phase-03/001-ai-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of an AI-powered chatbot interface that allows users to manage their todo tasks through natural language conversations. The system builds upon the existing Phase-02 full-stack application by copying the structure, then adds an OpenAI ChatKit frontend component, Python-based AI agent with MCP server for task operations (using Neon HTTP MCP server as placeholder for now), and integrates with ChatKit stores connected to Neon DB for conversation persistence. The architecture enables conversational task management with context awareness and MCP-protocol tool execution, with future plans to implement custom MCP server.

## Technical Context

**Language/Version**: TypeScript 5.0+, Python 3.12, Next.js 16+ for frontend; Python 3.12, FastAPI, OpenAI Agents SDK for backend
**Primary Dependencies**: Next.js, React, OpenAI ChatKit, FastAPI, OpenAI Agents SDK, Official MCP SDK, SQLModel, Neon Postgres
**Storage**: Neon Serverless Postgres database with SQLModel ORM for tasks, conversations, and messages
**Testing**: pytest for backend, No Testing Library for frontend (as per project requirements)
**Target Platform**: Web application (Next.js frontend + FastAPI backend) with browser support
**Project Type**: Web application (frontend + backend with MCP server)
**Performance Goals**: Chat responses under 3 seconds, 95% accuracy in natural language understanding, 95% of multi-turn conversations handled correctly
**Constraints**: <200ms UI response time, conversation context preservation, secure JWT token handling, 30-second AI API timeouts
**Scale/Scope**: Individual user chatbot interactions, up to 100 requests per user per hour (rate-limited), conversation history storage

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Based on the project constitution, this AI chatbot implementation follows security-first principles with proper integration to the existing authentication system. The use of OpenAI ChatKit for the frontend, MCP server architecture for tool execution, and integration with the existing Phase-02 backend aligns with the established architecture patterns. The implementation maintains user isolation by validating JWT tokens and ensuring users can only access their own data.

## Project Structure

### Documentation (this feature)

```text
specs/phase-03/001-ai-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
phase-03/                          # Copied from phase-02
├── frontend/                      # Next.js frontend from Phase-02
│   ├── src/
│   │   ├── app/
│   │   │   ├── (dashboard)/             # Dashboard layout from Phase-02
│   │   │   │   ├── page.tsx             # Dashboard page with integrated chat
│   │   │   │   └── layout.tsx
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── chat/                     # New chat components using ChatKit React
│   │   │   │   └── chat-interface.tsx    # Main chat component using ChatKit React
│   │   │   └── ui/                       # Shared UI components from Phase-02
│   │   └── features/
│   │       └── chat/
│   │           ├── hooks.tsx             # Chat-specific hooks
│   │           ├── api.ts                # Chat API client
│   │           ├── queries.ts            # Chat-related API calls
│   │           └── types.ts              # Chat-related TypeScript types
│   ├── package.json
│   ├── next.config.ts
│   └── tsconfig.json
└── backend/                      # FastAPI backend from Phase-02
    ├── src/
    │   ├── main.py               # FastAPI app entry point from Phase-02
    │   ├── models/
    │   │   ├── conversation.py   # New conversation entity
    │   │   ├── message.py        # New message entity
    │   │   └── base.py           # Base model from Phase-02
    │   ├── services/
    │   │   ├── chat_service.py   # New chat business logic
    │   │   ├── task_service.py   # Task operations service from Phase-02
    │   │   └── auth_service.py   # Authentication service from Phase-02
    │   ├── api/
    │   │   └── routes/
    │   │       └── chat_routes.py    # New chat API endpoints with ChatKit integration
    │   ├── agents/
    │   │   ├── chat_agent.py     # New OpenAI Agent implementation
    │   │   └── task_tools.py     # New MCP task operation tools
    │   ├── services/
    │   │   ├── chat_service.py   # New chat business logic
    │   │   ├── chatkit_stores.py # ChatKit stores connecting to Neon DB
    │   │   └── chatkit_server.py # ChatKit server implementation
    │   └── config/
    │       ├── database.py       # Database configuration from Phase-02
    │       └── settings.py       # Application settings from Phase-02
    ├── requirements.txt
    └── tests/
```

**Structure Decision**: Copy entire Phase-02 structure to Phase-03 and extend with chatbot functionality. This maintains consistency with the existing architecture while adding the new AI chatbot capabilities. The MCP server components will be integrated into the backend to provide tools for the AI agent.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| MCP Server Integration | Required for AI agent to perform task operations | Direct API calls would not leverage MCP protocol as specified |
| Separate Chat API endpoints | Needed for chat-specific functionality distinct from existing todo API | Modifying existing API would create tight coupling |
