"""
Comprehensive logging configuration for operational visibility.
"""
import logging
import sys
import json
from datetime import datetime
from typing import Dict, Any
import os


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as JSON.

        Args:
            record: The log record to format

        Returns:
            JSON-formatted log message
        """
        log_entry = {
            'timestamp': datetime.utcfromtimestamp(record.created).isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'pid': record.process,
            'thread': record.thread,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        # Add any extra fields that were passed to the logger
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)

        # Add any additional fields that might have been added via add_extra
        for key, value in record.__dict__.items():
            if key not in log_entry and key not in [
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'lineno', 'funcName', 'created',
                'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'getMessage', 'exc_info',
                'exc_text', 'stack_info'
            ]:
                log_entry[key] = value

        return json.dumps(log_entry)


def setup_logging(log_level: str = "INFO", log_format: str = "json", log_file: str = None):
    """
    Set up comprehensive logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format type ('json' or 'standard')
        log_file: Optional file path to write logs to
    """
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Create handler
    if log_file:
        handler = logging.FileHandler(log_file)
    else:
        handler = logging.StreamHandler(sys.stdout)

    # Set formatter based on format type
    if log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Set specific log levels for different components
    logging.getLogger("kafka").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("confluent_kafka").setLevel(logging.INFO)
    logging.getLogger("src.kafka").setLevel(numeric_level)
    logging.getLogger("src.services").setLevel(numeric_level)

    # Log startup message
    root_logger.info(
        "Logging configured",
        extra={
            "log_level": log_level,
            "log_format": log_format,
            "log_file": log_file,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with operational visibility enhancements.

    Args:
        name: Name of the logger

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Add contextual information to log records
    class ContextFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            # Add service context
            record.service_name = os.environ.get("SERVICE_NAME", "todo-chatbot")
            record.environment = os.environ.get("APP_ENV", "development")
            record.version = os.environ.get("SERVICE_VERSION", "1.0.0")
            return True

    logger.addFilter(ContextFilter())
    return logger


def log_event(
    logger: logging.Logger,
    event_type: str,
    event_data: Dict[str, Any],
    level: int = logging.INFO
):
    """
    Log a structured event for operational visibility.

    Args:
        logger: The logger instance to use
        event_type: Type of event being logged
        event_data: Data associated with the event
        level: Logging level for the event
    """
    extra_data = {
        "event_type": event_type,
        "event_data": event_data,
        "timestamp": datetime.utcnow().isoformat()
    }

    logger.log(level, f"Event: {event_type}", extra=extra_data)


def log_kafka_operation(
    logger: logging.Logger,
    operation: str,
    topic: str,
    partition: int = None,
    offset: int = None,
    success: bool = True,
    duration_ms: float = None,
    error: str = None
):
    """
    Log Kafka-specific operations for operational visibility.

    Args:
        logger: The logger instance to use
        operation: The Kafka operation being performed
        topic: The topic involved
        partition: The partition involved (optional)
        offset: The offset involved (optional)
        success: Whether the operation was successful
        duration_ms: Duration of the operation in milliseconds (optional)
        error: Error message if operation failed (optional)
    """
    extra_data = {
        "operation": operation,
        "topic": topic,
        "partition": partition,
        "offset": offset,
        "success": success,
        "duration_ms": duration_ms,
        "timestamp": datetime.utcnow().isoformat()
    }

    if error:
        extra_data["error"] = error

    message = f"Kafka {operation} on topic {topic}"
    if partition is not None:
        message += f" partition {partition}"
    if offset is not None:
        message += f" offset {offset}"

    message += f" - {'SUCCESS' if success else 'FAILED'}"

    logger.log(logging.INFO if success else logging.ERROR, message, extra=extra_data)


def log_performance_metric(
    logger: logging.Logger,
    metric_name: str,
    value: float,
    unit: str = "",
    tags: Dict[str, str] = None
):
    """
    Log performance metrics for operational visibility.

    Args:
        logger: The logger instance to use
        metric_name: Name of the metric
        value: Value of the metric
        unit: Unit of measurement
        tags: Additional tags for the metric
    """
    extra_data = {
        "metric_type": "performance",
        "metric_name": metric_name,
        "value": value,
        "unit": unit,
        "tags": tags or {},
        "timestamp": datetime.utcnow().isoformat()
    }

    logger.info(f"PERFORMANCE METRIC: {metric_name} = {value}{unit}", extra=extra_data)


# Initialize logging configuration
if __name__ == "__main__":
    setup_logging(log_level="INFO", log_format="json")
    logger = get_logger(__name__)
    logger.info("Logger initialized for testing")