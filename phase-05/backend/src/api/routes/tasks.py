from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlmodel import Session
from typing import  Optional, Generator
from datetime import datetime

# Handle both direct execution and module import
try:
    from ...schemas.task import CreateTaskRequest, TaskResponse, TaskListResponse, UpdateTaskRequest
    from ...services.task_service import TaskService
    from ...database.database import engine
    from ...auth.middleware import JWTBearer
    from ...config.settings import settings
    from ...utils.exceptions import InvalidRecurrencePatternException, InvalidReminderTimeException, ValidationError
    from ...utils.validation import validate_task_title, validate_task_description, validate_user_id, validate_task_id
except ImportError:
    # When running tests or as module, use absolute imports
    from src.schemas.task import CreateTaskRequest, TaskResponse, TaskListResponse, UpdateTaskRequest
    from src.services.task_service import TaskService
    from src.database.database import engine
    from src.auth.middleware import JWTBearer
    from src.config.settings import settings
    from src.utils.exceptions import InvalidRecurrencePatternException, InvalidReminderTimeException, ValidationError
    from src.utils.validation import validate_task_title, validate_task_description, validate_user_id, validate_task_id

router = APIRouter(prefix="/api/{user_id}", tags=["tasks"])
security = JWTBearer()


def get_session_with_user_context(user_id: str = Path(...), token: str = Depends(security)) -> Generator[Session, None, None]:
    """Dependency that provides a database session with user context for RLS."""
    from ...auth.jwt import get_user_id_from_token
    from sqlalchemy import text

    # Verify that the token user matches the URL user_id
    token_user_id = get_user_id_from_token(token)
    if not token_user_id or token_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access tasks for yourself"
        )

    # Create and yield the session with user context
    with Session(engine) as session:
        # Set the current user ID for RLS policies (only for PostgreSQL/production)
        if 'postgresql' in settings.database_url.lower():
            session.exec(text("SET app.current_user_id = :user_id"), params={"user_id": user_id})
        yield session


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_data: CreateTaskRequest,
    token: str = Depends(security),
    session: Session = Depends(get_session_with_user_context)
):
    """Create a new task for the authenticated user."""
    # Note: Authorization is handled by the get_session_with_user_context dependency
    # which sets the RLS context and verifies token matches user_id

    # Validate and sanitize user_id
    validated_user_id = validate_user_id(user_id)

    # Validate and sanitize task title and description
    validated_title = validate_task_title(task_data.title)
    validated_description = validate_task_description(task_data.description)

    # Update task_data with sanitized values
    task_data.title = validated_title
    if task_data.description is not None:
        task_data.description = validated_description

    # Validate recurrence fields if the task is recurring
    if getattr(task_data, 'is_recurring', False):
        if not getattr(task_data, 'recurrence_pattern', None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recurrence pattern is required for recurring tasks"
            )

        if task_data.recurrence_pattern not in ['daily', 'weekly', 'monthly', 'yearly']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid recurrence pattern. Must be one of: daily, weekly, monthly, yearly"
            )

    # Create the task using the service
    try:
        # Check if this is a recurring task
        if getattr(task_data, 'is_recurring', False):
            task = TaskService.create_recurring_task(validated_user_id, task_data, session)
        else:
            task = TaskService.create_task(validated_user_id, task_data, session)

        # Convert SQLModel task to Pydantic TaskResponse
        task_response = TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            user_id=task.user_id,
            category=task.category,
            priority=task.priority,
            due_date=task.due_date,
            reminder_time=task.reminder_time,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        return task_response
    except (InvalidRecurrencePatternException, InvalidReminderTimeException, ValidationError) as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating task: {str(e)}"
        )


@router.get("/tasks", response_model=TaskListResponse)
async def get_tasks(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    keyword: Optional[str] = None,
    completed: Optional[bool] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    token: str = Depends(security),
    session: Session = Depends(get_session_with_user_context)
):
    """Get all tasks for the authenticated user with optional search and filter."""
    # Note: Authorization is handled by the get_session_with_user_context dependency

    # Search and filter tasks based on parameters
    if keyword or completed is not None or category or priority or date_from or date_to:
        tasks = TaskService.search_tasks(
            user_id=user_id,
            keyword=keyword,
            completed=completed,
            date_from=date_from,
            date_to=date_to,
            session=session,
            category=category,
            priority=priority,
            skip=skip,
            limit=limit
        )
    else:
        # Get all tasks for the user without filtering
        tasks = TaskService.get_tasks_by_user(user_id, session, skip, limit)

    task_responses = [
        TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            user_id=task.user_id,
            category=task.category,
            priority=task.priority,
            due_date=task.due_date,
            reminder_time=task.reminder_time,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        for task in tasks
    ]

    return TaskListResponse(tasks=task_responses, count=len(task_responses))


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: int,
    token: str = Depends(security),
    session: Session = Depends(get_session_with_user_context)
):
    """Get a specific task for the authenticated user."""
    # Note: Authorization is handled by the get_session_with_user_context dependency

    # Validate inputs
    validated_user_id = validate_user_id(user_id)
    validated_task_id = validate_task_id(task_id)

    # Get the specific task
    task = TaskService.get_task_by_id(validated_task_id, validated_user_id, session)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        user_id=task.user_id,
        category=task.category,
        priority=task.priority,
        due_date=task.due_date,
        reminder_time=task.reminder_time,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: int,
    task_data: UpdateTaskRequest,
    token: str = Depends(security),
    session: Session = Depends(get_session_with_user_context)
):
    """Update a specific task for the authenticated user."""
    # Note: Authorization is handled by the get_session_with_user_context dependency

    # Validate and sanitize inputs
    validated_user_id = validate_user_id(user_id)
    validated_task_id = validate_task_id(task_id)

    # Validate and sanitize task title and description if provided
    if task_data.title is not None:
        task_data.title = validate_task_title(task_data.title)
    if task_data.description is not None:
        task_data.description = validate_task_description(task_data.description)

    # Update the task
    updated_task = TaskService.update_task(validated_task_id, validated_user_id, task_data, session)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission to update it"
        )

    return TaskResponse(
        id=updated_task.id,
        title=updated_task.title,
        description=updated_task.description,
        completed=updated_task.completed,
        user_id=updated_task.user_id,
        category=updated_task.category,
        priority=updated_task.priority,
        due_date=updated_task.due_date,
        reminder_time=updated_task.reminder_time,
        created_at=updated_task.created_at,
        updated_at=updated_task.updated_at
    )


@router.delete("/tasks/{task_id}")
async def delete_task(
    user_id: str,
    task_id: int,
    token: str = Depends(security),
    session: Session = Depends(get_session_with_user_context)
):
    """Delete a specific task for the authenticated user."""
    # Note: Authorization is handled by the get_session_with_user_context dependency

    # Validate inputs
    validated_user_id = validate_user_id(user_id)
    validated_task_id = validate_task_id(task_id)

    # Delete the task
    success = TaskService.delete_task(validated_task_id, validated_user_id, session)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission to delete it"
        )

    return {"message": "Task deleted successfully"}


@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    user_id: str,
    task_id: int,
    token: str = Depends(security),
    session: Session = Depends(get_session_with_user_context)
):
    """Toggle the completion status of a task for the authenticated user."""
    # Note: Authorization is handled by the get_session_with_user_context dependency

    # Validate inputs
    validated_user_id = validate_user_id(user_id)
    validated_task_id = validate_task_id(task_id)

    # Toggle task completion
    task = TaskService.toggle_task_completion(validated_task_id, validated_user_id, session)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission to modify it"
        )

    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        user_id=task.user_id,
        category=task.category,
        priority=task.priority,
        due_date=task.due_date,
        reminder_time=task.reminder_time,
        created_at=task.created_at,
        updated_at=task.updated_at
    )
