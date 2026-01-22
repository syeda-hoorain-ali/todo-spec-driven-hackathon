import time
import logging
from enum import Enum
from typing import Callable, Any, Optional, Dict
from datetime import datetime


logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """
    Possible states of the circuit breaker.
    """
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for Kafka connectivity.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize the circuit breaker.

        Args:
            name: Name of the circuit breaker for identification
            failure_threshold: Number of consecutive failures before opening the circuit
            timeout: Time in seconds to wait before transitioning to half-open state
            expected_exception: Type of exception that triggers failure count
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception

        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        self._last_attempt_time = None

        logger.info(f"Circuit breaker '{name}' initialized with threshold={failure_threshold}, timeout={timeout}s")

    def call(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Call the provided function through the circuit breaker.

        Args:
            func: The function to call
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            The result of the function call

        Raises:
            Exception: If the circuit is open or if the function raises an exception
        """
        if self._state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self._state = CircuitBreakerState.HALF_OPEN
                logger.info(f"Circuit breaker '{self.name}' transitioning to HALF_OPEN state")
            else:
                logger.warning(f"Circuit breaker '{self.name}' is OPEN, rejecting call")
                raise Exception(f"Circuit breaker '{self.name}' is OPEN")

        if self._state == CircuitBreakerState.HALF_OPEN:
            self._last_attempt_time = time.time()

        try:
            result = func(*args, **kwargs)

            # Success case
            if self._state == CircuitBreakerState.HALF_OPEN:
                logger.info(f"Circuit breaker '{self.name}' reset after successful call")
                self._reset()
            elif self._state == CircuitBreakerState.CLOSED:
                # Reset failure count on success if in closed state
                self._failure_count = 0

            return result

        except self.expected_exception as e:
            # Failure case
            self._record_failure()
            logger.error(f"Circuit breaker '{self.name}' recorded failure: {str(e)}")
            raise

    def _should_attempt_reset(self) -> bool:
        """
        Check if enough time has passed to attempt resetting the circuit.

        Returns:
            True if reset should be attempted, False otherwise
        """
        if self._last_failure_time is None:
            return False

        return (time.time() - self._last_failure_time) >= self.timeout

    def _record_failure(self):
        """
        Record a failure and update the circuit breaker state accordingly.
        """
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == CircuitBreakerState.HALF_OPEN:
            # If failure occurs in half-open state, go back to open
            self._state = CircuitBreakerState.OPEN
            logger.warning(f"Circuit breaker '{self.name}' returned to OPEN state after failed attempt")
        elif self._failure_count >= self.failure_threshold:
            # If threshold is reached in closed state, open the circuit
            self._state = CircuitBreakerState.OPEN
            logger.warning(f"Circuit breaker '{self.name}' opened after {self.failure_threshold} failures")
        else:
            logger.debug(f"Circuit breaker '{self.name}' failure count: {self._failure_count}/{self.failure_threshold}")

    def _reset(self):
        """
        Reset the circuit breaker to closed state.
        """
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        self._last_attempt_time = None
        logger.info(f"Circuit breaker '{self.name}' reset to CLOSED state")

    def get_state_info(self) -> Dict[str, Any]:
        """
        Get information about the current state of the circuit breaker.

        Returns:
            Dictionary with state information
        """
        return {
            "name": self.name,
            "state": self._state.value,
            "failure_count": self._failure_count,
            "failure_threshold": self.failure_threshold,
            "timeout": self.timeout,
            "last_failure_time": self._last_failure_time,
            "last_attempt_time": self._last_attempt_time,
            "time_remaining_until_reset": max(0, self.timeout - (time.time() - self._last_failure_time)) if self._last_failure_time else 0
        }

    @property
    def state(self) -> CircuitBreakerState:
        """Get the current state of the circuit breaker."""
        return self._state

    @property
    def is_closed(self) -> bool:
        """Check if the circuit breaker is in closed state."""
        return self._state == CircuitBreakerState.CLOSED

    @property
    def is_open(self) -> bool:
        """Check if the circuit breaker is in open state."""
        return self._state == CircuitBreakerState.OPEN

    @property
    def is_half_open(self) -> bool:
        """Check if the circuit breaker is in half-open state."""
        return self._state == CircuitBreakerState.HALF_OPEN


class KafkaCircuitBreaker:
    """
    Specialized circuit breaker for Kafka operations.
    """

    def __init__(self, name: str = "kafka-connection", **kwargs):
        """
        Initialize the Kafka circuit breaker.

        Args:
            name: Name of the circuit breaker
            **kwargs: Additional arguments to pass to the base CircuitBreaker
        """
        self.circuit_breaker = CircuitBreaker(name=name, expected_exception=Exception, **kwargs)

    def call_kafka_operation(self, operation: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Call a Kafka operation through the circuit breaker.

        Args:
            operation: The Kafka operation to perform
            *args: Arguments to pass to the operation
            **kwargs: Keyword arguments to pass to the operation

        Returns:
            The result of the operation
        """
        return self.circuit_breaker.call(operation, *args, **kwargs)

    def get_state_info(self) -> Dict[str, Any]:
        """Get state information for the Kafka circuit breaker."""
        return self.circuit_breaker.get_state_info()

    @property
    def is_available(self) -> bool:
        """Check if Kafka is available based on circuit breaker state."""
        return self.circuit_breaker.is_closed or self.circuit_breaker.is_half_open


# Global Kafka circuit breaker instance
kafka_circuit_breaker = KafkaCircuitBreaker()