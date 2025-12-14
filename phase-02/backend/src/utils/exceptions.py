from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Union
import logging

# Get logger
logger = logging.getLogger(__name__)

class TaskException(Exception):
    """Base exception for task-related errors"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class TaskNotFoundException(TaskException):
    """Raised when a task is not found"""
    def __init__(self, task_id: int):
        super().__init__(f"Task with ID {task_id} not found", 404)

class UnauthorizedAccessException(TaskException):
    """Raised when a user tries to access another user's tasks"""
    def __init__(self):
        super().__init__("You are not authorized to access this resource", 403)

class InvalidRecurrencePatternException(TaskException):
    """Raised when an invalid recurrence pattern is provided"""
    def __init__(self, pattern: str):
        super().__init__(f"Invalid recurrence pattern: {pattern}. Must be one of: daily, weekly, monthly, yearly", 400)

class InvalidReminderTimeException(TaskException):
    """Raised when reminder time is after due date"""
    def __init__(self):
        super().__init__("Reminder time cannot be after due date", 400)

class ValidationError(TaskException):
    """Raised for general validation errors"""
    def __init__(self, message: str):
        super().__init__(message, 400)

# Exception handlers
async def task_not_found_handler(request: Request, exc: TaskNotFoundException):
    logger.error(f"Task not found: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

async def unauthorized_access_handler(request: Request, exc: UnauthorizedAccessException):
    logger.error(f"Unauthorized access: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

async def invalid_recurrence_pattern_handler(request: Request, exc: InvalidRecurrencePatternException):
    logger.error(f"Invalid recurrence pattern: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

async def invalid_reminder_time_handler(request: Request, exc: InvalidReminderTimeException):
    logger.error(f"Invalid reminder time: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

async def validation_error_handler(request: Request, exc: ValidationError):
    logger.error(f"Validation error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

async def general_exception_handler(request: Request, exc: Union[Exception, HTTPException]):
    logger.error(f"General error occurred: {str(exc)}")
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred"}
        )