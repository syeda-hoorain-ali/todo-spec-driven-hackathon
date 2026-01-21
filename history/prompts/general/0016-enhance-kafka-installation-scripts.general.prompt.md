---
id: "0016"
title: "Enhance Kafka Installation Scripts"
stage: "general"
date_iso: "2026-01-21"
model: "qwen3-code-plus"
surface: "agent"
feature: "none"
branch: "main"
user: "user"
command: "enhance kafka installation scripts"
labels: ["kafka", "installation", "docker", "automation"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
---

## Files Modified

- `.claude/skills/kafka/scripts/install-kafka.ps1`
- `.claude/skills/kafka/scripts/install-kafka.sh`
- `.claude/skills/kafka/SKILL.md`

## Summary

Enhanced the Kafka installation scripts to automatically detect environment capabilities and choose the appropriate installation method. The scripts now check for Java 17+ first, and if not available, check for Docker and run Kafka in a container as a fallback.

## Details

Updated both PowerShell and Bash installation scripts to:
1. Check for Java 17+ availability first
2. If Java not available, check for Docker availability
3. Proceed with native installation if Java is available
4. Start Kafka in Docker container if Docker is available but Java isn't
5. Show clear error message if neither is available
6. Provide appropriate usage instructions based on the installation method used

Updated the SKILL.md documentation to explain the new dual-path functionality and clarify prerequisites.

## Outcome

The installation scripts now handle environments where Java isn't available by automatically falling back to Docker-based Kafka. This provides a more robust and user-friendly installation experience.

## Evaluation

The changes successfully address the requirement to handle both Java and Docker-based installations automatically. Users no longer need to manually determine which approach to use - the scripts intelligently select the appropriate method based on available system capabilities.
