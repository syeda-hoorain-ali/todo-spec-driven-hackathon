#!/usr/bin/env python3
"""
Todo App - A Python console todo application with in-memory storage
"""
import sys
from todo_app.cli.cli_interface import CLIInterface


def main():
    """Main entry point for the todo application."""
    cli = CLIInterface()

    # Check if running in interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == 'interactive':
        cli.run_interactive()
    else:
        try:
            cli.run()
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(2)


if __name__ == "__main__":
    main()