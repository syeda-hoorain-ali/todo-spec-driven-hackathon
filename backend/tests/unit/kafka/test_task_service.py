import pytest
from unittest.mock import Mock, patch, MagicMock
from src.services.task_service import TaskService


class TestTaskService:
    """Test cases for TaskService class."""

    def test_task_service_initialization(self):
        """Test that TaskService initializes correctly."""
        # Act
        service = TaskService()

        # Assert
        assert service is not None
        assert service.connection_pool is not None

    @patch('src.services.task_service.uuid.uuid4')
    @patch('src.services.task_service.get_connection_pool')
    def test_create_task_publishes_event(self, mock_get_connection_pool, mock_uuid):
        """Test that creating a task publishes a Kafka event."""
        # Arrange
        mock_uuid.return_value = "test-task-id"

        mock_connection_pool = Mock()
        mock_producer_context = Mock()
        mock_producer = Mock()

        mock_connection_pool.get_producer.return_value.__enter__.return_value = mock_producer
        mock_connection_pool.execute_producer_operation_with_retry = lambda op, name: op()

        mock_get_connection_pool.return_value = mock_connection_pool

        service = TaskService()

        # Act
        result = service.create_task(
            title="Test Task",
            description="Test Description",
            user_id="test-user"
        )

        # Assert
        assert result["id"] == "test-task-id"
        assert result["title"] == "Test Task"
        assert result["description"] == "Test Description"
        assert result["user_id"] == "test-user"

        # Verify that the producer was called to publish the event
        mock_producer.produce.assert_called_once()
        mock_producer.flush.assert_called_once()

    @patch('src.services.task_service.get_connection_pool')
    def test_update_task_publishes_event(self, mock_get_connection_pool):
        """Test that updating a task publishes a Kafka event."""
        # Arrange
        mock_connection_pool = Mock()
        mock_producer_context = Mock()
        mock_producer = Mock()

        mock_connection_pool.get_producer.return_value.__enter__.return_value = mock_producer
        mock_connection_pool.execute_producer_operation_with_retry = lambda op, name: op()

        mock_get_connection_pool.return_value = mock_connection_pool

        service = TaskService()

        # Act
        result = service.update_task(
            task_id="test-task-id",
            title="Updated Task",
            user_id="test-user"
        )

        # Assert
        assert result["id"] == "test-task-id"
        assert result["title"] == "Updated Task"
        assert result["user_id"] == "test-user"

        # Verify that the producer was called to publish the event
        mock_producer.produce.assert_called_once()
        mock_producer.flush.assert_called_once()