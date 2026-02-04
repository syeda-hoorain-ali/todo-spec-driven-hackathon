from mcp.server.fastmcp import FastMCP
import logging
from sqlmodel import select
from contextlib import asynccontextmanager
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from .database import get_session_with_user
from .models import Task, AddTaskRequest, ListTasksRequest, CompleteTaskRequest, DeleteTaskRequest, UpdateTaskRequest
from .schemas import AddTaskResponse, ListTasksResponse, CompleteTaskResponse, DeleteTaskResponse, UpdateTaskResponse
from .tools import create_task, list_tasks_filtered, complete_task_in_db, delete_task_from_db, update_task_in_db
from .config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
mcp = FastMCP(
    name="Taskflow MCP Server",
    json_response=True,
    stateless_http=True,
    streamable_http_path="/",
    port=settings.port,
    host= settings.host,
)


# Define the add_task tool
@mcp.tool()
async def add_task(request: AddTaskRequest) -> AddTaskResponse:
    """
    Create a new task
    """
    try:
        # Get database session
        with next(get_session_with_user(user_id=request.user_id)) as session:
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
        with next(get_session_with_user(user_id=request.user_id)) as session:
            tasks = list_tasks_filtered(session, request)

            # Convert tasks to dictionaries
            task_dicts = [task.model_dump(mode='json') for task in tasks]
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
        with next(get_session_with_user(user_id=request.user_id)) as session:
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
        with next(get_session_with_user(user_id=request.user_id)) as session:
            # First get the task to return its details in the response
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
        with next(get_session_with_user(user_id=request.user_id)) as session:
            updated_task = update_task_in_db(session, request.task_id, request.user_id, request)

            return UpdateTaskResponse(
                task_id=updated_task.id,
                status="updated",
                title=updated_task.title
            )
    except Exception as e:
        logger.error(f"Error in update_task: {str(e)}")
        raise


@mcp.custom_route("/health", methods=["GET"]) 
async def health_check(request: Request) -> JSONResponse: 
    return JSONResponse({"status": "ok"})


# Create the ASGI app for Vercel
# CRITICAL: You need the lifespan context manager
@asynccontextmanager
async def lifespan(app):
    async with mcp.session_manager.run():
        yield


# Export the ASGI app
app = mcp.streamable_http_app()
app.router.lifespan_context = lifespan


if __name__ == "__main__":
    import sys

    # Run the server
    if len(sys.argv) > 1 and "--stdio" in sys.argv:
        # Run as MCP server via stdio
        mcp.run(transport="stdio")
    else:
        # For development, just run the server in the foreground
        mcp.run(transport="streamable-http")

        print("Starting MCP server...")
        print("Use --stdio argument to run as MCP server via stdio")
        
# uv run -m --with mcp src.mcp_server.main
