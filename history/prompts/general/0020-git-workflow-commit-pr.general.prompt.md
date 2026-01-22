---
id: 0020
title: git-workflow-commit-pr
stage: general
date: 2026-01-22
surface: agent
model: qwen3-code-plus
feature: none
branch: update-kafka-skill
user: Claude
command: /sp.git.commit_pr
labels: [git, workflow, commit, pr]
links:
  spec: null
  ticket: null
  adr: null
  pr: https://github.com/syeda-hoorain-ali/todo-spec-driven-hackathon/pull/13
files:
  - .claude/skills/kafka/SKILL.md
  - .claude/skills/kafka/references/kafka-reference.md
  - .claude/skills/kafka/references/admin-examples.md
  - .claude/skills/kafka/references/common-patterns.md
  - .claude/skills/kafka/references/connect-examples.md
  - .claude/skills/kafka/references/consumer-examples.md
  - .claude/skills/kafka/references/installation-setup.md
  - .claude/skills/kafka/references/producer-examples.md
  - .claude/skills/kafka/references/stream-processing.md
  - .claude/skills/kafka/references/troubleshooting.md
  - .claude/skills/kafka/scripts/install-kafka.ps1
  - .claude/skills/kafka/scripts/install-kafka.sh
  - history/prompts/general/0016-enhance-kafka-installation-scripts.general.prompt.md
  - history/prompts/general/0017-add-docker-daemon-check.general.prompt.md
  - history/prompts/general/0018-update-kafka-skill-admin-privileges.general.prompt.md
  - history/prompts/general/0019-kafka-installation-fix.general.prompt.md
  - history/prompts/phase-05/001-dapr/0007-dapr-integration-complete.phr.general.prompt.md
tests:
  - git commit
  - git push
  - gh pr create
---

## Prompt

/sp.git.commit_pr

## Response snapshot

I've successfully completed the git workflow for the Kafka skill updates:

✅ Workflow executed successfully:
• Branch: update-kafka-skill
• Commit: "feat(kafka): update Kafka skill with enhanced installation and administration guides"
• PR: https://github.com/syeda-hoorain-ali/todo-spec-driven-hackathon/pull/13

The changes included enhancing the Kafka skill with comprehensive installation scripts, administration examples, consumer/producer patterns, and troubleshooting guides. The pull request has been created with a detailed description of the changes.

## Outcome

- ✅ Impact: Created feature branch, committed changes, and opened PR #13 with enhanced Kafka skill documentation and installation scripts
- 🧪 Tests: git commit, git push, gh pr creation operations successful
- 📁 Files: Updated Kafka skill files, added reference documentation, added OS-specific installation scripts, reorganized prompt files
- 🔁 Next prompts: Ready for code review and merge of PR #13
- 🧠 Reflection: Successfully automated the complete git workflow from branch creation to PR generation

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A