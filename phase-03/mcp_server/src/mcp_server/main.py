from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from typing import List, Dict, Any
import logging

from .database import get_session, init_db
from .models import Task, AddTaskRequest, ListTasksRequest, CompleteTaskRequest, DeleteTaskRequest, UpdateTaskRequest
from .tools import create_task, list_tasks_filtered, complete_task_in_db, delete_task_from_db, update_task_in_db
from .auth import verify_token

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
mcp = FastMCP(name="todo-mcp-server", json_response=True)

# Define response models for the tools
class AddTaskResponse(BaseModel):
    task_id: int
    status: str
    title: str


class ListTasksResponse(BaseModel):
    tasks: List[Dict[str, Any]]  # For now keeping as dict for compatibility with MCP protocol


class CompleteTaskResponse(BaseModel):
    task_id: int
    status: str
    title: str


class DeleteTaskResponse(BaseModel):
    task_id: int
    status: str
    title: str


class UpdateTaskResponse(BaseModel):
    task_id: int
    status: str
    title: str


# Define the add_task tool
@mcp.tool()
async def add_task(request: AddTaskRequest) -> AddTaskResponse:
    """
    Create a new task
    """
    try:
        # Get database session
        with next(get_session()) as session:
            created_task = create_task(session, request)

            return AddTaskResponse(
                task_id=created_task.id,
                status="created",
                title=created_task.title
            )
    except Exception as e:
        logger.error(f"Error in add_task: {str(e)}")
        raise


# Define the list_tasks tool
@mcp.tool()
async def list_tasks(request: ListTasksRequest) -> ListTasksResponse:
    """
    Retrieve tasks with filtering options
    """
    try:
        # Get database session
        with next(get_session()) as session:
            tasks = list_tasks_filtered(session, request)

            # Convert tasks to dictionaries
            task_dicts = []
            for task in tasks:
                task_dict = {
                    "id": task.id,
                    "user_id": task.user_id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "category": task.category,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                    "is_recurring": task.is_recurring,
                    "recurrence_pattern": task.recurrence_pattern,
                    "recurrence_interval": task.recurrence_interval,
                    "next_occurrence": task.next_occurrence.isoformat() if task.next_occurrence else None,
                    "recurrence_end_date": task.recurrence_end_date.isoformat() if task.recurrence_end_date else None,
                    "max_occurrences": task.max_occurrences,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
                task_dicts.append(task_dict)

            return ListTasksResponse(tasks=task_dicts)
    except Exception as e:
        logger.error(f"Error in list_tasks: {str(e)}")
        raise


# Define the complete_task tool
@mcp.tool()
async def complete_task(request: CompleteTaskRequest) -> CompleteTaskResponse:
    """
    Mark a task as complete
    """
    try:
        # Get database session
        with next(get_session()) as session:
            completed_task = complete_task_in_db(session, request.task_id, request.user_id)

            return CompleteTaskResponse(
                task_id=completed_task.id,
                status="completed",
                title=completed_task.title
            )
    except Exception as e:
        logger.error(f"Error in complete_task: {str(e)}")
        raise


# Define the delete_task tool
@mcp.tool()
async def delete_task(request: DeleteTaskRequest) -> DeleteTaskResponse:
    """
    Remove a task
    """
    try:
        # Get database session
        with next(get_session()) as session:
            # First get the task to return its details in the response
            from sqlmodel import select
            statement = select(Task).where(Task.id == request.task_id, Task.user_id == request.user_id)
            task = session.exec(statement).first()

            if not task:
                raise Exception("Task not found or access denied")

            # Delete the task
            deleted = delete_task_from_db(session, request.task_id, request.user_id)

            if not deleted:
                raise Exception("Task not found or access denied")

            return DeleteTaskResponse(
                task_id=task.id,
                status="deleted",
                title=task.title
            )
    except Exception as e:
        logger.error(f"Error in delete_task: {str(e)}")
        raise


# Define the update_task tool
@mcp.tool()
async def update_task(request: UpdateTaskRequest) -> UpdateTaskResponse:
    """
    Modify task details
    """
    try:
        # Get database session
        with next(get_session()) as session:
            updated_task = update_task_in_db(session, request.task_id, request.user_id, request)

            return UpdateTaskResponse(
                task_id=updated_task.id,
                status="updated",
                title=updated_task.title
            )
    except Exception as e:
        logger.error(f"Error in update_task: {str(e)}")
        raise


if __name__ == "__main__":
    import sys

    # Initialize the database
    init_db()

    # Run the server
    if len(sys.argv) > 1 and "--stdio" in sys.argv:
        # Run as MCP server via stdio
        mcp.run(transport="stdio")
    else:
        # For development, just run the server in the foreground
        mcp.run(transport="streamable-http")

        print("Starting MCP server...")
        print("Use --stdio argument to run as MCP server via stdio")
        