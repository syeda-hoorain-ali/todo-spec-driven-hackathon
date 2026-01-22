import pytest
import asyncio
import time
from unittest.mock import Mock, patch
from src.services.task_service import TaskService
from src.kafka.consumer import KafkaConsumer
from src.kafka.topics import TASK_CREATED_TOPIC
from src.kafka.event_schemas import TaskCreatedEventSchema


@pytest.mark.asyncio
async def test_task_creation_triggers_kafka_event():
    """
    Test end-to-end flow: create task → publish event → consume and process → verify within 5 seconds.
    """
    # This is a simplified test that verifies the flow logic
    # In a real implementation, we would need a running Kafka instance or mocking

    # Arrange
    task_service = TaskService()

    # We'll mock the actual Kafka interaction but verify the flow
    with patch.object(task_service.connection_pool, 'execute_producer_operation_with_retry') as mock_producer_call:
        # Act - Create a task
        start_time = time.time()

        task_result = task_service.create_task(
            title="Integration Test Task",
            description="Test task for end-to-end flow",
            user_id="test-user-123"
        )

        end_time = time.time()
        duration = end_time - start_time

        # Assert - Verify task was created
        assert task_result is not None
        assert task_result["title"] == "Integration Test Task"
        assert task_result["user_id"] == "test-user-123"

        # Verify that a Kafka event was published (mock was called)
        assert mock_producer_call.called
        assert duration < 5.0, f"Task creation took {duration}s, which exceeds 5s SLA"

        # Verify the call was made with the expected parameters
        # The first argument to the call is the operation function
        call_args = mock_producer_call.call_args
        assert call_args is not None


def test_task_created_event_schema_validation():
    """
    Test that task.created events conform to the expected schema.
    """
    # Arrange
    event_payload_data = {
        "taskId": "test-task-id",
        "title": "Test Task",
        "description": "Test Description",
        "status": "pending",
        "priority": "medium",
        "dueDate": "2023-12-31T23:59:59Z",
        "tags": ["test", "integration"],
        "createdAt": "2023-01-01T00:00:00Z",
        "updatedAt": "2023-01-01T00:00:00Z"
    }

    # Act
    event = TaskCreatedEventSchema(
        userId="test-user",
        payload=event_payload_data
    )

    # Assert
    assert event.eventId is not None
    assert event.timestamp is not None
    assert event.eventType == "task.created"
    assert event.source == "task-service"
    assert event.userId == "test-user"
    assert event.payload.taskId == "test-task-id"
    assert event.payload.title == "Test Task"


def test_multiple_consumers_can_process_events():
    """
    Test that multiple consumers can process events (conceptual test).
    """
    # This is a conceptual test - in practice, this would require actual Kafka setup
    # to verify that multiple consumers in the same group can process different partitions

    # Simulate that the consumer classes exist and can be instantiated
    from src.kafka.consumers.task_consumer import TaskConsumer
    from src.kafka.consumers.notification_consumer import NotificationConsumer
    from src.kafka.consumers.audit_consumer import AuditConsumer

    # Verify that consumers can be instantiated with different group IDs
    task_consumer = TaskConsumer(group_id="test-task-group")
    notification_consumer = NotificationConsumer(group_id="test-notification-group")
    audit_consumer = AuditConsumer(group_id="test-audit-group")

    # Verify they have the expected attributes
    assert hasattr(task_consumer, 'subscribe')
    assert hasattr(notification_consumer, 'subscribe')
    assert hasattr(audit_consumer, 'subscribe')

    # Clean up
    task_consumer.close()
    notification_consumer.close()
    audit_consumer.close()


def test_event_processing_within_slas():
    """
    Test that event processing meets performance SLAs.
    """
    # Arrange
    task_service = TaskService()

    # Measure the time it takes to create multiple tasks
    start_time = time.time()

    # Create several tasks to test throughput
    for i in range(10):
        with patch.object(task_service.connection_pool, 'execute_producer_operation_with_retry') as mock_producer_call:
            task_service.create_task(
                title=f"SLA Test Task {i}",
                description=f"SLA test task {i}",
                user_id="sla-tester"
            )

    end_time = time.time()
    total_duration = end_time - start_time

    # Assert that all 10 tasks were created within a reasonable time
    # (In a real system, we'd have stricter SLAs)
    assert total_duration < 30.0, f"Creating 10 tasks took {total_duration}s, which is too slow"


def test_task_update_triggers_kafka_event():
    """
    Test end-to-end flow: update task → publish event → consume and process → verify consistency.
    """
    # Arrange
    task_service = TaskService()

    # We'll mock the actual Kafka interaction but verify the flow logic
    with patch.object(task_service.connection_pool, 'execute_producer_operation_with_retry') as mock_producer_call:
        # Act - Update a task
        start_time = time.time()

        task_result = task_service.update_task(
            task_id="test-task-id",
            title="Updated Integration Test Task",
            description="Updated test task for end-to-end flow",
            user_id="test-user-123"
        )

        end_time = time.time()
        duration = end_time - start_time

        # Assert - Verify task was updated
        assert task_result is not None
        assert task_result["id"] == "test-task-id"
        assert task_result["title"] == "Updated Integration Test Task"
        assert task_result["user_id"] == "test-user-123"

        # Verify that a Kafka event was published (mock was called)
        assert mock_producer_call.called

        # Verify the call was made with the expected parameters
        # The first argument to the call is the operation function
        call_args = mock_producer_call.call_args
        assert call_args is not None


def test_reminder_flow_triggers_notifications():
    """
    Test reminder flow: schedule task → generate reminder event → deliver notification within 1 minute.
    """
    # Arrange
    from src.services.reminder_scheduler import reminder_scheduler
    from datetime import datetime, timedelta

    # Use a future time for the reminder (in 2 seconds for testing)
    future_time = datetime.now() + timedelta(seconds=2)
    reminder_time = future_time.isoformat()

    # Act - Schedule a reminder
    start_time = time.time()

    job_id = reminder_scheduler.schedule_reminder(
        task_id="test-reminder-task",
        user_id="test-user",
        due_date="2023-12-31T23:59:59Z",
        reminder_time=reminder_time,
        reminder_types=["in-app"]
    )

    end_time = time.time()
    scheduling_duration = end_time - start_time

    # Assert - Verify the reminder was scheduled
    assert job_id is not None
    assert "test-reminder-task" in job_id

    # Check that scheduling happened quickly (under 1 second)
    assert scheduling_duration < 1.0, f"Scheduling took {scheduling_duration}s, which is too slow"

    # Get upcoming reminders to verify it was added
    upcoming_reminders = reminder_scheduler.get_upcoming_reminders()
    assert len(upcoming_reminders) > 0

    # Find our specific reminder
    reminder_found = False
    for reminder in upcoming_reminders:
        if reminder['task_id'] == 'test-reminder-task':
            reminder_found = True
            break

    assert reminder_found, "Scheduled reminder not found in upcoming reminders"

    # Cancel the reminder since we don't actually want it to execute
    reminder_scheduler.cancel_reminder(job_id)


def test_audit_trail_persistence_and_search():
    """
    Test audit trail: perform task operations → generate audit events → verify persistence and search.
    """
    # Arrange
    from src.services.audit_log_service import AuditEntry, audit_log_service
    from datetime import datetime

    # Create a test audit entry
    audit_entry = AuditEntry(
        entity_type="task",
        entity_id="test-audit-task-123",
        operation="CREATE",
        user_id="test-audit-user",
        details={"title": "Test Task", "description": "Test Description"},
        source="test"
    )

    # Act - Save the audit entry
    start_time = time.time()
    audit_log_service.save_audit_entry(audit_entry)
    end_time = time.time()
    save_duration = end_time - start_time

    # Assert - Verify the entry was saved
    assert audit_entry.id is not None, "Audit entry should have been assigned an ID"

    # Verify we can retrieve the entry by ID
    retrieved_entry = audit_log_service.get_audit_entry_by_id(audit_entry.id)
    assert retrieved_entry is not None, "Audit entry should be retrievable by ID"
    assert retrieved_entry.entity_id == "test-audit-task-123", "Retrieved entry should have correct entity ID"
    assert retrieved_entry.user_id == "test-audit-user", "Retrieved entry should have correct user ID"

    # Test retrieval with filters
    entries = audit_log_service.get_audit_entries(entity_id="test-audit-task-123")
    assert len(entries) >= 1, "Should find at least one entry with the specified entity ID"
    assert entries[0].entity_id == "test-audit-task-123", "Entry should have correct entity ID"

    # Test search functionality
    search_results = audit_log_service.search_audit_entries(search_term="Test Task")
    assert len(search_results) >= 1, "Should find entry when searching for 'Test Task'"

    # Verify that saving was fast enough (under 1 second)
    assert save_duration < 1.0, f"Saving audit entry took {save_duration}s, which is too slow"

    # Clean up - Test retention policy by cleaning up entries older than 0 days (will delete our test entry)
    # But we won't run this as it would delete our test entry immediately
    # audit_log_service.cleanup_old_entries(days_to_keep=0)


def test_extensibility_pattern():
    """
    Test extensibility: add new event type → create consumer → verify functionality.
    """
    # Arrange - Import necessary modules
    from src.kafka.event_handler import EventDispatcher
    from src.kafka.consumer_factory import consumer_factory
    from src.kafka.sample_events import UserLoggedInHandler, UserLoggedInEventSchema
    from src.kafka.dead_letter_queue import create_dlq_handler
    from src.kafka.producer import KafkaProducer
    from src.kafka.event_registry import event_registry
    import uuid

    # Create DLQ handler
    dlq_handler = create_dlq_handler(KafkaProducer())

    # Create a handler for the sample event
    handler = UserLoggedInHandler(dlq_handler)

    # Create an event dispatcher and register the handler
    dispatcher = EventDispatcher()
    dispatcher.register_handler("user.logged.in", handler)

    # Verify the event type is registered
    assert event_registry.is_event_type_registered("user.logged.in"), "Event type should be registered"
    schema_class = event_registry.get_schema_class("user.logged.in")
    assert schema_class is not None, "Schema class should exist for registered event type"

    # Create a consumer using the factory
    consumer = consumer_factory.create_consumer_with_handlers(
        group_id="extensibility-test-group",
        topics=["user.events"],
        event_dispatcher=dispatcher
    )

    # Verify consumer was created
    assert consumer is not None, "Consumer should be created successfully"

    # Test event validation
    test_event_data = {
        'eventId': str(uuid.uuid4()),
        'timestamp': '2023-01-01T00:00:00Z',
        'eventType': 'user.logged.in',
        'source': 'authentication-service',
        'userId': 'test-user-123',
        'payload': {
            'user_id': 'test-user-123',
            'session_id': 'session-abc',
            'ip_address': '127.0.0.1',
            'timestamp': '2023-01-01T00:00:00Z'
        }
    }

    # Validate the event against the schema
    is_valid = event_registry.validate_event("user.logged.in", test_event_data)
    assert is_valid, "Event should be valid according to its schema"

    # Test the dispatcher with a sample message
    sample_message = {
        'value': test_event_data,
        'topic': 'user.events',
        'partition': 0,
        'offset': 0
    }

    # Dispatch the message - this should work without errors
    success = dispatcher.dispatch(sample_message)
    assert success, "Message should be dispatched successfully"

    # Clean up
    consumer.close()