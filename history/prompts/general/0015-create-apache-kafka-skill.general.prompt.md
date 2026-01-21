---
id: 0015
title: Create Apache Kafka Skill
stage: general
date_iso: 2026-01-19
surface: agent
model: qwen3-code-plus
feature: none
branch: main
user: user
command: Create Kafka skill
labels: ["kafka", "skill", "event-streaming", "architecture"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - .claude/skills/kafka/SKILL.md
  - .claude/skills/kafka/scripts/kafka-utils.sh
  - .claude/skills/kafka/references/kafka-reference.md
  - .claude/skills/kafka/assets/python-examples.py
  - .claude/skills/kafka/README.md
tests_yaml: []
prompt_text: |
  Using your skill creator skill create a new skill for Apache Kafka. I will use
  it to build event-driven architectures from hello world to professional production
  systems. Use context7 skill to study official documentation and then build it
  so no self assumed knowledge.
response_text: |
  Created a comprehensive Apache Kafka skill that includes:
  - Complete SKILL.md with Java producer/consumer examples, security configuration, monitoring metrics, and best practices
  - Utility script for common Kafka operations (topic management, producing, consuming)
  - Reference materials with configuration properties and best practices
  - Python examples to complement Java examples
  - Used context7 tools to get latest Kafka documentation
outcome: Successfully created a comprehensive Kafka skill with all required components
evaluation: The skill includes practical examples, security guidance, monitoring metrics, and production best practices
---
