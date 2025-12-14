import re
from typing import Optional
from ..utils.exceptions import ValidationError

def sanitize_input(text: Optional[str]) -> Optional[str]:
    """
    Sanitize input text by removing potentially dangerous characters/sequences.
    """
    if text is None:
        return None

    # Remove potentially dangerous characters but preserve normal text
    sanitized = text.strip()

    # Remove any script tags (basic protection against XSS)
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'vbscript:', '', sanitized, flags=re.IGNORECASE)

    # Remove other potentially dangerous patterns
    sanitized = re.sub(r'eval\(', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'expression\(', '', sanitized, flags=re.IGNORECASE)

    return sanitized

def validate_task_title(title: str) -> str:
    """
    Validate and sanitize task title.
    """
    if not title or not title.strip():
        raise ValidationError("Task title is required and cannot be empty")

    # Sanitize the title
    sanitized_title = sanitize_input(title)

    if len(sanitized_title) > 255:
        raise ValidationError("Task title must not exceed 255 characters")

    return sanitized_title

def validate_task_description(description: Optional[str]) -> Optional[str]:
    """
    Validate and sanitize task description.
    """
    if description is None:
        return None

    # Sanitize the description
    sanitized_description = sanitize_input(description)

    if len(sanitized_description) > 1000:
        raise ValidationError("Task description must not exceed 1000 characters")

    return sanitized_description

def validate_user_id(user_id: str) -> str:
    """
    Validate user ID format to prevent injection attacks.
    """
    if not user_id:
        raise ValidationError("User ID is required")

    # Allow alphanumeric characters, hyphens, and underscores (typical for user IDs)
    if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
        raise ValidationError("Invalid user ID format")

    return user_id

def validate_task_id(task_id: int) -> int:
    """
    Validate task ID.
    """
    if task_id <= 0:
        raise ValidationError("Task ID must be a positive integer")

    return task_id