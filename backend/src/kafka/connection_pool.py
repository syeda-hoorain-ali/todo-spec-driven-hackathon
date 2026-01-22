import logging
import time
import random
from typing import Dict, Any, Optional, Callable
from contextlib import contextmanager
from threading import Lock
from .producer import KafkaProducer
from .consumer import KafkaConsumer
from .circuit_breaker import kafka_circuit_breaker


logger = logging.getLogger(__name__)


class ExponentialBackoffRetry:
    """
    Exponential backoff retry mechanism for Kafka operations.
    """

    def __init__(self, max_retries: int = 5, base_delay: float = 1.0, max_delay: float = 60.0, jitter: bool = True):
        """
        Initialize the retry mechanism.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds for first retry
            max_delay: Maximum delay in seconds for any retry
            jitter: Whether to add random jitter to delays
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter

    def execute_with_retry(self, operation: Callable[[], Any], operation_name: str = "operation"):
        """
        Execute an operation with exponential backoff retry logic.

        Args:
            operation: The operation to execute
            operation_name: Name of the operation for logging

        Returns:
            Result of the operation

        Raises:
            Exception: If all retry attempts fail
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                result = operation()
                if attempt > 0:
                    logger.info(f"{operation_name} succeeded after {attempt} retries")
                return result
            except Exception as e:
                last_exception = e
                if attempt == self.max_retries:
                    logger.error(f"{operation_name} failed after {self.max_retries} retries: {str(e)}")
                    raise e

                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                if self.jitter:
                    delay = delay * (0.5 + random.random() * 0.5)  # Add jitter

                logger.warning(f"{operation_name} failed on attempt {attempt + 1}, "
                              f"retrying in {delay:.2f}s: {str(e)}")
                time.sleep(delay)

        # This should never be reached, but included for type safety
        if last_exception:
            raise last_exception

    def execute_with_retry_for_event_processing(self, operation: Callable[[], Any], operation_name: str = "event processing"):
        """
        Execute an operation with exponential backoff retry logic specifically for event processing.
        This is similar to execute_with_retry but logs differently for event processing scenarios.

        Args:
            operation: The operation to execute (typically event processing)
            operation_name: Name of the operation for logging

        Returns:
            Result of the operation

        Raises:
            Exception: If all retry attempts fail
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                result = operation()
                if attempt > 0:
                    logger.info(f"{operation_name} succeeded after {attempt} retry attempts")
                return result
            except Exception as e:
                last_exception = e
                if attempt == self.max_retries:
                    logger.error(f"{operation_name} failed after {self.max_retries} retry attempts: {str(e)}. Sending to DLQ.")
                    raise e

                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                if self.jitter:
                    delay = delay * (0.5 + random.random() * 0.5)  # Add jitter

                logger.warning(f"{operation_name} failed on attempt {attempt + 1}, "
                              f"retrying in {delay:.2f}s. Error: {str(e)}")
                time.sleep(delay)

        # This should never be reached, but included for type safety
        if last_exception:
            raise last_exception


class KafkaConnectionPool:
    """
    Connection pool for managing Kafka producers and consumers with graceful degradation.
    """
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the connection pool."""
        if hasattr(self, '_initialized'):
            return
        self._producers: Dict[str, KafkaProducer] = {}
        self._consumers: Dict[str, KafkaConsumer] = {}
        self._retry_mechanism = ExponentialBackoffRetry()
        self._circuit_breaker = kafka_circuit_breaker  # Use the global circuit breaker
        self._degraded_mode = False
        self._degraded_operations_count = 0
        self._max_degraded_operations = 100  # Threshold to reset degraded mode
        self._initialized = True

    @contextmanager
    def get_producer(self, producer_id: str = "default"):
        """
        Get a producer from the pool (context manager).

        Args:
            producer_id: Identifier for the producer

        Yields:
            KafkaProducer instance
        """
        if self._degraded_mode:
            # In degraded mode, we might want to skip Kafka operations or use alternative storage
            logger.warning(f"Connection pool in degraded mode, producer {producer_id} may not be available")

        producer = self._get_or_create_producer(producer_id)
        try:
            yield producer
        finally:
            # In a real implementation, you might return the producer to the pool
            # For now, we just ensure it's available for reuse
            pass

    def _get_or_create_producer(self, producer_id: str) -> KafkaProducer:
        """
        Get an existing producer or create a new one.

        Args:
            producer_id: Identifier for the producer

        Returns:
            KafkaProducer instance
        """
        if producer_id not in self._producers:
            try:
                self._producers[producer_id] = KafkaProducer()
                logger.info(f"Created new Kafka producer: {producer_id}")
            except Exception as e:
                logger.error(f"Failed to create Kafka producer {producer_id}: {str(e)}")
                # Enter degraded mode if producer creation fails
                self._enter_degraded_mode()
                # In a real implementation, you might want to store messages in a local queue for later processing
                raise
        return self._producers[producer_id]

    @contextmanager
    def get_consumer(self, group_id: str):
        """
        Get a consumer from the pool (context manager).

        Args:
            group_id: Consumer group ID

        Yields:
            KafkaConsumer instance
        """
        if self._degraded_mode:
            logger.warning(f"Connection pool in degraded mode, consumer group {group_id} may not be available")

        consumer = self._get_or_create_consumer(group_id)
        try:
            yield consumer
        finally:
            # In a real implementation, you might return the consumer to the pool
            # For now, we just ensure it's available for reuse
            pass

    def _get_or_create_consumer(self, group_id: str) -> KafkaConsumer:
        """
        Get an existing consumer or create a new one.

        Args:
            group_id: Consumer group ID

        Returns:
            KafkaConsumer instance
        """
        if group_id not in self._consumers:
            try:
                self._consumers[group_id] = KafkaConsumer(group_id)
                logger.info(f"Created new Kafka consumer for group: {group_id}")
            except Exception as e:
                logger.error(f"Failed to create Kafka consumer for group {group_id}: {str(e)}")
                # Enter degraded mode if consumer creation fails
                self._enter_degraded_mode()
                raise
        return self._consumers[group_id]

    def execute_producer_operation_with_retry(self, operation: Callable[[], Any], operation_name: str = "producer operation"):
        """
        Execute a producer operation with retry logic and graceful degradation.

        Args:
            operation: The operation to execute
            operation_name: Name of the operation for logging

        Returns:
            Result of the operation
        """
        if self._degraded_mode:
            logger.warning(f"Skipping {operation_name} due to degraded mode")
            # In a real implementation, you might queue the operation for later
            # or use an alternative storage mechanism
            return self._handle_degraded_operation(operation, operation_name)

        try:
            # Use circuit breaker for the operation
            return self._circuit_breaker.call_kafka_operation(self._retry_mechanism.execute_with_retry, operation, operation_name)
        except Exception as e:
            logger.error(f"Producer operation failed: {operation_name}, error: {str(e)}")
            # Check if we should enter degraded mode
            if self._should_enter_degraded_mode():
                self._enter_degraded_mode()
            raise

    def execute_consumer_operation_with_retry(self, operation: Callable[[], Any], operation_name: str = "consumer operation"):
        """
        Execute a consumer operation with retry logic and graceful degradation.

        Args:
            operation: The operation to execute
            operation_name: Name of the operation for logging

        Returns:
            Result of the operation
        """
        if self._degraded_mode:
            logger.warning(f"Skipping {operation_name} due to degraded mode")
            # In a real implementation, you might queue the operation for later
            # or use an alternative processing mechanism
            return self._handle_degraded_operation(operation, operation_name)

        try:
            # Use circuit breaker for the operation
            return self._circuit_breaker.call_kafka_operation(self._retry_mechanism.execute_with_retry, operation, operation_name)
        except Exception as e:
            logger.error(f"Consumer operation failed: {operation_name}, error: {str(e)}")
            # Check if we should enter degraded mode
            if self._should_enter_degraded_mode():
                self._enter_degraded_mode()
            raise

    def _handle_degraded_operation(self, operation: Callable[[], Any], operation_name: str):
        """
        Handle an operation when in degraded mode.

        Args:
            operation: The operation to handle
            operation_name: Name of the operation for logging

        Returns:
            Result of the operation (or a default value in degraded mode)
        """
        # Increment the counter for operations in degraded mode
        self._degraded_operations_count += 1

        # In a real implementation, you might:
        # 1. Store the operation in a local queue for later processing
        # 2. Return a default response
        # 3. Log the operation for later replay
        logger.info(f"Handling {operation_name} in degraded mode")

        # For now, return None as a placeholder
        return None

    def _enter_degraded_mode(self):
        """
        Enter degraded mode when Kafka connectivity issues are detected.
        """
        if not self._degraded_mode:
            self._degraded_mode = True
            logger.warning("Entering degraded mode due to Kafka connectivity issues")
            # In a real implementation, you might:
            # 1. Switch to alternative storage (local files, DB, etc.)
            # 2. Reduce operation frequency
            # 3. Alert monitoring systems

    def _exit_degraded_mode(self):
        """
        Exit degraded mode when Kafka connectivity is restored.
        """
        if self._degraded_mode:
            self._degraded_mode = False
            self._degraded_operations_count = 0
            logger.info("Exiting degraded mode, Kafka connectivity restored")

    def _should_enter_degraded_mode(self) -> bool:
        """
        Determine if the system should enter degraded mode.

        Returns:
            True if degraded mode should be entered, False otherwise
        """
        # In a real implementation, you might check:
        # 1. Number of consecutive failures
        # 2. Circuit breaker state
        # 3. External health checks
        return self._circuit_breaker.is_available == False

    def is_degraded(self) -> bool:
        """
        Check if the connection pool is in degraded mode.

        Returns:
            True if in degraded mode, False otherwise
        """
        return self._degraded_mode

    def get_status(self) -> Dict[str, Any]:
        """
        Get the status of the connection pool.

        Returns:
            Dictionary with status information
        """
        return {
            "degraded_mode": self._degraded_mode,
            "degraded_operations_count": self._degraded_operations_count,
            "max_degraded_operations": self._max_degraded_operations,
            "producer_count": len(self._producers),
            "consumer_count": len(self._consumers),
            "circuit_breaker_state": self._circuit_breaker.get_state_info()
        }

    def close_all_connections(self):
        """Close all connections in the pool."""
        for producer_id, producer in self._producers.items():
            try:
                producer.flush()
                # Note: We don't call close() here as the producer might be shared
            except Exception as e:
                logger.error(f"Error closing producer {producer_id}: {str(e)}")

        for group_id, consumer in self._consumers.items():
            try:
                consumer.close()
            except Exception as e:
                logger.error(f"Error closing consumer group {group_id}: {str(e)}")


# Global connection pool instance
connection_pool = KafkaConnectionPool()


def get_connection_pool() -> KafkaConnectionPool:
    """
    Get the global Kafka connection pool instance.

    Returns:
        KafkaConnectionPool instance
    """
    return connection_pool