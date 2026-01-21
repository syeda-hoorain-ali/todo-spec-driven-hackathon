---
id: "0017"
title: "Add Docker Daemon Check to Installation Scripts"
stage: "general"
date_iso: "2026-01-21"
model: "qwen3-code-plus"
surface: "agent"
feature: "none"
branch: "main"
user: "user"
command: "add docker daemon check"
labels: ["kafka", "installation", "docker", "error-handling"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
---

## Files Modified

- `.claude/skills/kafka/scripts/install-kafka.ps1`
- `.claude/skills/kafka/scripts/install-kafka.sh`

## Summary

Enhanced both Kafka installation scripts to check if the Docker daemon is running before attempting to start the Kafka container. This prevents errors when Docker Desktop is installed but not currently running.

## Details

Updated both PowerShell and Bash installation scripts to:
1. Check if the Docker daemon is accessible before attempting to run containers
2. Provide clear error messages if Docker Desktop/engine is not running
3. Guide users to start Docker Desktop before running the script
4. Include platform-specific instructions (WSL2 on Windows, service status on Linux/macOS)

## Outcome

The installation scripts now gracefully handle the scenario where Docker is installed but the daemon is not running, providing helpful instructions to the user instead of cryptic Docker API connection errors.

## Evaluation

The changes successfully address the issue where the script would fail with a confusing Docker API connection error when Docker Desktop wasn't running. Users now receive clear instructions to start Docker before running the script.
