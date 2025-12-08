# 001-todo-app Tasks

**Feature**: 001-todo-app: Todo In-Memory Python Console App
**Created**: 2025-12-08
**Status**: Draft
**Author**: Claude Code

## Implementation Strategy

MVP will implement User Story 1 (Add and View Tasks) with basic functionality. Additional features will be implemented incrementally following the priority order from the specification.

## Dependencies

User stories are designed to be independently implementable with minimal dependencies:
- US1 (P1) - Core functionality, required by all other stories
- US2 (P1) - Depends on US1 (needs tasks to mark complete)
- US3 (P2) - Depends on US1 (needs tasks to delete)
- US4 (P2) - Depends on US1 (needs tasks to update)
- US5 (P3) - Depends on US1 (needs tasks to search)
- US6 (P3) - Depends on US1 (needs tasks to add priorities/tags)
- US7 (P4) - Depends on US1 (needs tasks to add recurrence/due dates)

## Parallel Execution Examples

Each user story can be developed in parallel by different developers:
- Developer A: Work on US2 (Mark Tasks Complete)
- Developer B: Work on US3 (Delete Tasks)
- Developer C: Work on US4 (Update Task Details)
- Developer D: Work on US5 (Search and Filter Tasks)

## Phase 1: Setup

Setup tasks for project initialization and environment configuration.

- [X] T001 Create project directory structure in src/phase-01/todo_app/
- [X] T002 Create pyproject.toml with project metadata and dependencies (Rich, pytest) following uv package management standards
- [X] T003 [P] Create main.py as entry point for the application
- [X] T004 [P] Create requirements-dev.txt for development dependencies
- [X] T005 Create .gitignore with Python and IDE patterns
- [X] T006 Set up virtual environment using uv
- [X] T007 Create README.md with project description and setup instructions

## Phase 2: Foundational

Foundational tasks that must be completed before user stories can be implemented.

- [X] T010 Create models/task.py with Task class and validation methods
- [X] T011 Create managers/task_manager.py with TaskManager class
- [X] T012 [P] Create cli/cli_interface.py with command parsing logic
- [X] T013 [P] Create ui/renderer.py with Rich-based display functions
- [X] T014 Set up basic testing structure with pytest
- [X] T015 Create configuration for testing framework
- [X] T016 Implement basic data validation for Task entity

## Phase 3: User Story 1 - Add and View Tasks (Priority: P1)

As a user, I want to add new tasks to my todo list and view them in the console so that I can keep track of what I need to do.

### Independent Test Criteria
- Can add a task through the command line
- Can view all tasks in the console with their status
- Task appears in the task list with a unique ID and pending status

### Implementation Tasks

- [X] T020 [US1] Implement Task creation with auto-generated ID in models/task.py
- [X] T021 [P] [US1] Implement add_task method in managers/task_manager.py
- [X] T022 [P] [US1] Create CLI argument parsing for 'add' command in cli/cli_interface.py
- [X] T023 [P] [US1] Create CLI argument parsing for 'list' command in cli/cli_interface.py
- [X] T024 [US1] Implement get_all_tasks method in managers/task_manager.py
- [X] T025 [US1] Implement rich table display for task list in ui/renderer.py
- [X] T026 [US1] Connect 'add' command to TaskManager in cli/cli_interface.py
- [X] T027 [US1] Connect 'list' command to TaskManager and Renderer in cli/cli_interface.py
- [X] T028 [US1] Test basic add and list functionality with pytest
- [X] T029 [US1] Validate task title and description constraints

## Phase 4: User Story 2 - Mark Tasks Complete (Priority: P1)

As a user, I want to mark tasks as complete so that I can track my progress and focus on remaining tasks.

### Independent Test Criteria
- Can mark a pending task as complete
- Task status changes to complete and is visually distinct in the list
- Can mark a completed task as pending again

### Implementation Tasks

- [X] T030 [US2] Add mark_complete and mark_incomplete methods to TaskManager in managers/task_manager.py
- [X] T031 [P] [US2] Create CLI argument parsing for 'complete' command in cli/cli_interface.py
- [X] T032 [P] [US2] Create CLI argument parsing for 'incomplete' command in cli/cli_interface.py
- [X] T033 [US2] Update Task model to support status transitions in models/task.py
- [X] T034 [US2] Update renderer to visually distinguish completed tasks in ui/renderer.py
- [X] T035 [US2] Connect 'complete' command to TaskManager in cli/cli_interface.py
- [X] T036 [US2] Connect 'incomplete' command to TaskManager in cli/cli_interface.py
- [X] T037 [US2] Test mark complete/incomplete functionality with pytest
- [X] T038 [US2] Validate task ID exists before marking complete/incomplete

## Phase 5: User Story 3 - Delete Tasks (Priority: P2)

As a user, I want to remove tasks I no longer need so that my task list stays organized and relevant.

### Independent Test Criteria
- Can delete a task by ID
- Deleted task no longer appears in the task list
- Appropriate error message when trying to delete non-existent task

### Implementation Tasks

- [X] T040 [US3] Implement delete_task method in managers/task_manager.py
- [X] T041 [P] [US3] Create CLI argument parsing for 'delete' command in cli/cli_interface.py
- [X] T042 [US3] Connect 'delete' command to TaskManager in cli/cli_interface.py
- [X] T043 [US3] Update renderer to confirm deletion in ui/renderer.py
- [X] T044 [US3] Test delete functionality with pytest
- [X] T045 [US3] Validate task ID exists before deletion
- [X] T046 [US3] Handle error case when trying to delete non-existent task

## Phase 6: User Story 4 - Update Task Details (Priority: P2)

As a user, I want to modify existing tasks so that I can keep my todo list accurate as my plans change.

### Independent Test Criteria
- Can update task title and description
- Can update task priority
- Can update task due date
- Changes are reflected in the task list

### Implementation Tasks

- [X] T050 [US4] Implement update_task method in managers/task_manager.py
- [X] T051 [P] [US4] Create CLI argument parsing for 'update' command options in cli/cli_interface.py
- [X] T052 [US4] Add support for updating priority in update_task method
- [X] T053 [US4] Add support for updating due date in update_task method
- [X] T054 [US4] Connect 'update' command to TaskManager in cli/cli_interface.py
- [X] T055 [US4] Test update functionality with pytest
- [X] T056 [US4] Validate updates against Task entity constraints
- [X] T057 [US4] Handle error case when trying to update non-existent task

## Phase 7: User Story 5 - Search and Filter Tasks (Priority: P3)

As a user, I want to search and filter my tasks by keyword, status, or priority so that I can quickly find relevant tasks.

### Independent Test Criteria
- Can search tasks by keyword in title or description
- Can filter tasks by status
- Can filter tasks by priority
- Only matching tasks are displayed

### Implementation Tasks

- [X] T060 [US5] Implement search_tasks method in managers/task_manager.py
- [X] T061 [P] [US5] Implement filter_tasks method in managers/task_manager.py
- [X] T062 [P] [US5] Create CLI argument parsing for 'search' command in cli/cli_interface.py
- [X] T063 [P] [US5] Add filter options to 'list' command in cli/cli_interface.py
- [X] T064 [US5] Update renderer to display search results in ui/renderer.py
- [X] T065 [US5] Connect 'search' command to TaskManager in cli/cli_interface.py
- [X] T066 [US5] Connect filtered 'list' command to TaskManager in cli/cli_interface.py
- [X] T067 [P] [US5] Implement sort_tasks method in managers/task_manager.py
- [X] T068 [US5] Add sort options to 'list' command in cli/cli_interface.py
- [X] T069 [US5] Connect sorted 'list' command to TaskManager in cli/cli_interface.py
- [X] T070 [US5] Test search, filter and sort functionality with pytest
- [X] T071 [US5] Optimize search and sort performance for large task lists

## Phase 8: User Story 6 - Set Priorities and Tags (Priority: P3)

As a user, I want to assign priorities and tags to my tasks so that I can better organize and prioritize my work.

### Independent Test Criteria
- Can add priority when creating a task
- Can add tags when creating a task
- Can update priority of existing task
- Can add/remove tags from existing task
- Tasks display priority and tags correctly

### Implementation Tasks

- [X] T072 [US6] Enhance Task model to support tags in models/task.py
- [X] T073 [P] [US6] Update Task creation to accept priority parameter in models/task.py
- [X] T074 [P] [US6] Update Task creation to accept tags parameter in models/task.py
- [X] T075 [US6] Update renderer to display priority and tags in ui/renderer.py
- [X] T076 [US6] Add priority and tags options to 'add' command in cli/cli_interface.py
- [X] T077 [US6] Add priority and tags options to 'update' command in cli/cli_interface.py
- [X] T078 [US6] Test priority and tags functionality with pytest
- [X] T079 [US6] Validate tag constraints (max 10 tags, max 50 chars each)

## Phase 9: User Story 7 - Recurring Tasks and Due Dates (Priority: P4)

As a user, I want to set recurring tasks and due dates so that I can manage time-sensitive and repetitive tasks effectively.

### Independent Test Criteria
- Can set due date when creating a task
- Can set recurrence pattern when creating a task
- Due dates are displayed in the task list
- Recurring tasks are properly stored

### Implementation Tasks

- [X] T080 [US7] Enhance Task model to support recurrence patterns in models/task.py
- [X] T081 [P] [US7] Add due date validation in Task model in models/task.py
- [X] T082 [P] [US7] Add recurrence pattern validation in Task model in models/task.py
- [X] T083 [US7] Update renderer to display due dates and recurrence in ui/renderer.py
- [X] T084 [US7] Add due date and recurrence options to 'add' command in cli/cli_interface.py
- [X] T085 [US7] Add due date and recurrence options to 'update' command in cli/cli_interface.py
- [X] T086 [US7] Test recurring tasks and due dates functionality with pytest
- [X] T087 [US7] Implement due date formatting for display

## Phase 10: Polish & Cross-Cutting Concerns

Final tasks to complete the application and ensure quality.

- [X] T100 Add comprehensive error handling throughout the application
- [X] T101 [P] Implement proper exit codes for CLI commands
- [X] T102 [P] Add help text for all available commands
- [X] T103 Add input validation for all user inputs
- [X] T104 Implement proper logging for debugging
- [X] T105 Add comprehensive test coverage (aim for 80%+)
- [X] T106 Create comprehensive README with usage examples
- [X] T107 Run all tests and fix any failures
- [X] T108 Perform integration testing of all features
- [X] T109 Final code review and cleanup
