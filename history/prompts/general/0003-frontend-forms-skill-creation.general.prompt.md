---
id: 0003
title: Frontend Forms Skill Creation
stage: general
date: 2025-12-10
surface: agent
model: qwen3-code-plus
feature: none
branch: 001-auth-system
user: d
command: "create skill for frontend forms"
labels: [skill, forms, shadcn, react-hook-form, zod, auth]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/frontend-forms/SKILL.md
tests: []
---
## Prompt

Create a skill file for frontend form patterns that follows the same structure as authentication forms, using shadcn Form components, react-hook-form, and Zod validation. The skill should document the pattern used in sign-in, sign-up, and other forms that integrate with feature hooks like useAuth, useTasks, etc.

## Response snapshot

Created a comprehensive skill file at .claude/skills/frontend-forms/SKILL.md that documents the form pattern including:

1. Required imports for shadcn Form components
2. Basic form structure with Card wrapper
3. Integration pattern with feature hooks (useAuth, useTasks, etc.)
4. Loading state handling from mutations
5. Form validation with Zod schemas
6. File organization and naming conventions
7. Accessibility and testing guidelines

The skill documents the pattern where forms use:
- shadcn Form components (Form, FormField, FormItem, FormLabel, FormControl, FormMessage)
- react-hook-form for form state management
- Zod for validation schemas
- Feature hooks (like useAuth) for API interactions
- Loading states from mutation hooks

## Outcome

- ✅ Impact: Created reusable skill documentation for consistent form patterns across the application
- 🧪 Tests: No tests needed as this is a documentation skill
- 📁 Files: Created .claude/skills/frontend-forms/SKILL.md with comprehensive form patterns
- 🔁 Next prompts: Can reference this skill when creating new forms
- 🧠 Reflection: The skill consolidates the form patterns used in auth components into a reusable guide

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Not applicable
- Prompt variant (if applicable): Not applicable
- Next experiment (smallest change to try): Could expand with more form field types or examples
