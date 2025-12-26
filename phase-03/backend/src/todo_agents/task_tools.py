from typing import List, Optional, Dict, Any
from datetime import datetime
from agents import Tool
from pydantic import BaseModel, Field
from ..models.task import TaskCreate, TaskUpdate
from ..services.task_service import TaskService
from sqlmodel import Session
from ..database.database import engine


class ListTasksRequest(BaseModel):
    """Request model for listing tasks"""
    user_id: str = Field(..., description="ID of the user whose tasks to list")
    description: Optional[str] = Field(None, description="Optional filter to search for in task titles/descriptions")


class CreateTaskRequest(BaseModel):
    """Request model for creating a task"""
    user_id: str = Field(..., description="ID of the user creating the task")
    title: str = Field(..., description="Title of the task")
    description: Optional[str] = Field(None, description="Description of the task")
    category: Optional[str] = Field("other", description="Category of the task")
    priority: Optional[str] = Field("medium", description="Priority of the task")
    due_date: Optional[str] = Field(None, description="Due date in ISO format")


class UpdateTaskRequest(BaseModel):
    """Request model for updating a task"""
    user_id: str = Field(..., description="ID of the user updating the task")
    task_id: int = Field(..., description="ID of the task to update")
    title: Optional[str] = Field(None, description="New title of the task")
    description: Optional[str] = Field(None, description="New description of the task")
    completed: Optional[bool] = Field(None, description="New completion status")
    category: Optional[str] = Field(None, description="New category")
    priority: Optional[str] = Field(None, description="New priority")
    due_date: Optional[str] = Field(None, description="New due date in ISO format")


class DeleteTaskRequest(BaseModel):
    """Request model for deleting a task"""
    user_id: str = Field(..., description="ID of the user deleting the task")
    task_id: int = Field(..., description="ID of the task to delete")


class CompleteTaskRequest(BaseModel):
    """Request model for marking a task as completed"""
    user_id: str = Field(..., description="ID of the user updating the task")
    task_id: int = Field(..., description="ID of the task to update")
    completed: bool = Field(True, description="Whether the task should be marked as completed")


class TaskOperationTools:
    """Class containing task operation tools that can be registered with an MCP server."""

    def _get_session(self) -> Session:
        """Get a new database session."""
        return Session(engine)

    async def list_tasks(self, user_id: str, description: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List tasks for the specified user.

        Args:
            user_id: ID of the user whose tasks to list (required)
            description: Optional filter description to search for in task titles/descriptions
        """
        session = self._get_session()
        try:
            if description:
                # Search for tasks matching the description
                tasks = TaskService.search_tasks(
                    user_id=user_id,
                    keyword=description,
                    session=session
                )
            else:
                # Get all tasks for the user
                tasks = TaskService.get_tasks_by_user(user_id, session)

            # Convert tasks to dictionaries for the response
            task_dicts = []
            for task in tasks:
                task_dict = {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "user_id": task.user_id,
                    "category": task.category,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                }
                task_dicts.append(task_dict)

            return task_dicts
        except Exception as e:
            return {"error": f"Error listing tasks: {str(e)}"}
        finally:
            session.close()

    async def create_task(self, user_id: str, title: str, description: Optional[str] = None,
                         category: Optional[str] = "other",
                         priority: Optional[str] = "medium",
                         due_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new task.

        Args:
            user_id: ID of the user creating the task (required)
            title: Title of the task (required)
            description: Description of the task (optional)
            category: Category of the task (optional, default: "other")
            priority: Priority of the task (optional, default: "medium")
            due_date: Due date in ISO format (optional)
        """
        session = self._get_session()
        try:
            # Parse due_date if provided
            parsed_due_date = None
            if due_date:
                parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))

            # Create task data object
            task_data = TaskCreate(
                title=title,
                description=description,
                completed=False,  # New tasks are not completed by default
                category=category,
                priority=priority,
                due_date=parsed_due_date
            )

            # Create the task using the service
            created_task = TaskService.create_task(user_id, task_data, session)

            # Convert to dictionary for response
            task_dict = {
                "id": created_task.id,
                "title": created_task.title,
                "description": created_task.description,
                "completed": created_task.completed,
                "user_id": created_task.user_id,
                "category": created_task.category,
                "priority": created_task.priority,
                "due_date": created_task.due_date.isoformat() if created_task.due_date else None,
                "reminder_time": created_task.reminder_time.isoformat() if created_task.reminder_time else None,
                "created_at": created_task.created_at.isoformat(),
                "updated_at": created_task.updated_at.isoformat(),
            }

            return task_dict
        except Exception as e:
            return {"error": f"Error creating task: {str(e)}"}
        finally:
            session.close()

    async def update_task(self, user_id: str, task_id: int, title: Optional[str] = None,
                         description: Optional[str] = None,
                         completed: Optional[bool] = None,
                         category: Optional[str] = None,
                         priority: Optional[str] = None,
                         due_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing task.

        Args:
            user_id: ID of the user updating the task (required)
            task_id: ID of the task to update (required)
            title: New title of the task (optional)
            description: New description of the task (optional)
            completed: New completion status (optional)
            category: New category (optional)
            priority: New priority (optional)
            due_date: New due date in ISO format (optional)
        """
        session = self._get_session()
        try:
            # Parse due_date if provided
            parsed_due_date = None
            if due_date:
                parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))

            # Create update data object
            update_data = TaskUpdate(
                title=title,
                description=description,
                completed=completed,
                category=category,
                priority=priority,
                due_date=parsed_due_date
            )

            # Update the task using the service
            updated_task = TaskService.update_task(task_id, user_id, update_data, session)

            if updated_task:
                # Convert to dictionary for response
                task_dict = {
                    "id": updated_task.id,
                    "title": updated_task.title,
                    "description": updated_task.description,
                    "completed": updated_task.completed,
                    "user_id": updated_task.user_id,
                    "category": updated_task.category,
                    "priority": updated_task.priority,
                    "due_date": updated_task.due_date.isoformat() if updated_task.due_date else None,
                    "reminder_time": updated_task.reminder_time.isoformat() if updated_task.reminder_time else None,
                    "created_at": updated_task.created_at.isoformat(),
                    "updated_at": updated_task.updated_at.isoformat(),
                }
                return task_dict
            else:
                return {"error": f"Task with ID {task_id} not found or you don't have permission to update it"}
        except Exception as e:
            return {"error": f"Error updating task: {str(e)}"}
        finally:
            session.close()

    async def delete_task(self, user_id: str, task_id: int) -> Dict[str, Any]:
        """
        Delete a task.

        Args:
            user_id: ID of the user deleting the task (required)
            task_id: ID of the task to delete (required)
        """
        session = self._get_session()
        try:
            # Delete the task using the service
            success = TaskService.delete_task(task_id, user_id, session)

            if success:
                return {"message": f"Task with ID {task_id} deleted successfully"}
            else:
                return {"error": f"Task with ID {task_id} not found or you don't have permission to delete it"}
        except Exception as e:
            return {"error": f"Error deleting task: {str(e)}"}
        finally:
            session.close()

    async def complete_task(self, user_id: str, task_id: int, completed: bool = True) -> Dict[str, Any]:
        """
        Mark a task as completed or not completed.

        Args:
            user_id: ID of the user updating the task (required)
            task_id: ID of the task to update (required)
            completed: Whether the task should be marked as completed (default: True)
        """
        session = self._get_session()
        try:
            # Toggle task completion using the service
            updated_task = TaskService.toggle_task_completion(task_id, user_id, session)

            if updated_task:
                # Convert to dictionary for response
                task_dict = {
                    "id": updated_task.id,
                    "title": updated_task.title,
                    "description": updated_task.description,
                    "completed": updated_task.completed,
                    "user_id": updated_task.user_id,
                    "category": updated_task.category,
                    "priority": updated_task.priority,
                    "due_date": updated_task.due_date.isoformat() if updated_task.due_date else None,
                    "reminder_time": updated_task.reminder_time.isoformat() if updated_task.reminder_time else None,
                    "created_at": updated_task.created_at.isoformat(),
                    "updated_at": updated_task.updated_at.isoformat(),
                }
                return task_dict
            else:
                return {"error": f"Task with ID {task_id} not found or you don't have permission to update it"}
        except Exception as e:
            return {"error": f"Error updating task completion: {str(e)}"}
        finally:
            session.close()