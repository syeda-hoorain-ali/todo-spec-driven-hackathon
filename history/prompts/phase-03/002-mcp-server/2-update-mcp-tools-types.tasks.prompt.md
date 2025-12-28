---
id: 2
title: "Update MCP Tools to Use Exact Types"
stage: "tasks"
date: "2025-12-28"
model: "qwen3-code-plus"
feature: "002-mcp-server"
branch: "phase-03/002-mcp-server"
user: "user"
command: "update mcp tools to use exact types"
labels: ["mcp-server", "typing", "tools", "improvement"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - "phase-03/mcp_server/src/mcp_server/main.py"
tests: []
---

# Update MCP Tools to Use Exact Types

## Prompt Text

use exact type in mcp tools instead of dict

## Response Text

Updated the MCP tools in main.py to use exact types instead of Dict[str, Any]. The changes included:

1. Changed `add_task` tool to accept `AddTaskRequest` directly instead of Dict[str, Any]
2. Changed `list_tasks` tool to accept `ListTasksRequest` directly instead of Dict[str, Any]
3. Changed `complete_task` tool to accept `CompleteTaskRequest` directly instead of Dict[str, Any]
4. Changed `delete_task` tool to accept `DeleteTaskRequest` directly instead of Dict[str, Any]
5. Changed `update_task` tool to accept `UpdateTaskRequest` directly instead of Dict[str, Any]

This improvement provides better type safety, reduces runtime errors, and makes the code more maintainable by using the exact Pydantic models that were already defined for each operation instead of generic dictionaries.

## Outcome

The MCP server tools now use proper type annotations with specific request models instead of generic dictionaries, improving code quality and maintainability.

## Evaluation

The changes were successfully implemented and all existing tests continue to pass, confirming that the functionality remains intact while improving type safety.