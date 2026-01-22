# Kafka Event-Driven Architecture Extensibility Guide

This document describes how to extend the Kafka-based event-driven architecture with new event types and consumers.

## Overview

The system is designed with extensibility in mind, allowing developers to add new event types and consumers without modifying existing code. The architecture follows the following patterns:

1. **Event Registration System** - Register new event types with schemas
2. **Abstract Event Handler Pattern** - Define handlers for processing events
3. **Consumer Factory Pattern** - Dynamically instantiate consumers
4. **Event Dispatcher** - Route events to appropriate handlers

## Adding a New Event Type

### 1. Define the Event Schema

Create a new schema class that extends the `BaseEventSchema`:

```python
from src.kafka.event_schemas import BaseEventSchema, BaseModel

class MyCustomEventPayload(BaseModel):
    custom_field: str
    another_field: int

class MyCustomEventSchema(BaseEventSchema):
    eventType: str = "my.custom.event"
    source: str = "my-service"
    payload: MyCustomEventPayload
```

### 2. Register the Event Type

Register your event type with the event registry:

```python
from src.kafka.event_registry import event_registry

event_registry.register_event_type(
    event_type="my.custom.event",
    schema_class=MyCustomEventSchema,
    metadata={
        "description": "Description of the custom event",
        "version": "1.0.0"
    }
)
```

Alternatively, use the decorator:

```python
from src.kafka.event_registry import register_event

@register_event(
    event_type="my.custom.event",
    schema_class=MyCustomEventSchema
)
class MyCustomEventSchema(BaseEventSchema):
    # ... schema definition
```

### 3. Create an Event Handler

Create a handler class that extends `AbstractEventHandler`:

```python
from src.kafka.event_handler import AbstractEventHandler

class MyCustomEventHandler(AbstractEventHandler):
    def handle(self, message: Dict[str, Any]) -> None:
        # Process the event
        event_data = message['value']
        custom_field = event_data['payload']['custom_field']

        # Your custom logic here
        print(f"Processing custom event with field: {custom_field}")
```

### 4. Register the Handler

Register your handler with the event dispatcher:

```python
from src.kafka.event_handler import EventDispatcher

dispatcher = EventDispatcher()
handler = MyCustomEventHandler(dlq_handler=my_dlq_handler)
dispatcher.register_handler("my.custom.event", handler)
```

## Creating a New Consumer

### 1. Using the Consumer Factory

Use the consumer factory to create a consumer with handlers:

```python
from src.kafka.consumer_factory import consumer_factory

# Create a consumer that uses the event dispatcher
consumer = consumer_factory.create_consumer_with_handlers(
    group_id="my-custom-consumer-group",
    topics=["my-topic"],
    event_dispatcher=dispatcher
)
```

### 2. Starting the Consumer

Start the consumer to begin processing messages:

```python
# Start consuming messages
consumer.start_consuming_with_handlers(["my-topic"])
```

## Complete Example

Here's a complete example of adding a new "user.profile.updated" event:

```python
# 1. Define the schema
from src.kafka.event_schemas import BaseEventSchema, BaseModel

class UserProfileUpdatedPayload(BaseModel):
    user_id: str
    updated_fields: list
    timestamp: str

class UserProfileUpdatedEventSchema(BaseEventSchema):
    eventType: str = "user.profile.updated"
    source: str = "user-service"
    payload: UserProfileUpdatedPayload

# 2. Register the event type
from src.kafka.event_registry import event_registry

event_registry.register_event_type(
    event_type="user.profile.updated",
    schema_class=UserProfileUpdatedEventSchema,
    metadata={
        "description": "Fired when a user profile is updated",
        "version": "1.0.0"
    }
)

# 3. Create the handler
from src.kafka.event_handler import AbstractEventHandler
from typing import Dict, Any

class UserProfileUpdatedHandler(AbstractEventHandler):
    def handle(self, message: Dict[str, Any]) -> None:
        event_data = message['value']
        user_id = event_data['payload']['user_id']
        updated_fields = event_data['payload']['updated_fields']

        print(f"User {user_id} profile updated with fields: {updated_fields}")

        # Add your custom business logic here

# 4. Set up the dispatcher and consumer
from src.kafka.event_handler import EventDispatcher
from src.kafka.consumer_factory import consumer_factory
from src.kafka.dead_letter_queue import create_dlq_handler
from src.kafka.producer import KafkaProducer

# Create DLQ handler
dlq_handler = create_dlq_handler(KafkaProducer())

# Create and register handler
handler = UserProfileUpdatedHandler(dlq_handler)
dispatcher = EventDispatcher()
dispatcher.register_handler("user.profile.updated", handler)

# Create consumer with handlers
consumer = consumer_factory.create_consumer_with_handlers(
    group_id="profile-update-consumer",
    topics=["user-events"],
    event_dispatcher=dispatcher
)

# Start consuming
consumer.start_consuming_with_handlers(["user-events"])
```

## Best Practices

1. **Always validate events** against their registered schema
2. **Handle errors gracefully** using the dead letter queue mechanism
3. **Use descriptive event type names** following the convention `domain.action.object`
4. **Keep handlers idempotent** to handle duplicate events safely
5. **Implement proper logging** for observability
6. **Consider performance implications** when adding new event types

## Testing New Events

When adding new events, make sure to:

1. Test the event schema validation
2. Test the handler logic with sample data
3. Test the consumer with real Kafka messages
4. Verify error handling and DLQ functionality
5. Validate that the event follows the expected format

## Monitoring and Observability

New events should include proper logging and metrics:

- Log successful event processing
- Log errors and DLQ events
- Track event processing rates
- Monitor consumer lag
- Track event validation failures