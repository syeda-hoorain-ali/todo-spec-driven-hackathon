# Implementation Tasks: AI-Powered Todo Chatbot

**Feature**: AI-Powered Todo Chatbot
**Spec**: [specs/phase-03/001-ai-chatbot/spec.md](./spec.md)
**Plan**: [specs/phase-03/001-ai-chatbot/plan.md](./plan.md)
**Date**: 2025-12-18

## Implementation Strategy

Build upon phase-02 by copying the entire structure to phase-03, then incrementally add chatbot functionality with ChatKit React component and MCP server integration. Implement in priority order of user stories with independent testability at each phase.

## Dependencies

- Complete phase-02 structure as foundation
- OpenAI API access and ChatKit React library
- MCP server setup for task operations

## Parallel Execution Examples

- Frontend chat interface development can proceed in parallel with backend agent development
- Database model creation can run in parallel with API endpoint development
- Authentication integration can happen independently of core chat functionality

---

## Phase 1: Project Setup

### Goal
Establish phase-03 project structure by copying phase-02 and setting up basic chatbot infrastructure.

### Independent Test Criteria
- Phase-03 directory structure exists and mirrors phase-02
- Basic project files are properly configured
- Dependencies are installed and accessible

### Tasks

- [X] T001 Copy phase-02 frontend directory to phase-03/frontend
- [X] T002 Copy phase-02 backend directory to phase-03/backend
- [X] T003 Update frontend package.json to reflect phase-03
- [X] T004 Update backend requirements.txt with AI/MCP dependencies
- [X] T005 Install ChatKit React library in frontend
- [X] T006 Install OpenAI and MCP SDK in backend
- [X] T007 Update README files to single heading as requested

---

## Phase 2: Foundational Components

### Goal
Implement foundational data models and services needed for all user stories.

### Independent Test Criteria
- Database models exist and are properly connected
- Basic authentication works with JWT tokens
- Conversation and message entities are functional

### Tasks

- [X] T008 [P] Create Conversation model in phase-03/backend/src/models/conversation.py
- [X] T009 [P] Create Message model in phase-03/backend/src/models/message.py
- [X] T010 [P] Update database configuration for new models in phase-03/backend/src/config/database.py
- [X] T011 [P] Create ChatService in phase-03/backend/src/services/chat_service.py
- [X] T012 [P] Create TaskTools for MCP in phase-03/backend/src/agents/task_tools.py
- [X] T013 [P] Create ChatAgent in phase-03/backend/src/agents/chat_agent.py
- [X] T014 [P] Create chat API routes in phase-03/backend/src/api/routes/chat_routes.py
- [X] T015 [P] Update authentication service to support chat endpoints in phase-03/backend/src/services/auth_service.py

---

## Phase 3: User Story 1 - Natural Language Task Management [P1]

### Goal
Enable users to manage todo tasks through natural language conversation with the AI chatbot.

### Independent Test Criteria
- User can engage with the chatbot using natural language commands like "Add a task to buy groceries"
- The task is created and confirmed by the chatbot
- Backend processes natural language and performs appropriate task operations

### Tasks

- [X] T016 [US1] Create chat interface component using ChatKit React in phase-03/frontend/src/components/chat/chat-interface.tsx
- [X] T017 [US1] Integrate chat component into dashboard page in phase-03/frontend/src/app/(dashboard)/dashboard/page.tsx
- [X] T018 [US1] Create chat API client in phase-03/frontend/src/features/chat/api.ts
- [X] T019 [US1] Create chat hooks for state management in phase-03/frontend/src/features/chat/hooks.tsx
- [X] T020 [US1] Create chat types definition in phase-03/frontend/src/features/chat/types.ts
- [X] T021 [US1] Create chat queries for API calls in phase-03/frontend/src/features/chat/queries.ts
- [X] T022 [US1] Implement chat endpoint in backend to handle natural language input in phase-03/backend/src/api/routes/chat_routes.py
- [X] T023 [US1] Connect chat endpoint to ChatAgent with task tools in phase-03/backend/src/agents/chat_agent.py
- [X] T024 [US1] Test natural language task creation functionality

---

## Phase 4: User Story 2 - Multi-turn Conversation Context [P1]

### Goal
Enable the chatbot to maintain context across multiple exchanges for natural, flowing conversations.

### Independent Test Criteria
- Chatbot remembers previous interactions in the same conversation
- User can reference previous tasks or actions without repeating context
- Conversation context persists during the session

### Tasks

- [X] T025 [US2] Implement conversation history storage in phase-03/backend/src/services/chat_service.py
- [X] T026 [US2] Update ChatAgent to maintain conversation context in phase-03/backend/src/agents/chat_agent.py
- [X] T027 [US2] Add conversation ID tracking in frontend chat component in phase-03/frontend/src/components/chat/chat-interface.tsx
- [X] T028 [US2] Implement message history loading in phase-03/frontend/src/features/chat/queries.ts
- [X] T029 [US2] Test multi-turn conversation functionality with context awareness

---

## Phase 5: User Story 3 - MCP-Enabled Task Operations [P2]

### Goal
Enable the chatbot to perform all basic task operations (create, read, update, delete) through natural language using MCP protocol (using Neon HTTP MCP server as placeholder for now).

### Independent Test Criteria
- All basic task operations (CRUD) work correctly through natural language commands
- MCP tools properly execute task operations via Neon HTTP server
- User can perform complex task management through conversation

### Tasks

- [X] T030 [US3] Implement MCP server integration using Neon HTTP server in phase-03/backend/src/agents/chat_agent.py
- [X] T031 [US3] Enhance task tools with full CRUD operations in phase-03/backend/src/agents/task_tools.py
- [X] T032 [US3] Test all task operations through natural language commands
- [X] T033 [US3] Implement error handling for MCP operations in phase-03/backend/src/agents/chat_agent.py
- [X] T034 [US3] Add validation for task operations in phase-03/backend/src/services/task_service.py

---

## Phase 6: ChatKit Integration [P1]

### Goal
Integrate ChatKit for conversation management and storage, connecting to Neon DB for persistence.

### Independent Test Criteria
- ChatKit stores successfully connect to Neon DB
- Conversation history persists between sessions
- Frontend successfully connects to ChatKit server
- ChatKit endpoints are accessible via FastAPI with authentication

### Tasks

- [X] T035 [P1] Create ChatKit stores implementation connecting to Neon DB in phase-03/backend/src/services/chatkit_stores.py
- [X] T036 [P1] Create ChatKit server implementation in phase-03/backend/src/services/chatkit_server.py
- [X] T037 [P1] Integrate ChatKit server with existing chat routes in phase-03/backend/src/api/routes/chat_routes.py
- [X] T038 [P1] Update frontend to connect to ChatKit server using React ChatKit in phase-03/frontend/src/components/chat/chat-interface.tsx
- [X] T039 [P1] Test ChatKit integration with Neon DB persistence
- [X] T040 [P1] Implement authentication for ChatKit endpoints in phase-03/backend/src/api/routes/chat_routes.py

## Phase 7: Cross-cutting Features & Polish

### Goal
Implement non-functional requirements and polish the user experience.

### Independent Test Criteria
- Rate limiting is properly enforced
- Authentication tokens are handled correctly
- Timeout and retry logic works as specified
- User data isolation is maintained

### Tasks

- [X] T041 Implement rate limiting for chat endpoints (max 100 requests per user per hour) in phase-03/backend/src/api/routes/chat_routes.py
- [X] T042 Add timeout handling for AI API calls with 30-second default in phase-03/backend/src/agents/chat_agent.py
- [X] T043 Implement retry logic for failed AI API calls with exponential backoff in phase-03/backend/src/agents/chat_agent.py
- [X] T044 Handle authentication token expiration with re-authentication prompt in phase-03/frontend/src/features/chat/queries.ts
- [X] T045 Add proper error messages for user-friendly responses in phase-03/backend/src/api/routes/chat_routes.py
- [X] T046 Add HTTP 429 responses when rate limits are exceeded in phase-03/backend/src/api/routes/chat_routes.py
- [X] T047 Implement proper user isolation in phase-03/backend/src/services/chat_service.py
- [X] T048 Add conversation context preservation during token refresh in phase-03/backend/src/services/chat_service.py
- [X] T049 Update final README files with complete documentation
- [X] T050 Test complete end-to-end functionality
