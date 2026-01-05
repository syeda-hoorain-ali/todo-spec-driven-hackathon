import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api.routes.tasks import router as tasks_router
from src.api.routes.chat import router as chat_router
from src.todo_agents.chat_agent import create_todo_chat_agent
from src.utils.logging import logger
from src.utils.exceptions import (
    TaskNotFoundException, UnauthorizedAccessException,
    InvalidRecurrencePatternException, InvalidReminderTimeException,
    ValidationError, task_not_found_handler, unauthorized_access_handler,
    invalid_recurrence_pattern_handler, invalid_reminder_time_handler,
    validation_error_handler, general_exception_handler
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Retry logic for MCP connection
    max_retries = 5
    retry_delay = 2
    agent, mcp_server = create_todo_chat_agent()
    
    for attempt in range(max_retries):
        try:
            await mcp_server.connect()
            logger.info("MCP server connected")
            break
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(f"MCP connection attempt {attempt + 1} failed, retrying in {retry_delay}s...")
            await asyncio.sleep(retry_delay)
    
    yield
    
    # Cleanup
    await mcp_server.cleanup()
    logger.info("MCP server cleanup")


app = FastAPI(title="Secured Todo API", version="1.0.0", lifespan=lifespan)

# Log application startup
logger.info("Secured Todo API starting up...")

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    # settings.frontend_base_url,  # Temporarily comment out for testing
]

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Expose authorization headers to frontend
    expose_headers=["Access-Control-Allow-Origin"]
)

app.include_router(tasks_router)

# Include chat routes (includes ChatKit functionality)
app.include_router(chat_router)

# Add exception handlers
app.add_exception_handler(TaskNotFoundException, task_not_found_handler)
app.add_exception_handler(UnauthorizedAccessException, unauthorized_access_handler)
app.add_exception_handler(InvalidRecurrencePatternException, invalid_recurrence_pattern_handler)
app.add_exception_handler(InvalidReminderTimeException, invalid_reminder_time_handler)
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

@app.get("/")
async def root():
    return {"message": "Welcome to the Secured Todo API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
