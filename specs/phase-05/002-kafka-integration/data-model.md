# Data Model for Kafka Integration

## Event Message Structure

### Base Event Schema
```json
{
  "eventId": "string",
  "timestamp": "ISO 8601 datetime",
  "eventType": "string",
  "source": "string",
  "userId": "string",
  "payload": "object",
  "headers": "object"
}
```

### Specific Event Types

#### Task Created Event
- **Topic**: `todo.task.events`
- **EventType**: `task.created`
- **Payload**:
  - taskId: string
  - title: string
  - description: string (optional)
  - status: enum (pending, completed, archived)
  - priority: enum (low, medium, high)
  - dueDate: ISO 8601 datetime (optional)
  - tags: array of strings
  - createdAt: ISO 8601 datetime
  - updatedAt: ISO 8601 datetime

#### Task Updated Event
- **Topic**: `todo.task.events`
- **EventType**: `task.updated`
- **Payload**:
  - taskId: string
  - previousState: object (previous task state)
  - newState: object (updated task state)
  - updatedAt: ISO 8601 datetime

#### Task Deleted Event
- **Topic**: `todo.task.events`
- **EventType**: `task.deleted`
- **Payload**:
  - taskId: string
  - deletedAt: ISO 8601 datetime

#### Task Completed Event
- **Topic**: `todo.task.events`
- **EventType**: `task.completed`
- **Payload**:
  - taskId: string
  - completedAt: ISO 8601 datetime
  - completedBy: string (userId)

#### Task Reminder Event
- **Topic**: `todo.reminders`
- **EventType**: `task.reminder`
- **Payload**:
  - taskId: string
  - userId: string
  - dueDate: ISO 8601 datetime
  - reminderTime: ISO 8601 datetime
  - reminderType: enum (email, push, in-app)

#### Audit Log Event
- **Topic**: `todo.audit.log`
- **EventType**: varies (create, update, delete, etc.)
- **Payload**:
  - action: string
  - userId: string
  - timestamp: ISO 8601 datetime
  - resourceType: string
  - resourceId: string
  - beforeState: object (optional)
  - afterState: object (optional)

## Consumer Group Models

### Task Consumer Group
- **Consumes From**: `todo.task.events`
- **Processing Logic**: Update task state, trigger related actions
- **Concurrency**: Configurable number of consumers based on load

### Notification Consumer Group
- **Consumes From**: `todo.reminders`, `todo.task.events`
- **Processing Logic**: Send notifications via appropriate channels
- **Concurrency**: Configurable based on notification volume

### Audit Consumer Group
- **Consumes From**: All event topics
- **Processing Logic**: Store audit records in persistent storage
- **Concurrency**: Single consumer to maintain audit sequence

## Topic Configuration

### todo.task.events
- **Partitions**: 6 (based on expected throughput)
- **Replication Factor**: 3 (for durability)
- **Retention Policy**: 7 days

### todo.audit.log
- **Partitions**: 3 (lower throughput requirement)
- **Replication Factor**: 3 (for compliance)
- **Retention Policy**: 90 days

### todo.notifications
- **Partitions**: 4 (moderate throughput)
- **Replication Factor**: 3
- **Retention Policy**: 7 days

### todo.reminders
- **Partitions**: 3 (moderate throughput)
- **Replication Factor**: 3
- **Retention Policy**: 1 day (short-lived events)

### todo.dead.letter
- **Partitions**: 2 (low throughput, error handling)
- **Replication Factor**: 3
- **Retention Policy**: 30 days

## Validation Rules

1. **Event ID**: Must be unique UUID
2. **Timestamp**: Must be in ISO 8601 format and current or past
3. **Event Type**: Must be one of predefined event types
4. **Required Fields**: All required fields must be present
5. **User ID**: Must be valid user identifier
6. **Payload**: Must conform to specific event type schema

## State Transitions

### Task State Transitions
- `pending` → `completed` (via task.completed event)
- `pending` → `archived` (via task.updated event)
- `completed` → `pending` (via task.updated event)
- `archived` → `pending` (via task.updated event)

### Event Processing States
- `created` → `published` → `consumed` → `processed` | `failed`
- Failed events transition to `todo.dead.letter` topic