---
id: 2
title: Frontend NextJS Agent Creation
stage: tasks-frontend
date: 2025-12-12
model: qwen3-code-plus
labels: ["agent", "nextjs", "typescript", "clean-architecture", "forms"]
---

# Frontend NextJS Agent Creation

## User Input

User wanted to create a specialized frontend agent for Next.js and TypeScript development that must use nextjs & frontend-forms skills for its work and architecture, with every file ending with a new line, following clean code practices.

## Implementation Details

Created a specialized frontend agent with the following characteristics:

### Agent Configuration
- Name: `frontend-nextjs-agents`
- Description: Specialized agent for Next.js and TypeScript development with clean architecture practices
- Color: purple
- Required skills: [frontend-forms, nextjs, auth]

### Agent Capabilities
- Creates Next.js components with proper TypeScript typing
- Follows clean architecture principles with minimal prop drilling
- Uses centralized configurations
- Applies proper naming conventions (kebab-case for files, named exports for components)
- Implements form handling with ShadCN and Zod validation
- Uses proper icon naming with "Icon" postfix
- Ensures every file ends with a newline character

### Architecture Guidelines Implemented
- Minimize prop drilling by using hooks directly in components
- Centralize configurations in feature-specific config files
- Use named exports for all components (arrow functions)
- Organize components in feature-based folder structures
- Use kebab-case for file names
- Import Lucide React icons with "Icon" postfix

### File Formatting Requirements
- Every file must end with a newline character
- Proper indentation and spacing
- Consistent TypeScript interfaces and types

## Files Modified

- `.claude/agents/frontend-nextjs-agents.md` - Created the specialized agent with all required configurations and guidelines

## Impact

The agent is now ready to be used for Next.js and TypeScript development with all clean code practices established. It enforces proper architecture patterns, clean code principles, and ensures consistent file formatting with newlines at the end of files.

## Follow-up Actions

None required - the agent is complete and ready for use in future development tasks.
