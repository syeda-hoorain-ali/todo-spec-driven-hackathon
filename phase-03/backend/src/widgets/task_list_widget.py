from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timezone
from chatkit.widgets import WidgetRoot, WidgetTemplate
from ..models.task import Task


WIDGET_DIR = Path(__file__).parent
WIDGET_FILE = WIDGET_DIR / "task_list.widget"

# Load the widget template with full path
task_list_widget_template = WidgetTemplate.from_file(str(WIDGET_FILE))

def _get_priority_color(priority: str | None) -> str:
    """Map priority to widget color scheme."""
    if priority == "low":
        return "success"
    elif priority == "medium":
        return "warning"
    elif priority in ["high", "urgent"]:
        return "danger"
    else:
        return "warning"  # default to warning for unknown


def _get_category_icon(category: str | None) -> str:
    """Map category to appropriate icon."""
    category_icons = {
        "work": "suitcase",
        "personal": "user",
        "health": "lifesaver",
        "finance": "chart",
        "learning": "book-open",
        "other": "document"
    }
    return category_icons.get(category or "other", "document")


def _get_toggle_icon(is_completed: bool) -> str:
    """Get icon for task completion toggle."""
    return "check-circle-filled" if is_completed else "empty-circle"


def _get_due_date_info(due_date: datetime | str | None) -> dict[str, str] | None:
    """Calculate due date label and color based on time remaining."""
    if not due_date:
        return None
    
    # Convert string to datetime if needed
    if isinstance(due_date, str):
        try:
            # Try to parse ISO format datetime string
            due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        except (ValueError, AttributeError) as e:
            print(f"Failed to parse due_date string: {due_date}, error: {e}")
            return None
    
    now = datetime.now(timezone.utc)
    
    # Ensure due_date is timezone-aware
    if due_date.tzinfo is None:
        due_date = due_date.replace(tzinfo=timezone.utc)
    
    time_diff = due_date - now
    days_remaining = time_diff.days
    
    # Determine label and color
    if days_remaining < 0:
        return {
            "label": f"Overdue by {abs(days_remaining)} days" if abs(days_remaining) > 1 else "Overdue",
            "color": "danger"
        }
    elif days_remaining == 0:
        return {
            "label": "Due today",
            "color": "warning"
        }
    elif days_remaining == 1:
        return {
            "label": "Due tomorrow",
            "color": "warning"
        }
    elif days_remaining <= 7:
        return {
            "label": f"Due in {days_remaining} days",
            "color": "warning"
        }
    else:
        return {
            "label": f"Due in {days_remaining} days",
            "color": "secondary"
        }


def _format_reminder(reminder_time: datetime | None) -> str | None:
    """Format reminder time as a readable string."""
    if not reminder_time:
        return None
    
    # Ensure reminder_time is timezone-aware
    if reminder_time.tzinfo is None:
        reminder_time = reminder_time.replace(tzinfo=timezone.utc)
    
    return reminder_time.strftime("%Y-%m-%d %H:%M")


def build_task_list_widget(title: str, tasks: List[Task]) -> WidgetRoot:
    """Build a task list widget from Task models."""
    widget_tasks : List[Dict[str, Any]] = []
    
    for task in tasks:
        task_data: Dict[str, Any] = {
            "id": str(task.id),  # Convert to string as schema expects string
            "title": task.title,
            "category": task.category or "other",
            "description": task.description,
            "icon": _get_category_icon(task.category),
            "isCompleted": task.completed,
            "due": _get_due_date_info(task.due_date),
            "reminder": _format_reminder(task.reminder_time),
            "priorityLabel": task.priority or "medium",
            "priorityColor": _get_priority_color(task.priority),
            "toggleIcon": _get_toggle_icon(task.completed),
        }
        

        widget_tasks.append(task_data)

    return task_list_widget_template.build(
        data={
            "header": title,
            "tasks": widget_tasks
        }
    )
