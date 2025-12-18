# API Contract: Chat Functionality

**Feature**: AI-Powered Todo Chatbot
**Date**: 2025-12-18
**Spec**: [specs/phase-03/001-ai-chatbot/spec.md](../spec.md)

## Overview

This document defines the API contract for the chat functionality of the AI-Powered Todo Chatbot. It specifies the endpoints, request/response formats, authentication requirements, and error handling for the chat API.

## Base URL

`http://localhost:8000/api` (development)
`https://api.yourdomain.com/api` (production)

## Authentication

All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer {jwt_token}
```

The JWT token must be obtained through the existing Better Auth system from Phase-02.

## Endpoints

### POST /chat

Send a message to the AI chatbot and receive a response.

#### Request

**Headers:**
- `Authorization: Bearer {jwt_token}`
- `Content-Type: application/json`

**Body:**
```json
{
  "message": "string (required, user's message)",
  "conversation_id": "integer (optional, existing conversation ID)",
  "user_timezone": "string (optional, e.g. 'UTC', 'America/New_York')"
}
```

#### Response

**Success (200):**
```json
{
  "conversation_id": "integer (conversation ID)",
  "response": "string (AI-generated response)",
  "tool_calls": "array (list of MCP tools invoked, optional)",
  "timestamp": "ISO 8601 datetime"
}
```

**Error (400, 401, 403, 429, 500):**
```json
{
  "error": "string (error message)",
  "code": "string (error code)"
}
```

#### Rate Limiting
- Maximum 100 requests per user per hour
- Returns 429 status when rate limit is exceeded

### GET /conversations

Retrieve all conversations for the authenticated user.

#### Request

**Headers:**
- `Authorization: Bearer {jwt_token}`

#### Response

**Success (200):**
```json
{
  "conversations": [
    {
      "id": "integer (conversation ID)",
      "title": "string (conversation title)",
      "created_at": "ISO 8601 datetime",
      "updated_at": "ISO 8601 datetime",
      "is_active": "boolean",
      "message_count": "integer"
    }
  ]
}
```

### GET /conversations/{id}

Retrieve a specific conversation with its messages.

#### Request

**Headers:**
- `Authorization: Bearer {jwt_token}`

#### Response

**Success (200):**
```json
{
  "conversation": {
    "id": "integer (conversation ID)",
    "title": "string (conversation title)",
    "created_at": "ISO 8601 datetime",
    "updated_at": "ISO 8601 datetime",
    "is_active": "boolean"
  },
  "messages": [
    {
      "id": "integer (message ID)",
      "role": "string (user|assistant|system)",
      "content": "string (message content)",
      "timestamp": "ISO 8601 datetime",
      "message_type": "string (text|command|response|error)"
    }
  ]
}
```

### DELETE /conversations/{id}

Delete a specific conversation.

#### Request

**Headers:**
- `Authorization: Bearer {jwt_token}`

#### Response

**Success (200):**
```json
{
  "success": true,
  "message": "string (confirmation message)"
}
```

**Error (404):**
```json
{
  "error": "Conversation not found",
  "code": "CONVERSATION_NOT_FOUND"
}
```

### POST /tasks (Extended from Phase-02)

Create a task (also accessible via chatbot MCP tools).

#### Request

**Headers:**
- `Authorization: Bearer {jwt_token}`
- `Content-Type: application/json`

**Body:**
```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string (optional, max 1000 chars)",
  "due_date": "ISO 8601 datetime (optional)",
  "priority": "string (optional, low|medium|high)"
}
```

#### Response

**Success (201):**
```json
{
  "id": "integer (task ID)",
  "user_id": "string (user ID)",
  "title": "string",
  "description": "string",
  "completed": "boolean",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime",
  "due_date": "ISO 8601 datetime (or null)",
  "priority": "string"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `UNAUTHORIZED` | Invalid or missing JWT token |
| `FORBIDDEN` | User trying to access resources that don't belong to them |
| `RATE_LIMIT_EXCEEDED` | User has exceeded rate limit |
| `VALIDATION_ERROR` | Request body doesn't match expected schema |
| `TASK_NOT_FOUND` | Requested task doesn't exist |
| `CONVERSATION_NOT_FOUND` | Requested conversation doesn't exist |
| `AI_SERVICE_ERROR` | Error communicating with AI service |
| `INTERNAL_ERROR` | Unexpected server error |

## HTTP Status Codes

- `200`: Success
- `201`: Created (for POST requests)
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (invalid JWT)
- `403`: Forbidden (user access violation)
- `404`: Not Found (resource doesn't exist)
- `429`: Too Many Requests (rate limit exceeded)
- `500`: Internal Server Error

## Security Considerations

1. All endpoints require authentication via JWT tokens
2. Users can only access their own conversations and tasks
3. Rate limiting prevents abuse
4. Input validation prevents injection attacks
5. Sensitive data is not exposed in responses

## Performance Requirements

1. API responses should be under 3 seconds
2. 95% of requests should return successfully
3. Support for 100 concurrent users
4. Proper timeout handling for AI API calls (30 seconds)