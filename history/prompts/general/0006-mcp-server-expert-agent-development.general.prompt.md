---
id: 0006
title: MCP Server Expert Agent Development
stage: general
date: 2025-12-21
surface: agent
model: qwen3-code-plus
feature: none
branch: phase-03/001-ai-chatbot
user: Claude
command: "Create MCP server expert agent with skills for OpenAI Agents SDK"
labels: ["mcp", "openai-agents", "sdk", "integration", "spec-driven-development"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/agents/mcp-server-expert-agent.md
  - .claude/skills/hosted-mcp-server/SKILL.md
  - .claude/skills/streamable-http-mcp-server/SKILL.md
  - .claude/skills/mcp-server-sse/SKILL.md
  - .claude/skills/mcp-server-stdio/SKILL.md
  - .claude/skills/mcp-server-troubleshooting/SKILL.md
  - .claude/skills/mcp-server-discovery/SKILL.md
tests: []
---

# MCP Server Expert Agent Development

## Prompt

Create an MCP server expert agent that can connect any kind of MCP server with OpenAI Agents SDK's agent, with appropriate skills for different transport methods and scenarios.

## Response

Developed a comprehensive MCP server expert agent with specialized skills for different transport methods:

1. Created the main agent configuration (.claude/agents/mcp-server-expert-agent.md) with:
   - Detailed system prompt focusing on skill usage
   - Configuration for 6 specialized skills
   - Clear guidelines for transport method selection

2. Created 6 specialized skills:
   - hosted-mcp-server: For publicly accessible servers using OpenAI's infrastructure
   - streamable-http-mcp-server: For HTTP-based server connections
   - mcp-server-sse: For Server-Sent Events transport
   - mcp-server-stdio: For local subprocess communication
   - mcp-server-troubleshooting: For diagnosing and fixing connection issues
   - mcp-server-discovery: For researching and finding connection details for specific services

3. Each skill includes:
   - Accurate parameter documentation
   - Proper usage context
   - Working code examples
   - Configuration options

4. The agent follows a skill-based approach where it selects the most appropriate skill based on user requirements rather than having all information in the system prompt.

## Outcome

Successfully created a modular, comprehensive MCP server expert agent system that can handle all types of MCP server connections with OpenAI Agents SDK. The agent is capable of:
- Connecting to different types of MCP servers using appropriate transport methods
- Troubleshooting connection issues
- Discovering connection details for specific services
- Providing accurate configuration guidance
- Following best practices for each transport method
