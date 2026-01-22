import logging
from typing import Dict, Any, Optional
from datetime import datetime
from collections import defaultdict
import threading
import time


logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collects and manages application metrics for monitoring.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the metrics collector."""
        if hasattr(self, '_initialized'):
            return
        self._counters = defaultdict(int)
        self._histograms = defaultdict(list)
        self._gauges = {}
        self._timers = {}
        self._lock = threading.RLock()
        self._initialized = True

    def increment_counter(self, name: str, labels: Optional[Dict[str, str]] = None, value: int = 1):
        """
        Increment a counter metric.

        Args:
            name: Name of the counter
            labels: Optional labels to attach to the counter
            value: Value to increment by (default 1)
        """
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] += value

    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        Record a value in a histogram.

        Args:
            name: Name of the histogram
            value: Value to record
            labels: Optional labels to attach to the histogram
        """
        key = self._make_key(name, labels)
        with self._lock:
            self._histograms[key].append(value)

    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        Set a gauge metric to a specific value.

        Args:
            name: Name of the gauge
            value: Value to set
            labels: Optional labels to attach to the gauge
        """
        key = self._make_key(name, labels)
        with self._lock:
            self._gauges[key] = value

    def start_timer(self, name: str, labels: Optional[Dict[str, str]] = None):
        """
        Start a timer for measuring duration.

        Args:
            name: Name of the timer
            labels: Optional labels to attach to the timer
        """
        key = self._make_key(name, labels)
        self._timers[key] = time.time()

    def stop_timer(self, name: str, labels: Optional[Dict[str, str]] = None):
        """
        Stop a timer and record the duration.

        Args:
            name: Name of the timer
            labels: Optional labels to attach to the timer

        Returns:
            Elapsed time in seconds
        """
        key = self._make_key(name, labels)
        if key in self._timers:
            elapsed = time.time() - self._timers[key]
            self.record_histogram(f"{name}_duration_seconds", elapsed, labels)
            del self._timers[key]
            return elapsed
        return 0

    def get_counter_value(self, name: str, labels: Optional[Dict[str, str]] = None) -> int:
        """
        Get the current value of a counter.

        Args:
            name: Name of the counter
            labels: Labels that were attached to the counter

        Returns:
            Current value of the counter
        """
        key = self._make_key(name, labels)
        return self._counters.get(key, 0)

    def get_histogram_values(self, name: str, labels: Optional[Dict[str, str]] = None) -> list:
        """
        Get all values recorded in a histogram.

        Args:
            name: Name of the histogram
            labels: Labels that were attached to the histogram

        Returns:
            List of recorded values
        """
        key = self._make_key(name, labels)
        return self._histograms.get(key, [])

    def get_gauge_value(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """
        Get the current value of a gauge.

        Args:
            name: Name of the gauge
            labels: Labels that were attached to the gauge

        Returns:
            Current value of the gauge
        """
        key = self._make_key(name, labels)
        return self._gauges.get(key, 0.0)

    def _make_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """
        Create a unique key for a metric with labels.

        Args:
            name: Name of the metric
            labels: Optional labels to attach

        Returns:
            Unique key string
        """
        if not labels:
            return name

        # Sort labels by key to ensure consistent ordering
        sorted_labels = sorted(labels.items())
        label_str = ','.join(f"{k}={v}" for k, v in sorted_labels)
        return f"{name}{{{label_str}}}"

    def collect_all_metrics(self) -> Dict[str, Any]:
        """
        Collect all metrics for reporting.

        Returns:
            Dictionary containing all collected metrics
        """
        with self._lock:
            return {
                'counters': dict(self._counters),
                'histograms': {k: list(v) for k, v in self._histograms.items()},
                'gauges': dict(self._gauges),
                'timestamps': datetime.utcnow().isoformat()
            }

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get a summary of performance metrics.

        Returns:
            Dictionary with performance summary
        """
        with self._lock:
            # Calculate performance metrics
            total_events = sum(v for k, v in self._counters.items() if 'success' in k)
            total_errors = sum(v for k, v in self._counters.items() if 'error' in k)
            success_rate = (total_events / (total_events + total_errors)) if (total_events + total_errors) > 0 else 0

            # Calculate average processing times from histograms
            avg_processing_times = {}
            for key, values in self._histograms.items():
                if values and 'duration' in key:
                    avg_processing_times[key] = sum(values) / len(values)

            return {
                'timestamp': datetime.utcnow().isoformat(),
                'summary': {
                    'total_events_processed': total_events,
                    'total_errors': total_errors,
                    'success_rate': round(success_rate, 4),
                    'average_processing_times': avg_processing_times,
                    'active_metrics': {
                        'counters': len(self._counters),
                        'histograms': len(self._histograms),
                        'gauges': len(self._gauges)
                    }
                }
            }


# Global metrics collector instance
metrics_collector = MetricsCollector()


def increment_counter(name: str, labels: Optional[Dict[str, str]] = None, value: int = 1):
    """
    Convenience function to increment a counter.

    Args:
        name: Name of the counter
        labels: Optional labels to attach to the counter
        value: Value to increment by (default 1)
    """
    metrics_collector.increment_counter(name, labels, value)


def record_histogram(name: str, value: float, labels: Optional[Dict[str, str]] = None):
    """
    Convenience function to record a histogram value.

    Args:
        name: Name of the histogram
        value: Value to record
        labels: Optional labels to attach to the histogram
    """
    metrics_collector.record_histogram(name, value, labels)


def set_gauge(name: str, value: float, labels: Optional[Dict[str, str]] = None):
    """
    Convenience function to set a gauge value.

    Args:
        name: Name of the gauge
        value: Value to set
        labels: Optional labels to attach to the gauge
    """
    metrics_collector.set_gauge(name, value, labels)


def start_timer(name: str, labels: Optional[Dict[str, str]] = None):
    """
    Convenience function to start a timer.

    Args:
        name: Name of the timer
        labels: Optional labels to attach to the timer
    """
    metrics_collector.start_timer(name, labels)


def stop_timer(name: str, labels: Optional[Dict[str, str]] = None) -> float:
    """
    Convenience function to stop a timer and record duration.

    Args:
        name: Name of the timer
        labels: Optional labels to attach to the timer

    Returns:
        Elapsed time in seconds
    """
    return metrics_collector.stop_timer(name, labels)