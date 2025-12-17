---
id: 1
title: Constitution and NextJS Skill Updates for Clean Code Practices
stage: constitution
date: 2025-12-12
model: qwen3-code-plus
labels: ["clean-code", "architecture", "prop-drilling", "configuration-centralization"]
---

# Constitution and NextJS Skill Updates for Clean Code Practices

## User Input

User wanted to update the constitution and Next.js skill to align with clean code practices that were implemented in the tasks feature, so that when adding new features in the future, these practices won't need to be specified again.

## Implementation Details

Updated both the project constitution and Next.js skill documentation to include clean code practices that were implemented in the tasks feature:

### Changes to Next.js Skill (`.claude/skills/nextjs/SKILL.md`):
- Added **Minimize Prop Drilling** section explaining how components should use hooks directly instead of receiving functions through props
- Added **Centralized Configurations** section explaining how to define shared configurations in central files to avoid duplication
- These practices will guide future development to follow the clean architecture implemented in the tasks feature

### Changes to Project Constitution (`.specify/memory/constitution.md`):
- Added **Clean Code Architecture Standards** section with four key principles:
  - **Minimize Prop Drilling**: Components should use hooks directly rather than receiving functions through props
  - **Centralized Configurations**: Shared configuration objects should be defined in central files to avoid duplication
  - **Component Minimalism**: Each component should have minimal necessary props
  - **Icon Naming Convention**: All Lucide React icons must use the "Icon" postfix

## Files Modified

- `.claude/skills/nextjs/SKILL.md` - Added clean code architecture patterns
- `.specify/memory/constitution.md` - Added Clean Code Architecture Standards section

## Impact

Future feature development will now follow these established clean code practices without needing to specify them again. The practices are now codified in the project's foundational documents, making them part of the standard development process.

## Follow-up Actions

None required - the changes are complete and will guide future development.
