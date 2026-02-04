from typing import List, Dict, Any
from pydantic import BaseModel

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
