# Data Model: AI-Powered Todo Chatbot

**Feature**: AI-Powered Todo Chatbot
**Date**: 2025-12-17
**Spec**: [specs/phase-03/001-ai-chatbot/spec.md](./spec.md)

## Overview

This document defines the data model for the AI-Powered Todo Chatbot feature, extending the existing Phase-02 data model with chat-specific entities while maintaining compatibility with existing task management functionality.

## Entity Models

### Conversation

Represents a chat session with context between a user and the AI assistant.

**Fields:**
- `id`: Integer (Primary Key, Auto-increment)
- `user_id`: String (Foreign Key to users table, required)
- `title`: String (Optional, auto-generated from first message or topic)
- `created_at`: DateTime (Required, default: current timestamp)
- `updated_at`: DateTime (Required, default: current timestamp, auto-updating)
- `is_active`: Boolean (Required, default: true)

**Relationships:**
- One-to-Many with Message (conversation has many messages)
- Many-to-One with User (belongs to one user)

**Validation Rules:**
- user_id must reference an existing user
- created_at must be in the past or present
- updated_at must be >= created_at

### Message

Represents individual messages in a conversation.

**Fields:**
- `id`: Integer (Primary Key, Auto-increment)
- `user_id`: String (Foreign Key to users table, required)
- `conversation_id`: Integer (Foreign Key to conversations table, required)
- `role`: String (Required, values: "user", "assistant", "system")
- `content`: Text (Required, max length: 10000 characters)
- `timestamp`: DateTime (Required, default: current timestamp)
- `message_type`: String (Optional, values: "text", "command", "response", "error")

**Relationships:**
- Many-to-One with Conversation (belongs to one conversation)
- Many-to-One with User (belongs to one user)

**Validation Rules:**
- conversation_id must reference an existing conversation
- role must be one of the allowed values
- content must not be empty
- timestamp must be in the past or present

### Task (Extended from Phase-02)

Represents a user's todo item, extended from the existing model.

**Fields:**
- `id`: Integer (Primary Key, Auto-increment)
- `user_id`: String (Foreign Key to users table, required)
- `title`: String (Required, max length: 200 characters)
- `description`: Text (Optional, max length: 1000 characters)
- `completed`: Boolean (Required, default: false)
- `created_at`: DateTime (Required, default: current timestamp)
- `updated_at`: DateTime (Required, default: current timestamp, auto-updating)
- `due_date`: DateTime (Optional)
- `priority`: String (Optional, values: "low", "medium", "high", default: "medium")

**Relationships:**
- Many-to-One with User (belongs to one user)

**Validation Rules:**
- user_id must reference an existing user
- title must be 1-200 characters
- priority must be one of the allowed values
- due_date must be in the future (if provided)

## Database Schema

```sql
-- Conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    conversation_id INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
```

## State Transitions

### Conversation States
- `active`: Conversation is open and accepting new messages
- `archived`: Conversation is closed but messages are preserved
- `deleted`: Conversation is marked for deletion (soft delete)

### Task States
- `pending`: Task is created but not completed
- `completed`: Task is marked as done
- `deleted`: Task is marked for deletion (soft delete from Phase-02)

## Relationships and Constraints

1. **User Isolation**: All data is associated with a specific user via user_id foreign key
2. **Cascade Deletion**: When a user is deleted, their conversations and messages are also deleted
3. **Conversation Integrity**: When a conversation is deleted, all associated messages are also deleted
4. **Message Ordering**: Messages are ordered by timestamp within each conversation

## API Data Transfer Objects

### ConversationDTO
```typescript
interface ConversationDTO {
  id: number;
  userId: string;
  title?: string;
  createdAt: Date;
  updatedAt: Date;
  isActive: boolean;
}
```

### MessageDTO
```typescript
interface MessageDTO {
  id: number;
  userId: string;
  conversationId: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  messageType?: 'text' | 'command' | 'response' | 'error';
}
```

### TaskDTO (Extended)
```typescript
interface TaskDTO {
  id: number;
  userId: string;
  title: string;
  description?: string;
  completed: boolean;
  createdAt: Date;
  updatedAt: Date;
  dueDate?: Date;
  priority?: 'low' | 'medium' | 'high';
}
```

## Migration Considerations

1. **Backward Compatibility**: Existing task operations from Phase-02 should continue to work
2. **Data Migration**: No migration needed as these are new tables with no existing data
3. **Indexing Strategy**: Proper indexes on foreign keys and frequently queried fields
4. **Performance**: Consider pagination for message history in long conversations
