"""
Renderer for the todo application.

This module uses Rich to format and display tasks in the terminal.
"""
from datetime import datetime
from typing import List
from rich.console import Console
from rich.table import Table
from rich.text import Text
from todo_app.models.task import Task


class Renderer:
    """
    Renders tasks and other information using Rich for beautiful terminal output.
    """
    def __init__(self):
        self.console = Console(force_terminal=True)

    def display_tasks(self, tasks: List[Task], show_all: bool = False):
        """Display a list of tasks in a formatted table."""
        if not tasks:
            self.console.print("[italic]No tasks found.[/italic]")
            return

        table = Table(title="TODO LIST")
        table.add_column("ID", style="dim", width=4)
        table.add_column("Title", style="bold", min_width=20)
        table.add_column("Status", justify="center")
        table.add_column("Priority", style="dim")
        table.add_column("Tags", style="dim")
        table.add_column("Recurrence", style="dim")
        table.add_column("Due", style="dim")

        for task in tasks:
            # Format status with visual indicator
            if task.status == "complete":
                status_text = "X"
                title_style = "dim strike"
            elif task.status == "in-progress":
                status_text = ">"
                title_style = "bold yellow"
            else:  # pending
                status_text = "O"
                title_style = "bold"

            # Format due date
            if task.due_date:
                due_text = task.due_date.strftime("%m/%d") if task.due_date else "-"
            else:
                due_text = "-"

            # Format priority with color
            if task.priority == "high":
                priority_text = f"[red]{task.priority}[/red]"
            elif task.priority == "medium":
                priority_text = f"[yellow]{task.priority}[/yellow]"
            else:  # low
                priority_text = f"[green]{task.priority}[/green]"

            # Format tags
            if task.tags:
                tags_text = ", ".join(task.tags)
            else:
                tags_text = "-"

            # Format recurrence
            recurrence_text = task.recurrence_pattern if task.recurrence_pattern != "none" else "-"

            table.add_row(
                str(task.id),
                Text(task.title, style=title_style),
                status_text,
                priority_text,
                tags_text,
                recurrence_text,
                due_text
            )

        self.console.print(table)

    def display_task_added(self, task: Task):
        """Display a success message when a task is added."""
        self.console.print(f"[green]Task #{task.id} added successfully:[/green]")
        self.console.print(f"- Title: {task.title}")
        self.console.print(f"- Status: {task.status}")
        self.console.print(f"- Priority: {task.priority}")
        self.console.print(f"- Created: {task.created_date.strftime('%Y-%m-%d')}")

    def display_task_status_updated(self, task: Task, new_status: str):
        """Display a success message when a task status is updated."""
        status_text = "complete" if new_status == "complete" else "pending"
        self.console.print(f"[green]Task #{task.id} marked as {status_text}[/green]")

    def display_task_deleted(self, task_id: int):
        """Display a success message when a task is deleted."""
        self.console.print(f"[green]Task #{task_id} deleted successfully[/green]")

    def display_task_updated(self, task: Task):
        """Display a success message when a task is updated."""
        self.console.print(f"[green]Task #{task.id} updated successfully:[/green]")
        self.console.print(f"- Title: {task.title}")
        if task.priority:
            priority_color = {"high": "red", "medium": "yellow", "low": "green"}[task.priority]
            self.console.print(f"- Priority: [{priority_color}]{task.priority}[/{priority_color}]")
        if task.due_date:
            self.console.print(f"- Due: {task.due_date.strftime('%Y-%m-%d')}")

    def display_search_results(self, tasks: List[Task], keyword: str):
        """Display search results in a formatted table."""
        if not tasks:
            self.console.print(f"[italic]No tasks found matching '{keyword}'.[/italic]")
            return

        self.console.print(f"[bold]SEARCH RESULTS FOR '{keyword}'[/bold]")
        table = Table()
        table.add_column("ID", style="dim", width=4)
        table.add_column("Title", style="bold", min_width=20)
        table.add_column("Status", justify="center")
        table.add_column("Priority", style="dim")
        table.add_column("Tags", style="dim")
        table.add_column("Due", style="dim")

        for task in tasks:
            # Format status with visual indicator
            if task.status == "complete":
                status_text = "X"
                title_style = "dim strike"
            elif task.status == "in-progress":
                status_text = ">"
                title_style = "bold yellow"
            else:  # pending
                status_text = "O"
                title_style = "bold"

            # Format due date
            if task.due_date:
                due_text = task.due_date.strftime("%m/%d") if task.due_date else "-"
            else:
                due_text = "-"

            # Format priority with color
            if task.priority == "high":
                priority_text = f"[red]{task.priority}[/red]"
            elif task.priority == "medium":
                priority_text = f"[yellow]{task.priority}[/yellow]"
            else:  # low
                priority_text = f"[green]{task.priority}[/green]"

            # Format tags
            if task.tags:
                tags_text = ", ".join(task.tags)
            else:
                tags_text = "-"

            # Format recurrence
            recurrence_text = task.recurrence_pattern if task.recurrence_pattern != "none" else "-"

            table.add_row(
                str(task.id),
                Text(task.title, style=title_style),
                status_text,
                priority_text,
                tags_text,
                recurrence_text,
                due_text
            )

        self.console.print(table)

    def display_error(self, message: str):
        """Display an error message."""
        self.console.print(f"[red]Error: {message}[/red]")