"""
Metrics collection for Kafka integration monitoring.
"""
import time
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge
from enum import Enum


class MetricType(Enum):
    """
    Enum for different metric types.
    """
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


# Define metrics
kafka_events_total = Counter(
    'kafka_events_total',
    'Total number of Kafka events processed',
    ['event_type', 'topic', 'result']
)

kafka_event_processing_duration = Histogram(
    'kafka_event_processing_duration_seconds',
    'Time spent processing Kafka events',
    ['event_type', 'topic']
)

kafka_producer_errors_total = Counter(
    'kafka_producer_errors_total',
    'Total number of Kafka producer errors',
    ['error_type', 'topic']
)

kafka_consumer_errors_total = Counter(
    'kafka_consumer_errors_total',
    'Total number of Kafka consumer errors',
    ['error_type', 'topic']
)

dlq_events_total = Counter(
    'dlq_events_total',
    'Total number of events sent to dead letter queue',
    ['topic', 'error_type']
)

kafka_producer_batch_size = Histogram(
    'kafka_producer_batch_size',
    'Size of message batches sent by Kafka producer',
    ['topic']
)

kafka_consumer_lag = Gauge(
    'kafka_consumer_lag',
    'Current lag of Kafka consumer',
    ['group_id', 'topic', 'partition']
)

kafka_connection_status = Gauge(
    'kafka_connection_status',
    'Status of Kafka connection (1=connected, 0=disconnected)',
    ['client_type']
)


def increment_counter(metric_name: str, labels: Optional[Dict[str, str]] = None):
    """
    Increment a counter metric.

    Args:
        metric_name: Name of the metric to increment
        labels: Optional labels to attach to the metric
    """
    if metric_name == 'kafka_events_total':
        kafka_events_total.labels(**(labels or {})).inc()
    elif metric_name == 'kafka_producer_errors_total':
        kafka_producer_errors_total.labels(**(labels or {})).inc()
    elif metric_name == 'kafka_consumer_errors_total':
        kafka_consumer_errors_total.labels(**(labels or {})).inc()
    elif metric_name == 'dlq_events_total':
        dlq_events_total.labels(**(labels or {})).inc()
    # Use actual defined metric names
    elif metric_name == 'kafka_events_processed_total':
        kafka_events_total.labels(**(labels or {})).inc()
    elif metric_name == 'kafka_producer_error_total':
        kafka_producer_errors_total.labels(**(labels or {})).inc()
    elif metric_name == 'kafka_consumer_error_total':
        kafka_consumer_errors_total.labels(**(labels or {})).inc()
    elif metric_name == 'dlq_events_total' or metric_name == 'dlq_events_sent_total':
        dlq_events_total.labels(**(labels or {})).inc()


def record_histogram(metric_name: str, value: float, labels: Optional[Dict[str, str]] = None):
    """
    Record a value in a histogram metric.

    Args:
        metric_name: Name of the histogram metric
        value: Value to record
        labels: Optional labels to attach to the metric
    """
    if metric_name == 'kafka_event_processing_duration_seconds':
        kafka_event_processing_duration.labels(**(labels or {})).observe(value)
    elif metric_name == 'kafka_producer_batch_size':
        kafka_producer_batch_size.labels(**(labels or {})).observe(value)


def set_gauge(metric_name: str, value: float, labels: Optional[Dict[str, str]] = None):
    """
    Set a gauge metric to a specific value.

    Args:
        metric_name: Name of the gauge metric
        value: Value to set
        labels: Optional labels to attach to the metric
    """
    if metric_name == 'kafka_consumer_lag':
        kafka_consumer_lag.labels(**(labels or {})).set(value)
    elif metric_name == 'kafka_connection_status':
        kafka_connection_status.labels(**(labels or {})).set(value)


def start_timer() -> float:
    """
    Start a timer for measuring durations.

    Returns:
        Start time in seconds since epoch
    """
    return time.time()


def stop_timer(start_time: float) -> float:
    """
    Stop a timer and return the elapsed time.

    Args:
        start_time: Start time from start_timer()

    Returns:
        Elapsed time in seconds
    """
    return time.time() - start_time
