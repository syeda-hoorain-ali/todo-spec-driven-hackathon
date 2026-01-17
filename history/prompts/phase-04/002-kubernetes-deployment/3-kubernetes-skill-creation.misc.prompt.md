---
id: 3
title: "Kubernetes Skill Creation"
stage: "misc"
date: "2026-01-05"
surface: "agent"
model: "claude-opus-4-5-20251101"
feature: "kubernetes-deployment"
branch: "phase-04/002-kubernetes-deployment"
user: "user"
command: "manual"
labels: ["kubernetes", "skill", "deployment", "minikube", "helm"]
link:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - ".claude/skills/kubernetes-deployment/SKILL.md"
  - ".claude/skills/kubernetes-deployment/references/best-practices.md"
  - ".claude/skills/kubernetes-deployment/references/taskflow-deployment.md"
  - ".claude/skills/kubernetes-deployment/scripts/kubectl-helper.sh"
tests: []
outcome: "Successfully created comprehensive Kubernetes deployment skill for containerized applications"
evaluation: "Skill includes documentation, best practices, application-specific guidance, and helper scripts for Kubernetes deployment from beginner to advanced levels"
---

# Kubernetes Skill Creation

## PROMPT_TEXT
Using your skill creator skill create a new skill for Kubernetes. I will use it to deploy and scale containerized applications from hello world to professional production systems. Use context7 to study official documentation and then build it so no self assumed knowledge.

## RESPONSE_TEXT
Created a comprehensive Kubernetes deployment skill with the following components:
1. Main skill documentation (SKILL.md) covering deployment workflows from basic to advanced
2. Best practices reference document for Kubernetes configuration and deployment
3. Application-specific guidance for the Taskflow application
4. Helper script for common Kubernetes operations
The skill is designed for beginners to learn Kubernetes deployment and scaling of containerized applications, with specific focus on the Taskflow application with frontend, backend, and MCP server components.
