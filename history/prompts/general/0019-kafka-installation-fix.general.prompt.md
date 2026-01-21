---
id: 019
title: kafka-installation-fix
stage: general
date: 2026-01-22
surface: agent
model: qwen3-code-plus
feature: none
branch: main
user: Claude
command: install kafka
labels: [kafka, installation, docker, configuration]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .claude/skills/kafka/scripts/install-kafka.ps1
 - .claude/skills/kafka/scripts/install-kafka.sh
 - test_kafka_connection.py
tests:
 - python test_kafka_connection.py
---

## Prompt

install kafka

## Response snapshot

Successfully installed Apache Kafka using the automated installation scripts. Fixed configuration issues in the Kafka Docker container setup that were preventing proper startup. Updated both the PowerShell and Bash installation scripts with correct Kafka 4.1.1 KRaft mode configuration parameters. Verified the installation by connecting to Kafka using the Python kafka-python library and sending test messages.

## Outcome

- ✅ Impact: Fixed Kafka installation scripts to prevent container startup failures
- 🧪 Tests: Python kafka-python client successfully connected and sent/received messages
- 📁 Files: Updated both installation scripts and created test script
- 🔁 Next prompts: Users can now install Kafka without configuration issues
- 🧠 Reflection: Proper Kafka KRaft configuration requires specific listener and security protocol mappings

## Evaluation notes (flywheel)

- Failure modes observed: Kafka container startup failure due to missing security protocol definitions for controller listener
- Graders run and results (PASS/FAIL): PASS - Kafka is now running and functional
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
