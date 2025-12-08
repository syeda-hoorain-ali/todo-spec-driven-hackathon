"""
CLI Interface for the todo application.

This module handles command-line argument parsing and execution.
"""
import argparse
import sys
from datetime import datetime
from todo_app.managers.task_manager import TaskManager
from todo_app.ui.renderer import Renderer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich import box
import questionary


class CLIInterface:
    """
    Handles command-line interface for the todo application.
    Parses commands and coordinates with TaskManager and Renderer.
    """

    def __init__(self):
        self.task_manager = TaskManager()
        self.renderer = Renderer()

    def _create_parser(self):
        """Create and configure the argument parser."""
        parser = argparse.ArgumentParser(
            prog='todo',
            description='A Python console todo application',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""Examples:
  todo add "Buy groceries"
  todo list --status pending
  todo complete 1
  todo search "project"
  todo update 1 "Updated title" --priority high
"""
        )

        subparsers = parser.add_subparsers(dest='command', help='Available commands')

        # Add command
        add_parser = subparsers.add_parser('add', help='Add a new task')
        add_parser.add_argument('title', help='Task title (max 200 chars)')
        add_parser.add_argument('description', nargs='?', default='', help='Task description (max 1000 chars)')
        add_parser.add_argument('--priority', choices=['low', 'medium', 'high'], default='medium',
                               help='Task priority (default: medium)')
        add_parser.add_argument('--due-date', help='Due date in YYYY-MM-DD format')
        add_parser.add_argument('--tags', help='Comma-separated list of tags (max 10 tags, max 50 chars each)')

        # List command
        list_parser = subparsers.add_parser('list', help='List all tasks')
        list_parser.add_argument('--status', choices=['pending', 'in-progress', 'complete'],
                                help='Filter by status')
        list_parser.add_argument('--priority', choices=['low', 'medium', 'high'],
                                help='Filter by priority')
        list_parser.add_argument('--sort', choices=['date', 'priority', 'title', 'due_date', 'status'],
                                default='date', help='Sort by criteria (default: date)')
        list_parser.add_argument('--reverse', action='store_true', help='Reverse sort order')
        list_parser.add_argument('--all', action='store_true', help='Show all tasks (including completed)')

        # Complete command
        complete_parser = subparsers.add_parser('complete', help='Mark a task as complete')
        complete_parser.add_argument('task_id', type=int, help='ID of the task to mark complete')

        # Incomplete command
        incomplete_parser = subparsers.add_parser('incomplete', help='Mark a task as incomplete')
        incomplete_parser.add_argument('task_id', type=int, help='ID of the task to mark incomplete')

        # Delete command
        delete_parser = subparsers.add_parser('delete', help='Delete a task')
        delete_parser.add_argument('task_id', type=int, help='ID of the task to delete')

        # Update command
        update_parser = subparsers.add_parser('update', help='Update a task')
        update_parser.add_argument('task_id', type=int, help='ID of the task to update')
        update_parser.add_argument('title', nargs='?', help='New task title (max 200 chars)')
        update_parser.add_argument('description', nargs='?', help='New task description (max 1000 chars)')
        update_parser.add_argument('--priority', choices=['low', 'medium', 'high'],
                                  help='New priority')
        update_parser.add_argument('--due-date', help='New due date in YYYY-MM-DD format')
        update_parser.add_argument('--status', choices=['pending', 'in-progress', 'complete'],
                                  help='New status')
        update_parser.add_argument('--tags', help='New comma-separated list of tags')

        # Search command
        search_parser = subparsers.add_parser('search', help='Search tasks by keyword')
        search_parser.add_argument('keyword', help='Search keyword')
        search_parser.add_argument('--case-sensitive', action='store_true',
                                  help='Perform case-sensitive search (default: case-insensitive)')

        # Help command (using default help from argparse)
        subparsers.add_parser('help', help='Show help information')

        return parser

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string in YYYY-MM-DD format."""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Date format must be YYYY-MM-DD, got: {date_str}")

    def _parse_tags(self, tags_str: str) -> list:
        """Parse comma-separated tags string."""
        if not tags_str:
            return []
        return [tag.strip() for tag in tags_str.split(',') if tag.strip()]

    def run(self):
        """Parse arguments and execute the appropriate command."""
        parser = self._create_parser()
        args = parser.parse_args()

        if not args.command:
            parser.print_help()
            sys.exit(0)

        try:
            if args.command == 'add':
                self._handle_add(args)
            elif args.command == 'list':
                self._handle_list(args)
            elif args.command == 'complete':
                self._handle_complete(args)
            elif args.command == 'incomplete':
                self._handle_incomplete(args)
            elif args.command == 'delete':
                self._handle_delete(args)
            elif args.command == 'update':
                self._handle_update(args)
            elif args.command == 'search':
                self._handle_search(args)
            elif args.command == 'help':
                parser.print_help()
                sys.exit(0)
            else:
                parser.print_help()
                sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError as e:
            print(f"Error: File not found - {e}", file=sys.stderr)
            sys.exit(3)
        except PermissionError as e:
            print(f"Error: Permission denied - {e}", file=sys.stderr)
            sys.exit(4)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.", file=sys.stderr)
            sys.exit(130)  # Standard exit code for Ctrl+C
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            sys.exit(2)

    def run_interactive(self):
        """Run the application in interactive mode with Rich UI."""
        console = Console(force_terminal=True)
        console.print(Panel("[bold blue]Todo App Interactive Mode[/bold blue]", expand=False))
        console.print("[italic]Type 'help' for commands, 'exit' or 'quit' to quit[/italic]")
        console.print("")  # Use empty print instead of rule() to avoid Unicode issues on Windows

        while True:
            try:
                # Use Rich prompt for better input experience
                user_input = Prompt.ask("[bold green]todo>[/bold green]", default="").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit']:
                    console.print("[bold red]Goodbye![/bold red]")
                    break

                if user_input.lower() == 'help':
                    self._show_interactive_help_rich()
                    continue

                # Enhanced command handling with Rich UI
                if user_input.lower() == 'add':
                    self._handle_interactive_add_form(console)
                    continue
                elif user_input.lower() == 'list':
                    self._handle_interactive_list(console)
                    continue
                elif user_input.lower() == 'complete':
                    # If user just types 'complete', use task selection
                    self._handle_interactive_complete(console)
                    continue
                elif user_input.lower().startswith('complete '):
                    # If user provides a task ID, use that
                    try:
                        task_id = int(user_input[9:].strip())
                        self._handle_interactive_complete(console, task_id)
                    except ValueError:
                        console.print("[red]Error: Please provide a valid task ID[/red]")
                    continue
                elif user_input.lower() == 'incomplete':
                    # If user just types 'incomplete', use task selection
                    self._handle_interactive_incomplete(console)
                    continue
                elif user_input.lower().startswith('incomplete '):
                    # If user provides a task ID, use that
                    try:
                        task_id = int(user_input[11:].strip())
                        self._handle_interactive_incomplete(console, task_id)
                    except ValueError:
                        console.print("[red]Error: Please provide a valid task ID[/red]")
                    continue
                elif user_input.lower() == 'delete':
                    # If user just types 'delete', use task selection
                    self._handle_interactive_delete(console)
                    continue
                elif user_input.lower().startswith('delete '):
                    # If user provides a task ID, use that
                    try:
                        task_id = int(user_input[7:].strip())
                        self._handle_interactive_delete(console, task_id)
                    except ValueError:
                        console.print("[red]Error: Please provide a valid task ID[/red]")
                    continue
                elif user_input.lower() == 'search':
                    self._handle_interactive_search_form(console)
                    continue
                elif user_input.lower() == 'update':
                    # If user just types 'update', use task selection
                    self._handle_interactive_update(console)
                    continue
                elif user_input.lower().startswith('update '):
                    # Parse update command manually for better UX
                    self._handle_interactive_update(console, user_input[7:].strip())
                    continue
                elif user_input.lower() == 'clear':
                    # Clear the terminal screen
                    self._handle_interactive_clear(console)
                    continue

                # Fallback to original parsing for complex commands
                try:
                    import shlex
                    args_list = shlex.split(user_input)

                    parser = self._create_parser()
                    if not args_list:
                        continue

                    args = parser.parse_args(args_list)

                    # Execute the command
                    if args.command == 'add':
                        self._handle_add(args)
                    elif args.command == 'list':
                        self._handle_list(args)
                    elif args.command == 'complete':
                        self._handle_complete(args)
                    elif args.command == 'incomplete':
                        self._handle_incomplete(args)
                    elif args.command == 'delete':
                        self._handle_delete(args)
                    elif args.command == 'update':
                        self._handle_update(args)
                    elif args.command == 'search':
                        self._handle_search(args)
                    elif args.command == 'help':
                        parser.print_help()
                    else:
                        parser.print_help()

                except SystemExit:
                    # argparse calls sys.exit when there are parsing errors,
                    # we want to continue the interactive session
                    pass
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")

            except KeyboardInterrupt:
                console.print("\n[bold red]Goodbye![/bold red]")
                break
            except EOFError:
                console.print("\n[bold red]Goodbye![/bold red]")
                break

    def _handle_interactive_add_form(self, console):
        """Handle add command with form-like prompts."""
        try:
            console.print("\n[bold]Adding New Task[/bold]")
            console.print("[dim]Press Enter to skip optional fields[/dim]")

            # Get title
            title = Prompt.ask("[bold]Title[/bold] (required)")
            if not title.strip():
                console.print("[red]Error: Title is required[/red]")
                return

            # Get description
            description = Prompt.ask("[bold]Description[/bold] (optional)")

            # Get priority
            priority = Prompt.ask(
                "[bold]Priority[/bold]",
                choices=["low", "medium", "high"],
                default="medium"
            )

            # Get due date
            due_date_str = Prompt.ask("[bold]Due Date[/bold] (YYYY-MM-DD, optional)")
            due_date = None
            if due_date_str.strip():
                try:
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                except ValueError:
                    console.print(f"[red]Error: Invalid date format. Use YYYY-MM-DD[/red]")
                    return

            # Get tags
            tags_str = Prompt.ask("[bold]Tags[/bold] (comma-separated, optional)")
            tags = []
            if tags_str.strip():
                tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]

            # Create the task
            task = self.task_manager.create_task(
                title=title.strip(),
                description=description.strip(),
                priority=priority,
                due_date=due_date,
                tags=tags
            )

            console.print(f"\n[green]Task #{task.id} added successfully:[/green]")
            console.print(f"  - Title: {task.title}")
            console.print(f"  - Description: {task.description}")
            console.print(f"  - Status: {task.status}")
            console.print(f"  - Priority: [bold]{task.priority}[/bold]")
            console.print(f"  - Due Date: {task.due_date.strftime('%Y-%m-%d') if task.due_date else 'None'}")
            console.print(f"  - Tags: {', '.join(task.tags) if task.tags else 'None'}")
            console.print(f"  - Created: {task.created_date.strftime('%Y-%m-%d')}")

        except KeyboardInterrupt:
            console.print("\n[italic]Add task cancelled[/italic]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    def _handle_interactive_add(self, console, args_str):
        """Handle add command with Rich UI."""
        import shlex
        try:
            args = shlex.split(args_str)
            if not args:
                console.print("[red]Error: Please provide at least a task title[/red]")
                return

            title = args[0]
            description = args[1] if len(args) > 1 else ""

            # Use Rich prompts for additional options
            priority = Prompt.ask(
                "Select priority:",
                choices=["low", "medium", "high"],
                default="medium"
            )

            # Create the task
            task = self.task_manager.create_task(
                title=title,
                description=description,
                priority=priority
            )

            console.print(f"[green]Task #{task.id} added successfully:[/green]")
            console.print(f"  - Title: {task.title}")
            console.print(f"  - Status: {task.status}")
            console.print(f"  - Priority: [bold]{task.priority}[/bold]")
            console.print(f"  - Created: {task.created_date.strftime('%Y-%m-%d')}")

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    def _handle_interactive_list(self, console):
        """Handle list command with Rich UI."""
        tasks = self.task_manager.get_all_tasks()
        if not tasks:
            console.print("[italic]No tasks found.[/italic]")
            return

        # Use the existing renderer but with Rich console
        self.renderer.display_tasks(tasks, show_all=True)


    def _select_task_interactive(self, console, prompt_text="Select a task:"):
        """Display a table of tasks and allow user to select one using questionary."""
        tasks = self.task_manager.get_all_tasks()
        if not tasks:
            console.print("[italic]No tasks available.[/italic]")
            return None

        # Create a table with task information
        table = Table(title="Available Tasks", box=box.ROUNDED, show_lines=True)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Priority", style="yellow")
        table.add_column("Due Date", style="blue")
        table.add_column("Tags", style="white")

        for task in tasks:
            status_style = "red" if task.status == "pending" else "green" if task.status == "complete" else "yellow"
            priority_style = "red" if task.priority == "high" else "yellow" if task.priority == "medium" else "blue"

            table.add_row(
                str(task.id),
                task.title,
                f"[{status_style}]{task.status}[/]",
                f"[{priority_style}]{task.priority}[/]",
                str(task.due_date.strftime('%Y-%m-%d') if task.due_date else 'None'),
                ', '.join(task.tags) if task.tags else 'None'
            )

        console.print(table)

        # Create choices for questionary
        choices = []
        for task in tasks:
            status_style = "red" if task.status == "pending" else "green" if task.status == "complete" else "yellow"
            priority_style = "red" if task.priority == "high" else "yellow" if task.priority == "medium" else "blue"

            choice_name = f"ID: {task.id} | {task.title} | Status: {task.status} | Priority: {task.priority}"
            choices.append(questionary.Choice(title=choice_name, value=task))

        # Ask user to select a task using questionary
        try:
            result = questionary.select(
                prompt_text,
                choices=choices
            ).ask()

            return result
        except KeyboardInterrupt:
            console.print("\n[italic]Selection cancelled[/italic]")
            return None
        except Exception:
            console.print("[red]Selection cancelled.[/red]")
            return None

    def _handle_interactive_complete(self, console, task_id=None):
        """Handle complete command with Rich UI."""
        # If no task_id provided, ask user to select a task
        if task_id is None:
            task = self._select_task_interactive(console, "Select a task to mark as complete:")
            if not task:
                return
            task_id = task.id

        task = self.task_manager.mark_complete(task_id)
        if task:
            console.print(f"[green]✓ Task #{task.id} marked as complete[/green]")
        else:
            console.print(f"[red]Error: Task with ID {task_id} not found[/red]")

    def _handle_interactive_incomplete(self, console, task_id=None):
        """Handle incomplete command with Rich UI."""
        # If no task_id provided, ask user to select a task
        if task_id is None:
            task = self._select_task_interactive(console, "Select a task to mark as pending:")
            if not task:
                return
            task_id = task.id

        task = self.task_manager.mark_incomplete(task_id)
        if task:
            console.print(f"[green]✓ Task #{task.id} marked as pending[/green]")
        else:
            console.print(f"[red]Error: Task with ID {task_id} not found[/red]")

    def _handle_interactive_delete(self, console, task_id=None):
        """Handle delete command with Rich UI."""
        # If no task_id provided, ask user to select a task
        if task_id is None:
            task = self._select_task_interactive(console, "Select a task to delete:")
            if not task:
                return
            task_id = task.id

        success = self.task_manager.delete_task(task_id)
        if success:
            console.print(f"[green]✓ Task #{task_id} deleted successfully[/green]")
        else:
            console.print(f"[red]Error: Task with ID {task_id} not found[/red]")

    def _handle_interactive_search_form(self, console):
        """Handle search command with form-like prompts."""
        try:
            console.print("\n[bold]Search Tasks[/bold]")

            # Get search keyword
            keyword = Prompt.ask("[bold]Search keyword[/bold] (case-insensitive)")
            if not keyword.strip():
                console.print("[red]Error: Search keyword is required[/red]")
                return

            # Perform the search (case-insensitive by default)
            tasks = self.task_manager.search_tasks(keyword.strip())

            if not tasks:
                console.print(f"\n[italic]No tasks found matching '{keyword.strip()}'.[/italic]")
                return

            console.print(f"\n[bold]SEARCH RESULTS FOR '{keyword.strip()}'[/bold] ([italic]case-insensitive[/italic])")
            self.renderer.display_search_results(tasks, keyword.strip())

        except KeyboardInterrupt:
            console.print("\n[italic]Search cancelled[/italic]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    def _handle_interactive_search(self, console, keyword):
        """Handle search command with Rich UI."""
        tasks = self.task_manager.search_tasks(keyword)
        if not tasks:
            console.print(f"[italic]No tasks found matching '{keyword}'.[/italic]")
            return

        console.print(f"[bold]SEARCH RESULTS FOR '{keyword}'[/bold]")
        self.renderer.display_search_results(tasks, keyword)

    def _handle_interactive_update(self, console, args_str=""):
        """Handle update command with Rich UI."""
        import shlex
        try:
            args = shlex.split(args_str) if args_str else []

            # If no arguments provided, ask user to select a task first
            if not args:
                task = self._select_task_interactive(console, "Select a task to update:")
                if not task:
                    return
                task_id = task.id
            else:
                try:
                    task_id = int(args[0])
                except ValueError:
                    console.print("[red]Error: Please provide a valid task ID[/red]")
                    return

            # Get the task to update
            task = self.task_manager.get_task(task_id)
            if not task:
                console.print(f"[red]Error: Task with ID {task_id} not found[/red]")
                return

            # Use Rich prompts to get update values
            console.print(f"\n[bold]Updating Task #{task.id}[/bold]")
            title = Prompt.ask(f"Title [cyan][default: {task.title}][/cyan]", default=task.title)
            description = Prompt.ask(f"Description [cyan][default: {task.description}][/cyan]", default=task.description)

            # Get priority with validation
            priority = Prompt.ask(
                f"Priority [cyan][low/medium/high, default: {task.priority}][/cyan]",
                choices=["low", "medium", "high"],
                default=task.priority
            )

            # Get due date with validation
            due_date_default = task.due_date.strftime('%Y-%m-%d') if task.due_date else 'none'
            due_date_input = Prompt.ask(f"Due date [cyan][YYYY-MM-DD or 'none' to remove, default: {due_date_default}][/cyan]",
                                      default=due_date_default)
            due_date = None
            if due_date_input and due_date_input != "none":
                try:
                    due_date = datetime.strptime(due_date_input, '%Y-%m-%d')
                except ValueError:
                    console.print(f"[red]Error: Invalid date format. Using existing due date.[/red]")
                    due_date = task.due_date

            # Get tags
            tags_default = ', '.join(task.tags) if task.tags else 'none'
            tags_input = Prompt.ask(f"Tags [cyan][comma-separated or 'none' to remove, default: {tags_default}][/cyan]",
                                  default=tags_default)
            tags = []
            if tags_input and tags_input != "none":
                tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]

            # Update the task
            updated_task = self.task_manager.update_task(
                task_id,
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                tags=tags
            )

            if updated_task:
                console.print(f"\n[green]Task #{updated_task.id} updated successfully:[/green]")
                console.print(f"  - Title: {updated_task.title}")
                console.print(f"  - Description: {updated_task.description}")
                console.print(f"  - Priority: [bold]{updated_task.priority}[/bold]")
                console.print(f"  - Due Date: {updated_task.due_date.strftime('%Y-%m-%d') if updated_task.due_date else 'None'}")
                console.print(f"  - Tags: {', '.join(updated_task.tags) if updated_task.tags else 'None'}")
            else:
                console.print(f"[red]Error: Failed to update task {task_id}[/red]")

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    def _handle_interactive_clear(self, console):
        """Clear the terminal screen without losing application state."""
        import os
        # Clear the screen based on the operating system
        os.system('cls' if os.name == 'nt' else 'clear')
        # Print the header again to maintain context
        console.print(Panel("[bold blue]Todo App Interactive Mode[/bold blue]", expand=False))
        console.print("[italic]Type 'help' for commands, 'exit' or 'quit' to quit[/italic]")
        console.print("")

    def _show_interactive_help_rich(self):
        """Show help for interactive mode with Rich formatting."""
        console = Console(force_terminal=True)
        console.print(Panel("[bold]Available Commands[/bold]", expand=False))

        help_table = Table.grid(padding=(0, 2))
        help_table.add_column(style="bold cyan")
        help_table.add_column(style="white")

        help_table.add_row("add", "Add a new task using form prompts")
        help_table.add_row("list", "List all tasks")
        help_table.add_row("complete [id]", "Mark a task as complete (with or without ID)")
        help_table.add_row("incomplete [id]", "Mark a task as pending (with or without ID)")
        help_table.add_row("delete [id]", "Delete a task (with or without ID)")
        help_table.add_row("update [id]", "Update a task with prompts (with or without ID)")
        help_table.add_row("search", "Search tasks by keyword using form prompts")
        help_table.add_row("clear", "Clear the terminal screen")
        help_table.add_row("help", "Show this help message")
        help_table.add_row("exit/quit", "Exit interactive mode")

        console.print(help_table)

        console.print("\n[bold]Examples:[/bold]")
        examples_table = Table.grid(padding=(0, 2))
        examples_table.add_column(style="italic")
        examples_table.add_column(style="white")

        examples_table.add_row("add", "Add a task using form prompts (title, priority, due date, tags)")
        examples_table.add_row("list", "Show all tasks")
        examples_table.add_row("search", "Search for tasks using form prompts")
        examples_table.add_row("clear", "Clear the terminal screen")
        examples_table.add_row("complete", "Select and mark a task as complete")
        examples_table.add_row("complete 1", "Mark task #1 as complete")

        console.print(examples_table)

    def _show_interactive_help(self):
        """Show help for interactive mode."""
        print("Available commands:")
        print("  add <title> [description] [--priority low|medium|high] [--due-date YYYY-MM-DD] [--tags tag1,tag2]")
        print("  list [--status pending|in-progress|complete] [--priority low|medium|high] [--sort date|priority|title|due_date|status] [--reverse] [--all]")
        print("  complete <task_id>")
        print("  incomplete <task_id>")
        print("  delete <task_id>")
        print("  update <task_id> [title] [description] [--priority low|medium|high] [--due-date YYYY-MM-DD] [--status pending|in-progress|complete] [--tags tag1,tag2]")
        print("  search <keyword> [--case-sensitive]")
        print("  help")
        print("  exit/quit")
        print("")
        print("Examples:")
        print("  add \"Buy groceries\"")
        print("  add \"Project work\" --priority high --tags work,important")
        print("  list --status pending")
        print("  complete 1")
        print("  search \"groceries\"")

    def _handle_add(self, args):
        """Handle the add command."""
        # Parse due date if provided
        due_date = None
        if args.due_date:
            due_date = self._parse_date(args.due_date)

        # Parse tags if provided
        tags = self._parse_tags(args.tags) if args.tags else []

        # Create the task
        task = self.task_manager.create_task(
            title=args.title,
            description=args.description,
            priority=args.priority,
            due_date=due_date,
            tags=tags
        )

        # Display success message
        self.renderer.display_task_added(task)

    def _handle_list(self, args):
        """Handle the list command."""
        # Build filters
        filters = {}
        if args.status:
            filters['status'] = args.status
        elif not args.all:
            # By default, don't show completed tasks
            filters['status'] = 'pending'

        if args.priority:
            filters['priority'] = args.priority

        # Get tasks based on filters
        tasks = self.task_manager.get_all_tasks()

        # Apply filters
        if 'status' in filters:
            if filters['status'] == 'pending':
                # Show pending and in-progress tasks, but not complete unless --all is specified
                if not args.all:
                    tasks = [t for t in tasks if t.status in ['pending', 'in-progress']]
                else:
                    tasks = [t for t in tasks if t.status == 'pending']
            elif filters['status'] == 'in-progress':
                tasks = [t for t in tasks if t.status == 'in-progress']
            elif filters['status'] == 'complete':
                tasks = [t for t in tasks if t.status == 'complete']
        elif not args.all:
            # Default behavior: show pending and in-progress tasks
            tasks = [t for t in tasks if t.status in ['pending', 'in-progress']]

        if 'priority' in filters:
            tasks = [t for t in tasks if t.priority == filters['priority']]

        # Sort tasks
        tasks = self.task_manager.sort_tasks(tasks, args.sort, args.reverse)

        # Display tasks
        self.renderer.display_tasks(tasks, args.all)

    def _handle_complete(self, args):
        """Handle the complete command."""
        task = self.task_manager.mark_complete(args.task_id)
        if task:
            self.renderer.display_task_status_updated(task, "complete")
        else:
            print(f"Error: Task with ID {args.task_id} not found", file=sys.stderr)
            sys.exit(1)

    def _handle_incomplete(self, args):
        """Handle the incomplete command."""
        task = self.task_manager.mark_incomplete(args.task_id)
        if task:
            self.renderer.display_task_status_updated(task, "pending")
        else:
            print(f"Error: Task with ID {args.task_id} not found", file=sys.stderr)
            sys.exit(1)

    def _handle_delete(self, args):
        """Handle the delete command."""
        success = self.task_manager.delete_task(args.task_id)
        if success:
            self.renderer.display_task_deleted(args.task_id)
        else:
            print(f"Error: Task with ID {args.task_id} not found", file=sys.stderr)
            sys.exit(1)

    def _handle_update(self, args):
        """Handle the update command."""
        updates = {}
        if args.title is not None:
            updates['title'] = args.title
        if args.description is not None:
            updates['description'] = args.description
        if args.priority:
            updates['priority'] = args.priority
        if args.due_date:
            updates['due_date'] = self._parse_date(args.due_date)
        if args.status:
            updates['status'] = args.status
        if args.tags is not None:
            updates['tags'] = self._parse_tags(args.tags)

        task = self.task_manager.update_task(args.task_id, **updates)
        if task:
            self.renderer.display_task_updated(task)
        else:
            print(f"Error: Task with ID {args.task_id} not found", file=sys.stderr)
            sys.exit(1)

    def _handle_search(self, args):
        """Handle the search command."""
        # For case-sensitive search, we'll handle it in the search method
        # For now, just do a basic search
        tasks = self.task_manager.search_tasks(args.keyword)

        # Display search results
        self.renderer.display_search_results(tasks, args.keyword)