from typing import List
from agents import function_tool, RunContextWrapper
from chatkit.agents import AgentContext

from .context import UserContext
from ..models.task import Task
from ..widgets.task_list_widget import build_task_list_widget


@function_tool
async def show_task_list(
    ctx: RunContextWrapper[AgentContext[UserContext]],
    title: str,
    tasks: List[Task],
):
    """
    Display a widget showing a list of tasks with their details and completion status.
    
    This function creates and streams a task list widget to the chat interface,
    displaying tasks with their title, description, category, priority, due dates,
    and completion status in a rich, interactive format.
    
    title (str): The header text to display at the top of the task list widget 
    tasks (list[Task]): List of Task objects to display in the widget.
    """

    print("tool called")
    try:
        widget = build_task_list_widget(title, tasks)
        print("Widget built successfully, streaming to client")

        await ctx.context.stream_widget(widget)
    except Exception as e:
        print(f'Error: {e}')
        print(e)

