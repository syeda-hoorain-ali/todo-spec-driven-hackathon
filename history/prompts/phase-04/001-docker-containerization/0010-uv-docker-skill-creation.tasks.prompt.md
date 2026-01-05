---
id: 0010
title: "uv Docker Integration Skill Creation"
stage: "tasks"
date: "2026-01-02"
model: "claude-sonnet-4-5-20251101"
feature: "docker-containerization"
branch: "phase-04/001-docker-containerization"
user: "Claude"
command: "Create uv Docker integration skill and template"
labels: ["docker", "uv", "skill", "template", "containerization"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - ".claude/skills/uv-docker-integration/SKILL.md"
  - ".claude/skills/uv-docker-integration/templates/python-uv-dockerfile.template"
tests: []
---

# uv Docker Integration Skill Creation

## Summary

This PHR documents the creation of a comprehensive skill for using uv (Python package manager) in Docker environments. The skill includes best practices for multi-stage builds, caching strategies, optimization techniques, and security considerations when containerizing Python applications with uv.

## Prompt Text

The user requested to fetch the uv Docker documentation from the official repository, understand it, and create a skill for using uv with Docker following best practices from the documentation. The user wanted to create a skill with templates for future use.

## Response Text

I've successfully:

1. Fetched the official uv Docker documentation from the uv repository
2. Analyzed the best practices and patterns described in the documentation
3. Created a comprehensive skill file (.claude/skills/uv-docker-integration/SKILL.md) that includes:
   - Detailed instructions for installing uv in Docker
   - Multi-stage Dockerfile patterns
   - Caching strategies for faster builds
   - Security best practices (non-root users, minimal images)
   - Optimization techniques (bytecode compilation, intermediate layers)
   - Development workflow patterns
   - Troubleshooting tips

4. Created a template Dockerfile (.claude/skills/uv-docker-integration/templates/python-uv-dockerfile.template) based on the official uv Docker example that demonstrates:
   - Using the official uv image with pre-installed uv
   - Setting up non-root user for security
   - Proper environment variable configuration
   - Efficient caching with mount points
   - Dependency installation with locked versions
   - Production-ready configuration

The skill follows the structure and guidelines for Claude skills, providing comprehensive guidance for using uv in Docker environments with practical examples and best practices.

## Outcome

Successfully created a reusable skill for uv Docker integration that can be used across projects. The skill provides comprehensive guidance for containerizing Python applications with uv, following industry best practices for security, performance, and maintainability. The accompanying template provides a ready-to-use Dockerfile that implements all the best practices.

## Evaluation

The skill creation followed proper structure and content guidelines:
- Clear description of when and how to use the skill
- Comprehensive coverage of uv Docker integration patterns
- Practical, copy-pastable Dockerfile examples
- Best practices for security, performance, and maintainability
- Proper organization with sections for different use cases
- Templates that follow official uv recommendations
- Troubleshooting guidance for common issues