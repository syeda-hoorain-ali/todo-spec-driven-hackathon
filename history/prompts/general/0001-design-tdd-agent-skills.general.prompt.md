---
id: 0001
title: Design TDD Agent and Skills for Todo Hackathon
stage: plan
date: 2025-12-07
surface: agent
model: qwen3-code-plus
feature: none
branch: main
user: user
command: "various commands to design TDD agent and skills for hackathon"
labels: ["tdd", "skills", "subagents", "hackathon", "todo-app", "testing"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - \skills-and-subagents.md
 - \.claude\agents\tdd-agent.md
tests:
 - tests for todo operations (to be implemented)
---

## Prompt

The user asked for information about the hackathon from the Todo Spec-Driven Development.pdf file, then wanted to know which skills and subagents to create. After detailing those, the user wanted to know which skills and subagents are important for Phase 1 specifically. Finally, the user decided to prioritize a TDD approach for the Python backend and requested creation of a TDD agent.

## Response snapshot

I analyzed the hackathon requirements and identified key skills and subagents needed for the project. For Phase 1, I prioritized:
1. Testing Subagent (TDD-focused) - Highest priority for TDD approach
2. Specification Generator Subagent - For spec-driven development
3. Todo Management Skill - Core functionality developed with TDD

I created two files:
1. \skills-and-subagents.md - Comprehensive list of all skills and subagents for the hackathon
2. \.claude\agents\tdd-agent.md - Detailed specification for the TDD agent focused on Python backend testing

The TDD agent includes functionality for generating tests for all required todo operations (Add, Delete, Update, View, Mark Complete), implementing proper TDD workflow (Red-Green-Refactor), and ensuring proper test coverage. It follows TDD principles with test-first approach and includes configuration options and usage commands.

## Outcome

- ✅ Impact: Created foundational tools for TDD-based development of the todo application
- 🧪 Tests: Designed test structures for all 5 basic todo operations (Add, Delete, Update, View, Mark Complete)
- 📁 Files: Created two specification documents for future implementation of TDD agent and other skills/subagents
- 🔁 Next prompts: Implementation of the TDD agent and other specified skills/subagents
- 🧠 Reflection: Prioritizing TDD early in the project will establish good testing practices for all subsequent phases of the hackathon

## Evaluation notes (flywheel)

- Failure modes observed: None at design stage
- Graders run and results (PASS/FAIL): Not applicable at design stage
- Prompt variant (if applicable): Not applicable
- Next experiment (smallest change to try): Begin implementation of the TDD agent based on the specification
