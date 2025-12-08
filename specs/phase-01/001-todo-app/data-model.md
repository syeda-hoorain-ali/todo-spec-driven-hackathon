# Data Model: 001-todo-app

## Task Entity

### Properties
- **id**: `int`
  - Auto-generated unique identifier
  - Primary key for the task
  - Auto-incrementing sequence

- **title**: `str`
  - Required field
  - Max length: 200 characters
  - Validation: Non-empty, trimmed whitespace

- **description**: `str`
  - Optional field
  - Max length: 1000 characters
  - Default: Empty string

- **status**: `str`
  - Enum values: "pending", "in-progress", "complete"
  - Default: "pending"
  - Validation: Must be one of the allowed values

- **priority**: `str`
  - Enum values: "low", "medium", "high"
  - Default: "medium"
  - Validation: Must be one of the allowed values

- **created_date**: `datetime`
  - Auto-generated timestamp
  - Format: ISO 8601 (YYYY-MM-DDTHH:MM:SS.mmmmmm)
  - Set on creation, read-only thereafter

- **due_date**: `datetime`
  - Optional field
  - Format: ISO 8601 (YYYY-MM-DDTHH:MM:SS.mmmmmm)
  - Can be None/NULL

- **tags**: `list[str]`
  - Optional field
  - Max items: 10 tags
  - Each tag max length: 50 characters
  - Default: Empty list

- **recurrence_pattern**: `str`
  - Optional field
  - Enum values: "daily", "weekly", "monthly", "none"
  - Default: "none"
  - Validation: Must be one of the allowed values

### Validation Rules
1. Title must be 1-200 characters after trimming
2. Description must be 0-1000 characters
3. Status must be one of: "pending", "in-progress", "complete"
4. Priority must be one of: "low", "medium", "high"
5. Tags list must have 0-10 items
6. Each tag must be 1-50 characters
7. Recurrence pattern must be one of: "daily", "weekly", "monthly", "none"

### State Transitions
- From "pending" → "in-progress" or "complete"
- From "in-progress" → "pending" or "complete"
- From "complete" → "pending" (to re-open)
- No transitions allowed when deleted

## TaskManager

### Responsibilities
- Maintain in-memory collection of tasks
- Provide CRUD operations for tasks
- Generate unique IDs for new tasks
- Handle search and filtering operations
- Validate task data before operations

### Methods
- `create_task(title: str, description: str = "", status: str = "pending", priority: str = "medium", due_date: datetime = None, tags: list[str] = [], recurrence_pattern: str = "none") -> Task`
- `get_task(task_id: int) -> Task | None`
- `get_all_tasks() -> list[Task]`
- `update_task(task_id: int, **updates) -> Task | None`
- `delete_task(task_id: int) -> bool`
- `search_tasks(keyword: str) -> list[Task]`
- `filter_tasks(**filters) -> list[Task]`
- `mark_complete(task_id: int) -> Task | None`
- `mark_incomplete(task_id: int) -> Task | None`

### In-Memory Storage
- Use dictionary with task ID as key for O(1) access
- Maintain auto-incrementing ID counter
- Thread-safe operations if needed for future extensions

## Implementation Considerations

### Python Class Definition
```python
from datetime import datetime
from typing import List, Optional

class Task:
    def __init__(
        self,
        id: int,
        title: str,
        description: str = "",
        status: str = "pending",
        priority: str = "medium",
        created_date: datetime = None,
        due_date: datetime = None,
        tags: List[str] = None,
        recurrence_pattern: str = "none"
    ):
        self.id = id
        self.title = self._validate_title(title)
        self.description = self._validate_description(description)
        self.status = self._validate_status(status)
        self.priority = self._validate_priority(priority)
        self.created_date = created_date or datetime.now()
        self.due_date = due_date
        self.tags = tags or []
        self.recurrence_pattern = self._validate_recurrence_pattern(recurrence_pattern)

    def _validate_title(self, title: str) -> str:
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        title = title.strip()
        if len(title) > 200:
            raise ValueError("Title cannot exceed 200 characters")
        return title

    def _validate_description(self, description: str) -> str:
        if len(description) > 1000:
            raise ValueError("Description cannot exceed 1000 characters")
        return description

    def _validate_status(self, status: str) -> str:
        valid_statuses = ["pending", "in-progress", "complete"]
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return status

    def _validate_priority(self, priority: str) -> str:
        valid_priorities = ["low", "medium", "high"]
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")
        return priority

    def _validate_recurrence_pattern(self, pattern: str) -> str:
        valid_patterns = ["daily", "weekly", "monthly", "none"]
        if pattern not in valid_patterns:
            raise ValueError(f"Recurrence pattern must be one of: {', '.join(valid_patterns)}")
        return pattern

    def validate_tags(self, tags: List[str]) -> List[str]:
        if len(tags) > 10:
            raise ValueError("A task cannot have more than 10 tags")
        for tag in tags:
            if not tag or not tag.strip():
                raise ValueError("Tags cannot be empty")
            if len(tag.strip()) > 50:
                raise ValueError("Each tag cannot exceed 50 characters")
        return [tag.strip() for tag in tags]
```