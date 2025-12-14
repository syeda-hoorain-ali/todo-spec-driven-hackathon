# Implementation Tasks: Secured Todo API

## Feature Overview
Implementation of secured REST API endpoints for a todo application using FastAPI backend with JWT token verification. The system will integrate with Better Auth from the frontend by verifying JWT tokens using the shared secret, ensuring user isolation where each user can only access their own tasks. The API will support all required CRUD operations for tasks with proper authentication and authorization checks. Additional features include search/filter, recurring tasks, and due dates with time reminders as specified in the requirements.

**Feature**: Secured Todo API
**Branch**: `002-secured-todo-api`
**Input**: `/specs/phase-02/002-secured-todo-api/spec.md`

## Implementation Strategy
Implement in priority order (P1, P2, etc.) with each user story as an independently testable increment. Start with core task functionality (User Story 1 & 2) as the MVP, then add update/delete/toggle functionality, and finally advanced features like search, filtering, recurring tasks, and due dates.

## Dependencies
- FastAPI must be properly configured before implementing API endpoints
- Database models must be created before implementing services
- JWT authentication middleware must be set up before securing endpoints
- SQLModel and database connection must be established before any data operations
- python-dotenv must be configured for environment variable management

## Parallel Execution Examples
- Database models can be developed in parallel with authentication setup
- Different API endpoints can be developed in parallel after foundational setup
- Unit tests can be written in parallel with implementation

---

## Phase 1: Project Setup

### Goal
Initialize project structure with required dependencies and configuration files.

### Tasks
- [x] T001 Initialize uv project in phase-02 directory with `uv init backend` command
- [x] T002 Create backend project directory structure per implementation plan: `mkdir -p backend/{src,tests}` and subdirectories
- [x] T003 [P] Install dependencies using uv package manager: `uv add fastapi[standard] uvicorn[standard] sqlmodel python-jose[cryptography] psycopg2-binary python-dotenv pytest`
- [x] T004 Create .env file with environment variable configuration for DATABASE_URL, BETTER_AUTH_SECRET, JWT_ALGORITHM
- [x] T005 Move backend/main.py entry point to backend/src/main.py with basic FastAPI app initialization

---

## Phase 2: Foundational Components

### Goal
Set up foundational components that are required by all user stories: database connection, JWT utilities, and configuration.

### Tasks
- [x] T006 Create database configuration module in backend/src/database/database.py with SQLModel engine and session setup
- [x] T007 [P] Create JWT utilities module in backend/src/auth/jwt.py with token verification functions
- [x] T008 [P] Create settings configuration module in backend/src/config/settings.py using python-dotenv
- [x] T009 [P] Create authentication middleware in backend/src/auth/middleware.py to verify JWT tokens
- [x] T010 Create base SQLModel in backend/src/models/base.py with common attributes
- [x] T011 [P] Create Task model in backend/src/models/task.py with all required fields and relationships per data model
- [x] T012 Create database initialization script to handle migrations and setup

---

## Phase 3: User Story 1 - Create Todo Tasks (Priority: P1)

### Goal
As an authenticated user, I want to create new todo tasks so that I can organize and track my work and responsibilities.

### Independent Test Criteria
Can be fully tested by creating a new task with a valid JWT token and verifying it appears in the user's task list, delivering the primary value of task creation and storage.

### Tasks
- [x] T013 [P] [US1] Create CreateTaskRequest schema in backend/src/schemas/task.py with title (required) and description (optional)
- [x] T014 [P] [US1] Create TaskResponse schema in backend/src/schemas/task.py with all required fields
- [x] T015 [US1] Create task service in backend/src/services/task_service.py with create_task method
- [x] T016 [P] [US1] Create POST /api/{user_id}/tasks endpoint in backend/src/api/routes/tasks.py
- [x] T017 [P] [US1] Implement JWT token verification in the create task endpoint to ensure user authentication
- [x] T018 [P] [US1] Add user_id validation to ensure token user matches URL user_id
- [x] T019 [US1] Implement proper error handling for unauthorized access (401) and forbidden access (403)
- [x] T020 [P] [US1] Add validation for task title and description according to data model requirements
- [x] T021 [US1] Test user story 1 end-to-end with valid JWT token and task creation

---

## Phase 4: User Story 2 - View Todo Tasks (Priority: P1)

### Goal
As an authenticated user, I want to view my todo tasks so that I can see what I need to do and track my progress.

### Independent Test Criteria
Can be fully tested by creating multiple tasks and then retrieving them via GET request, verifying users can see only their own tasks and not others'.

### Tasks
- [x] T022 [P] [US2] Create TaskListResponse schema in backend/src/schemas/task.py with tasks array and count
- [x] T023 [US2] Add get_tasks method to task service in backend/src/services/task_service.py
- [x] T024 [P] [US2] Create GET /api/{user_id}/tasks endpoint in backend/src/api/routes/tasks.py
- [x] T025 [P] [US2] Implement JWT token verification in the get tasks endpoint
- [x] T026 [P] [US2] Add user_id validation to ensure token user matches URL user_id
- [x] T027 [US2] Implement proper filtering to return only tasks belonging to authenticated user
- [x] T028 [P] [US2] Add proper error handling for unauthorized access (401) and forbidden access (403)
- [x] T029 [US2] Implement pagination support for task lists (optional enhancement)
- [x] T030 [P] [US2] Create GET /api/{user_id}/tasks/{id} endpoint for retrieving specific task
- [x] T031 [US2] Add proper error handling for task not found (404)
- [x] T032 [US2] Test user story 2 end-to-end with valid JWT token and task retrieval

---

## Phase 5: User Story 3 - Update and Manage Tasks (Priority: P2)

### Goal
As an authenticated user, I want to update, complete, and delete my todo tasks so that I can maintain an accurate and current task list.

### Independent Test Criteria
Can be fully tested by creating a task, updating its details, toggling its completion status, and deleting it, verifying all operations work only for the authenticated user's own tasks.

### Tasks
- [x] T033 [P] [US3] Create UpdateTaskRequest schema in backend/src/schemas/task.py with optional title and description
- [x] T034 [US3] Add update_task method to task service in backend/src/services/task_service.py
- [x] T035 [P] [US3] Add delete_task method to task service in backend/src/services/task_service.py
- [x] T036 [P] [US3] Add toggle_completion method to task service in backend/src/services/task_service.py
- [x] T037 [US3] Create PUT /api/{user_id}/tasks/{id} endpoint in backend/src/api/routes/tasks.py
- [x] T038 [P] [US3] Create DELETE /api/{user_id}/tasks/{id} endpoint in backend/src/api/routes/tasks.py
- [x] T039 [P] [US3] Create PATCH /api/{user_id}/tasks/{id}/complete endpoint in backend/src/api/routes/tasks.py
- [x] T040 [US3] Implement JWT token verification for all update/manage endpoints
- [x] T041 [P] [US3] Add user_id validation to ensure token user matches URL user_id for all operations
- [x] T042 [P] [US3] Implement proper error handling for unauthorized access (401), forbidden access (403), and task not found (404)
- [x] T043 [US3] Add proper validation for update operations
- [x] T044 [P] [US3] Test task update functionality end-to-end
- [x] T045 [P] [US3] Test task deletion functionality end-to-end
- [x] T046 [P] [US3] Test task completion toggle functionality end-to-end

---

## Phase 6: Advanced Features - Search & Filter

### Goal
Implement search and filtering capabilities to allow users to find tasks by keyword, status, priority, or date.

### Tasks
- [x] T047 [P] Create SearchFilterRequest schema in backend/src/schemas/task.py with search parameters
- [x] T048 Add search_tasks method to task service in backend/src/services/task_service.py with keyword search
- [x] T049 [P] Add filter_tasks method to task service with status, priority, and date filtering
- [x] T050 [P] Update GET /api/{user_id}/tasks endpoint to support search and filter parameters
- [x] T051 Create tests for search and filtering functionality
- [x] T052 Document search and filter API parameters

---

## Phase 7: Advanced Features - Recurring Tasks

### Goal
Implement recurring tasks functionality to auto-schedule repeating tasks (e.g., "weekly meeting").

### Tasks
- [x] T053 [P] Extend Task model in backend/src/models/task.py to include recurrence fields
- [x] T054 Create RecurringTask schema in backend/src/schemas/task.py with recurrence pattern fields
- [x] T055 [P] Add create_recurring_task method to task service in backend/src/services/task_service.py
- [x] T056 [P] Add recurrence processing logic to handle auto-scheduling of repeating tasks
- [x] T057 Update POST endpoint to support recurring task creation
- [x] T058 Create background job to handle recurring task scheduling
- [x] T059 Add tests for recurring task functionality

---

## Phase 8: Advanced Features - Due Dates & Time Reminders

### Goal
Implement due dates and time reminders functionality to allow users to set deadlines with date/time pickers.

### Tasks
- [x] T060 [P] Extend Task model in backend/src/models/task.py to include due_date and reminder fields
- [x] T061 [P] Update CreateTaskRequest and UpdateTaskRequest schemas to include due_date and reminder
- [x] T062 [P] Add due date validation logic to task service
- [x] T063 Create reminder notification system in backend/src/services/task_service.py
- [x] T064 Update all endpoints to handle due dates and reminders
- [x] T065 Create background job to handle reminder notifications
- [x] T066 Add tests for due dates and reminder functionality

---

## Phase 9: Testing & Quality Assurance

### Goal
Implement comprehensive testing to ensure all functionality works as specified and meets quality standards.

### Tasks
- [x] T067 [P] Create unit tests for task service in backend/tests/unit/test_task_service.py
- [x] T068 [P] Create unit tests for JWT utilities in backend/tests/unit/test_jwt.py
- [x] T069 Create integration tests for all API endpoints in backend/tests/integration/
- [x] T070 [P] Create authentication tests to verify security requirements
- [x] T071 [P] Implement test coverage requirements (minimum 80% as per constitution)
- [x] T072 Create contract tests for API endpoints in backend/tests/contract/
- [x] T073 Run complete test suite and verify all tests pass

---

## Phase 10: Polish & Cross-Cutting Concerns

### Goal
Final touches and deployment preparation for the secured todo API.

### Tasks
- [x] T074 Update backend/README.md with setup and usage instructions for the backend API
- [x] T075 [P] Add comprehensive API documentation with examples
- [x] T076 [P] Create deployment scripts for Docker containerization
- [x] T077 [P] Optimize database queries and connection settings
- [x] T078 [P] Add logging and monitoring capabilities
- [x] T079 [P] Implement proper error handling and user feedback messages
- [x] T080 [P] Add input validation and sanitization
- [x] T081 [P] Perform security review and vulnerability assessment
- [x] T082 [P] Performance testing to ensure response times meet requirements
- [x] T083 Final integration testing of all features
