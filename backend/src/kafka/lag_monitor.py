import logging
import threading
import time
from typing import Dict, List, Optional, Any
from confluent_kafka import Consumer, TopicPartition
from ..monitoring.metrics import increment_counter, record_histogram, set_gauge
from .config import get_kafka_consumer_config


logger = logging.getLogger(__name__)


class ConsumerLagMonitor:
    """
    Monitors consumer lag and provides alerting capabilities.
    """

    def __init__(self, group_id: str, topics: List[str], check_interval: int = 30):
        """
        Initialize the consumer lag monitor.

        Args:
            group_id: Consumer group ID to monitor
            topics: List of topics to monitor
            check_interval: Interval in seconds between checks
        """
        self.group_id = group_id
        self.topics = topics
        self.check_interval = check_interval
        self.running = False
        self.monitor_thread = None
        self.lag_threshold = 1000  # Alert if lag exceeds this threshold
        self.last_lag_values = {}

        # Create admin consumer to get lag information
        config = get_kafka_consumer_config(group_id)
        config['enable.auto.commit'] = False
        config['enable.partition.eof'] = False
        config['group.id'] = f"lag-monitor-{group_id}"

        self.admin_consumer = Consumer(config)
        logger.info(f"Initialized consumer lag monitor for group: {group_id}")

    def start_monitoring(self):
        """
        Start monitoring consumer lag in a background thread.
        """
        if self.running:
            logger.warning("Lag monitor is already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info(f"Started consumer lag monitoring for group: {self.group_id}")

    def stop_monitoring(self):
        """
        Stop monitoring consumer lag.
        """
        if not self.running:
            logger.info("Lag monitor is already stopped")
            return

        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            logger.info("Consumer lag monitoring stopped")

        if self.admin_consumer:
            self.admin_consumer.close()

    def _monitor_loop(self):
        """
        Main monitoring loop that runs in a background thread.
        """
        while self.running:
            try:
                self._check_consumer_lag()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in lag monitoring loop: {str(e)}")
                time.sleep(min(5, self.check_interval))  # Brief pause before retrying

    def _check_consumer_lag(self):
        """
        Check the consumer lag for all monitored topics.
        """
        try:
            # Get the list of topic partitions for this consumer group
            assignments = self.admin_consumer.assignment()

            # If no assignments, try to get them by querying the group
            if not assignments:
                # Subscribe temporarily to get assignments
                self.admin_consumer.subscribe(self.topics)

                # Poll once to trigger assignment
                self.admin_consumer.poll(timeout=1.0)

                assignments = self.admin_consumer.assignment()

            if not assignments:
                logger.warning(f"No partitions assigned to consumer group: {self.group_id}")
                return

            total_lag = 0

            for tp in assignments:
                # Get the current position (offset) of the consumer
                try:
                    committed_position = self.admin_consumer.committed([tp], timeout=5)[0].offset
                except Exception:
                    # If no committed offset, set to beginning
                    committed_position = -1001  # Special value indicating no committed offset

                # Get the high watermark (latest offset) for the partition
                try:
                    _, high_watermark = self.admin_consumer.get_watermark_offsets(tp, timeout=5)
                except Exception as e:
                    logger.warning(f"Could not get watermark offsets for {tp}: {str(e)}")
                    continue

                # Calculate lag
                if committed_position >= 0:
                    lag = max(0, high_watermark - committed_position)
                else:
                    # If no committed offset, lag is the entire partition
                    lag = high_watermark if high_watermark > 0 else 0

                # Store the lag value
                partition_key = f"{tp.topic}[{tp.partition}]"
                self.last_lag_values[partition_key] = lag
                total_lag += lag

                # Record individual partition lag
                record_histogram("kafka_consumer_lag_messages", lag, {
                    "topic": tp.topic,
                    "partition": str(tp.partition),
                    "group": self.group_id
                })

                # Set gauge for partition lag
                set_gauge("kafka_consumer_lag_current", lag, {
                    "topic": tp.topic,
                    "partition": str(tp.partition),
                    "group": self.group_id
                })

                # Check if lag exceeds threshold
                if lag > self.lag_threshold:
                    logger.warning(
                        f"High consumer lag detected: {partition_key} in group {self.group_id} has lag of {lag} messages"
                    )

                    # Increment alert counter
                    increment_counter("kafka_consumer_lag_high_alerts_total", {
                        "topic": tp.topic,
                        "partition": str(tp.partition),
                        "group": self.group_id,
                        "lag": str(lag)
                    })

            # Record total lag for the group
            set_gauge("kafka_consumer_group_lag_total", total_lag, {
                "group": self.group_id
            })

            logger.debug(f"Consumer group {self.group_id} total lag: {total_lag} messages across {len(assignments)} partitions")

        except Exception as e:
            logger.error(f"Error checking consumer lag: {str(e)}")
            # Increment error counter
            increment_counter("kafka_lag_monitor_error_total", {
                "group": self.group_id,
                "error_type": type(e).__name__
            })

    def get_current_lag(self) -> Dict[str, int]:
        """
        Get the current lag values for all monitored partitions.

        Returns:
            Dictionary mapping partition keys to lag values
        """
        return self.last_lag_values.copy()

    def get_lag_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current lag situation.

        Returns:
            Dictionary with lag summary information
        """
        current_lag = self.get_current_lag()

        if not current_lag:
            return {
                "total_lag": 0,
                "max_lag": 0,
                "avg_lag": 0,
                "partitions_monitored": 0,
                "partitions_with_lag": 0,
                "lag_exceeding_threshold": 0
            }

        total_lag = sum(current_lag.values())
        max_lag = max(current_lag.values()) if current_lag else 0
        avg_lag = total_lag / len(current_lag) if current_lag else 0
        partitions_with_lag = sum(1 for lag in current_lag.values() if lag > 0)
        lag_exceeding_threshold = sum(1 for lag in current_lag.values() if lag > self.lag_threshold)

        return {
            "total_lag": total_lag,
            "max_lag": max_lag,
            "avg_lag": avg_lag,
            "partitions_monitored": len(current_lag),
            "partitions_with_lag": partitions_with_lag,
            "lag_exceeding_threshold": lag_exceeding_threshold,
            "timestamp": time.time()
        }

    def set_lag_threshold(self, threshold: int):
        """
        Set the threshold for lag alerting.

        Args:
            threshold: New threshold value
        """
        logger.info(f"Setting lag threshold to {threshold} for group {self.group_id}")
        self.lag_threshold = threshold


class GlobalLagMonitor:
    """
    Global monitor for tracking multiple consumer groups.
    """

    def __init__(self):
        """Initialize the global lag monitor."""
        self.monitors: Dict[str, ConsumerLagMonitor] = {}
        self._lock = threading.Lock()

    def add_monitor(self, group_id: str, topics: List[str], check_interval: int = 30):
        """
        Add a new consumer group to monitor.

        Args:
            group_id: Consumer group ID to monitor
            topics: List of topics to monitor
            check_interval: Interval in seconds between checks
        """
        with self._lock:
            if group_id not in self.monitors:
                monitor = ConsumerLagMonitor(group_id, topics, check_interval)
                self.monitors[group_id] = monitor
                logger.info(f"Added lag monitor for group: {group_id}")
            else:
                logger.warning(f"Lag monitor already exists for group: {group_id}")

    def start_all_monitors(self):
        """Start all registered monitors."""
        for group_id, monitor in self.monitors.items():
            try:
                monitor.start_monitoring()
            except Exception as e:
                logger.error(f"Failed to start monitor for group {group_id}: {str(e)}")

    def stop_all_monitors(self):
        """Stop all registered monitors."""
        for group_id, monitor in self.monitors.items():
            try:
                monitor.stop_monitoring()
            except Exception as e:
                logger.error(f"Failed to stop monitor for group {group_id}: {str(e)}")

        with self._lock:
            self.monitors.clear()

    def get_global_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all monitored consumer groups.

        Returns:
            Dictionary with global lag summary
        """
        summary = {
            "groups_monitored": len(self.monitors),
            "group_details": {},
            "timestamp": time.time()
        }

        for group_id, monitor in self.monitors.items():
            try:
                group_summary = monitor.get_lag_summary()
                summary["group_details"][group_id] = group_summary
            except Exception as e:
                logger.error(f"Failed to get summary for group {group_id}: {str(e)}")

        return summary


# Global lag monitor instance
global_lag_monitor = GlobalLagMonitor()