from pydantic import BaseModel
from typing import Optional
from fastapi import Request


class UserContext(BaseModel):
    """Pydantic model for user context in chat operations"""
    user_id: str
    request: Optional[dict] = None  # Store minimal request info if needed

