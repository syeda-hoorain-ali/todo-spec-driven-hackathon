from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Handle both direct execution and module import
try:
    from .api.routes.tasks import router as tasks_router
    from .config.settings import settings
    from .utils.logging import logger
    from .utils.exceptions import (
        TaskNotFoundException, UnauthorizedAccessException,
        InvalidRecurrencePatternException, InvalidReminderTimeException,
        ValidationError, task_not_found_handler, unauthorized_access_handler,
        invalid_recurrence_pattern_handler, invalid_reminder_time_handler,
        validation_error_handler, general_exception_handler
    )
except ImportError:
    # When running tests, use absolute import
    from api.routes.tasks import router as tasks_router
    from config.settings import settings
    from utils.logging import logger
    from utils.exceptions import (
        TaskNotFoundException, UnauthorizedAccessException,
        InvalidRecurrencePatternException, InvalidReminderTimeException,
        ValidationError, task_not_found_handler, unauthorized_access_handler,
        invalid_recurrence_pattern_handler, invalid_reminder_time_handler,
        validation_error_handler, general_exception_handler
    )

app = FastAPI(title="Secured Todo API", version="1.0.0")

# Log application startup
logger.info("Secured Todo API starting up...")

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    settings.frontend_base_url,
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
