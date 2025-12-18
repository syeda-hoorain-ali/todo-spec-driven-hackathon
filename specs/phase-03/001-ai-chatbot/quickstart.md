# Quickstart Guide: AI-Powered Todo Chatbot

**Feature**: AI-Powered Todo Chatbot
**Date**: 2025-12-17
**Spec**: [specs/phase-03/001-ai-chatbot/spec.md](./spec.md)

## Overview

This guide provides a quick overview of how to set up and run the AI-Powered Todo Chatbot feature. It covers the essential steps to get the application running with chatbot functionality.

## Prerequisites

- Node.js 20+ (for frontend)
- Python 3.12+ (for backend)
- A package manager (npm, yarn, pnpm, or bun)
- PostgreSQL or Neon Serverless Database
- OpenAI API key
- Better Auth secret

## Setup Instructions

### 1. Environment Setup

First, copy the Phase-02 structure to Phase-03:

```bash
cp -r phase-02 phase-03
```

### 2. Backend Setup

Navigate to the backend directory and install dependencies:

```bash
cd phase-03/backend
pip install -r requirements.txt
```

Set up environment variables in `.env`:

```env
DATABASE_URL=your_neon_database_url
OPENAI_API_KEY=your_openai_api_key
BETTER_AUTH_SECRET=your_better_auth_secret
JWT_SECRET=your_jwt_secret
MCP_SERVER_PORT=8001
```

### 3. Frontend Setup

Navigate to the frontend directory and install dependencies:

```bash
cd phase-03/frontend
npm install
```

Set up environment variables in `.env.local`:

```env
NEXT_PUBLIC_OPENAI_API_KEY=your_openai_api_key
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_CHAT_API_URL=http://localhost:8000
```

### 4. Database Setup

Run the database migrations to create the new conversation and message tables:

```bash
cd phase-03/backend
python -m src.models.migrate
```

### 5. Running the Application

#### Backend (with MCP Server)

```bash
cd phase-03/backend
uvicorn src.main:app --reload --port 8000
```

In a separate terminal, start the MCP server:

```bash
cd phase-03/backend
python -m src.agents.mcp_server
```

#### Frontend

```bash
cd phase-03/frontend
npm run dev
```

## Key Endpoints

### Chat API Endpoints

- `POST /api/chat` - Send a message to the chatbot
- `GET /api/conversations` - Get list of user's conversations
- `GET /api/conversations/{id}` - Get specific conversation with messages
- `DELETE /api/conversations/{id}` - Delete a conversation

### Task API Endpoints (Extended)

- `GET /api/tasks` - Get user's tasks (existing from Phase-02)
- `POST /api/tasks` - Create a task (existing from Phase-02)
- `PUT /api/tasks/{id}` - Update a task (existing from Phase-02)
- `DELETE /api/tasks/{id}` - Delete a task (existing from Phase-02)
- `PATCH /api/tasks/{id}/complete` - Toggle task completion (existing from Phase-02)

## Using the Chat Interface

1. Navigate to `http://localhost:3000/chat`
2. Ensure you're logged in (authentication required)
3. Type your natural language request, e.g.:
   - "Add a task to buy groceries"
   - "What are my pending tasks?"
   - "Mark the first task as complete"
   - "Delete the meeting task"

## Development Workflow

### Adding New MCP Tools

1. Create a new tool in `phase-03/backend/src/agents/task_tools.py`
2. Register the tool with the MCP server
3. Update the agent configuration to use the new tool

### Extending Chat Features

1. Add new components in `phase-03/frontend/src/components/chat/`
2. Update the chat service in `phase-03/frontend/src/services/chat-api.ts`
3. Add new endpoints in `phase-03/backend/src/api/chat_routes.py`

## Testing the Feature

### Manual Testing

1. Test natural language commands for task creation, reading, updating, and deletion
2. Verify conversation context is maintained across multiple exchanges
3. Test error handling for invalid requests
4. Verify user isolation (users only see their own data)

### API Testing

Use the following curl commands to test the API directly:

```bash
# Send a message to the chatbot
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}'

# Get user's conversations
curl -X GET http://localhost:8000/api/conversations \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Ensure JWT tokens are properly set and not expired
2. **AI API Errors**: Verify OpenAI API key is correct and has sufficient quota
3. **Database Connection**: Check that DATABASE_URL is properly configured
4. **MCP Server Not Responding**: Ensure the MCP server is running on the specified port

### Debugging Tips

- Enable debug logging by setting `DEBUG=true` in environment variables
- Check the backend logs for detailed error information
- Use browser developer tools to inspect API requests and responses
- Verify that all required environment variables are set
