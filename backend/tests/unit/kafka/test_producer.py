import pytest
from unittest.mock import Mock, patch, MagicMock
from src.kafka.producer import KafkaProducer


class TestKafkaProducer:
    """Test cases for KafkaProducer class."""

    @patch('src.kafka.producer.Producer')
    def test_producer_initialization(self, mock_producer_class):
        """Test that KafkaProducer initializes correctly."""
        # Arrange
        mock_producer_instance = Mock()
        mock_producer_class.return_value = mock_producer_instance

        # Act
        producer = KafkaProducer()

        # Assert
        assert producer is not None
        mock_producer_class.assert_called_once()

    @patch('src.kafka.producer.Producer')
    @patch('src.kafka.producer.serialize_message')
    def test_produce_method_calls_underlying_producer(self, mock_serialize, mock_producer_class):
        """Test that the produce method calls the underlying producer."""
        # Arrange
        mock_producer_instance = Mock()
        mock_producer_class.return_value = mock_producer_instance
        mock_serialize.return_value = '{"test": "message"}'

        producer = KafkaProducer()
        topic = "test-topic"
        message = {"test": "message"}
        key = "test-key"
        headers = {"header": "value"}

        # Act
        producer.produce(topic, message, key, headers)

        # Assert
        mock_serialize.assert_called_once_with(message)
        mock_producer_instance.produce.assert_called_once_with(
            topic=topic,
            value='{"test": "message"}',
            key=key,
            headers=headers,
            callback=producer.delivery_callback
        )
        mock_producer_instance.poll.assert_called_once_with(0)

    @patch('src.kafka.producer.Producer')
    def test_flush_method_calls_underlying_flush(self, mock_producer_class):
        """Test that the flush method calls the underlying producer flush."""
        # Arrange
        mock_producer_instance = Mock()
        mock_producer_instance.flush.return_value = 0
        mock_producer_class.return_value = mock_producer_instance

        producer = KafkaProducer()
        timeout = 10

        # Act
        result = producer.flush(timeout)

        # Assert
        mock_producer_instance.flush.assert_called_once_with(timeout)
        assert result == 0

    def test_delivery_callback_success(self, caplog):
        """Test delivery callback with no error."""
        # Arrange
        producer = KafkaProducer()
        mock_msg = Mock()
        mock_msg.topic.return_value = "test-topic"
        mock_msg.partition.return_value = 0
        mock_msg.offset.return_value = 100

        # Act
        with caplog.at_level("INFO"):
            producer.delivery_callback(None, mock_msg)

        # Assert
        assert "Message delivered" in caplog.text

    def test_delivery_callback_failure(self, caplog):
        """Test delivery callback with error."""
        # Arrange
        producer = KafkaProducer()
        mock_error = Mock()
        mock_error.code.return_value = 1

        # Act
        with caplog.at_level("ERROR"):
            producer.delivery_callback(mock_error, None)

        # Assert
        assert "Message delivery failed" in caplog.text

    @patch('src.kafka.producer.Producer')
    @patch('src.kafka.producer.serialize_message')
    def test_produce_method_with_exception(self, mock_serialize, mock_producer_class):
        """Test that the produce method properly handles exceptions."""
        # Arrange
        mock_producer_instance = Mock()
        mock_producer_class.return_value = mock_producer_instance
        mock_serialize.side_effect = Exception("Serialization error")

        producer = KafkaProducer()
        topic = "test-topic"
        message = {"test": "message"}

        # Act & Assert
        with pytest.raises(Exception, match="Serialization error"):
            producer.produce(topic, message)

    @patch('src.kafka.producer.Producer')
    def test_get_delivery_success_rate_returns_float(self, mock_producer_class):
        """Test that get_delivery_success_rate returns a float value."""
        # Arrange
        mock_producer_instance = Mock()
        mock_producer_class.return_value = mock_producer_instance

        producer = KafkaProducer()

        # Act
        success_rate = producer.get_delivery_success_rate()

        # Assert
        assert isinstance(success_rate, float)
        assert 0.0 <= success_rate <= 1.0

    @patch('src.kafka.producer.Producer')
    @patch('src.kafka.producer.serialize_message')
    def test_produce_with_ack_method(self, mock_serialize, mock_producer_class):
        """Test that the produce_with_ack method works correctly."""
        # Arrange
        mock_producer_instance = Mock()
        mock_producer_class.return_value = mock_producer_instance
        mock_serialize.return_value = '{"test": "message"}'

        producer = KafkaProducer()
        topic = "test-topic"
        message = {"test": "message"}
        key = "test-key"
        headers = {"header": "value"}

        # Act
        producer.produce_with_ack(topic, message, key, headers)

        # Assert
        mock_serialize.assert_called_once_with(message)
        mock_producer_instance.produce.assert_called_once()
        mock_producer_instance.poll.assert_called_once_with(0)