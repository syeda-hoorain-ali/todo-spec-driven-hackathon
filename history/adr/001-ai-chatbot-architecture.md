# ADR: AI Chatbot Architecture for Todo App

## Status
Accepted

## Context
We needed to implement an AI-powered chatbot for the todo app that allows users to manage their tasks through natural language conversations. The solution needed to integrate with the existing phase-02 architecture while providing secure, scalable, and maintainable functionality.

## Decision

### 1. MCP Server Integration
We decided to use the Model Context Protocol (MCP) to connect the AI agent with backend task operations. This provides a secure and standardized way to expose tools to the AI agent without giving it direct database access.

### 2. Data Model Design
We created separate Conversation and Message models to store chat history, with proper relationships to the existing User model to ensure data isolation and proper authorization.

### 3. Frontend Integration
We used the ChatKit React component for the frontend chat interface, implementing it as a floating widget that integrates seamlessly with the existing dashboard.

### 4. Authentication and Authorization
We leveraged the existing Better Auth JWT system to ensure user isolation and secure access to conversations and tasks.

## Alternatives Considered

### Direct API Calls vs MCP
- Direct API calls: Simpler but less secure and standardized
- MCP: More complex but provides better security boundaries and standardization

### Storage Options
- Separate database: More isolation but added complexity
- Same database with new tables: Simpler and maintains consistency with existing approach

### Frontend Options
- Custom chat component: More control but more development time
- ChatKit React: Faster implementation with good features out of the box

## Consequences

### Positive
- Secure tool access through MCP protocol
- Consistent with existing architecture patterns
- Reusable components for future AI features
- Proper user isolation and data security

### Negative
- Added complexity with MCP server setup
- Learning curve for MCP protocol
- Additional dependencies and infrastructure

## Implementation
The decision was implemented in the phase-03 directory with both backend and frontend components following the architecture described above.