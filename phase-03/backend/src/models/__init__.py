# Import all models here to make them available when importing from the models package
from .base import Base
from .task import Task, TaskCreate, TaskRead, TaskUpdate
from .thread import Thread, ThreadCreate, ThreadRead, ThreadUpdate
from .thread_item import ThreadItem, ThreadItemCreate, ThreadItemRead, ThreadItemUpdate

# Export models so they're available when importing from models
__all__ = [
    "Base",
    "Task", "TaskCreate", "TaskRead", "TaskUpdate",
    "Thread", "ThreadCreate", "ThreadRead", "ThreadUpdate",
    "ThreadItem", "ThreadItemCreate", "ThreadItemRead", "ThreadItemUpdate"
]
