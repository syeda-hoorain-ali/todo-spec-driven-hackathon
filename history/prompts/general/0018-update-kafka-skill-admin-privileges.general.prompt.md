---
id: "0018"
title: "Update Kafka Skill Admin Privileges"
stage: "general"
date_iso: "2026-01-21"
model: "qwen3-code-plus"
surface: "agent"
feature: "none"
branch: "main"
user: "user"
command: "update kafka skill admin privileges"
labels: ["kafka", "documentation", "security"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
---

## Files Modified

- `.claude/skills/kafka.SKILL.md`

## Summary

Updated the Kafka skill documentation to include clear instructions about running installation scripts with administrator privileges. This addresses the issue encountered when installing Kafka to system directories that require elevated permissions.

## Details

Added explicit instructions in the SKILL.md file to inform users that they must run the installation scripts with administrator privileges on Windows or as root on Linux/macOS. The documentation now includes specific commands that users can copy-paste to run the scripts with the necessary elevated permissions.

## Outcome

The Kafka skill documentation now properly warns users about privilege requirements for installation, reducing potential errors during the installation process.

## Evaluation

The changes successfully address the requirement to inform users about running installation scripts with elevated privileges. The instructions are clear, specific, and provide copy-paste ready commands for both Windows and Linux/macOS platforms.