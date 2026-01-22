import logging
import threading
import time
from typing import List, Dict, Optional, Callable
from .consumer import KafkaConsumer
from .producer import KafkaProducer
from .config import get_kafka_consumer_config
from ..monitoring.metrics import increment_counter, record_histogram


logger = logging.getLogger(__name__)


class MultiConsumerManager:
    """
    Manager for handling multiple consumers per group with partition alignment.
    """

    def __init__(self, group_id: str, num_consumers: int = 1):
        """
        Initialize the multi-consumer manager.

        Args:
            group_id: Consumer group ID
            num_consumers: Number of consumers to create for the group
        """
        self.group_id = group_id
        self.num_consumers = num_consumers
        self.consumers: List[KafkaConsumer] = []
        self.consumer_threads: List[threading.Thread] = []
        self.running = False
        self.message_processors: List[Callable] = []

        # Create multiple consumers for the group
        for i in range(num_consumers):
            consumer = KafkaConsumer(group_id=f"{group_id}-consumer-{i}")
            self.consumers.append(consumer)

        logger.info(f"Initialized MultiConsumerManager with {num_consumers} consumers for group {group_id}")

    def add_message_processor(self, processor_func: Callable[[Dict], None]):
        """
        Add a message processor function to handle consumed messages.

        Args:
            processor_func: Function that takes a message dict and processes it
        """
        self.message_processors.append(processor_func)

    def _consumer_worker(self, consumer: KafkaConsumer, topics: List[str], worker_id: int):
        """
        Worker function for a single consumer thread.

        Args:
            consumer: The consumer instance
            topics: Topics to subscribe to
            worker_id: ID of this worker thread
        """
        logger.info(f"Starting consumer worker {worker_id} for group {self.group_id}")

        try:
            consumer.subscribe(topics)

            def message_callback(message: Dict):
                # Process the message with all registered processors
                for processor in self.message_processors:
                    try:
                        start_time = time.time()
                        processor(message)
                        end_time = time.time()

                        # Record processing time
                        processing_time = end_time - start_time
                        record_histogram(
                            "multi_consumer_message_processing_time_seconds",
                            processing_time,
                            {"worker_id": str(worker_id), "topic": message.get('topic', 'unknown')}
                        )

                        # Increment success counter
                        increment_counter(
                            "multi_consumer_messages_processed_total",
                            {"worker_id": str(worker_id), "topic": message.get('topic', 'unknown')}
                        )
                    except Exception as e:
                        logger.error(f"Error processing message in worker {worker_id}: {str(e)}")
                        increment_counter(
                            "multi_consumer_message_processing_error_total",
                            {"worker_id": str(worker_id), "error_type": type(e).__name__}
                        )

            # Start consuming messages
            while self.running:
                consumer.running = self.running
                # Using a shorter timeout to allow for graceful shutdown
                msg = consumer.poll(timeout=1.0)

                if msg is None:
                    continue

                if msg.error():
                    logger.error(f"Consumer worker {worker_id} error: {msg.error()}")
                    increment_counter(
                        "multi_consumer_error_total",
                        {"worker_id": str(worker_id), "error_type": "poll_error"}
                    )
                    continue

                try:
                    # Deserialize the message value
                    from .serialization import deserialize_message
                    message_value = deserialize_message(msg.value().decode('utf-8'))

                    # Create message dict with metadata
                    message_dict = {
                        'value': message_value,
                        'key': msg.key().decode('utf-8') if msg.key() else None,
                        'topic': msg.topic(),
                        'partition': msg.partition(),
                        'offset': msg.offset(),
                        'timestamp': msg.timestamp()[1],
                        'headers': {h[0]: h[1].decode('utf-8') for h in msg.headers()} if msg.headers() else None,
                        'worker_id': worker_id  # Track which worker processed this
                    }

                    # Process the message
                    message_callback(message_dict)

                    # Commit the offset after successful processing
                    consumer._consumer.commit(msg)

                except Exception as e:
                    logger.error(f"Error in consumer worker {worker_id} processing message: {str(e)}")
                    increment_counter(
                        "multi_consumer_message_processing_error_total",
                        {"worker_id": str(worker_id), "error_type": type(e).__name__}
                    )

                    # Handle the error (could send to DLQ)
                    consumer.handle_message_error(msg, e)

        except Exception as e:
            logger.error(f"Consumer worker {worker_id} crashed: {str(e)}")
            increment_counter(
                "multi_consumer_crash_total",
                {"worker_id": str(worker_id), "error_type": type(e).__name__}
            )
        finally:
            logger.info(f"Consumer worker {worker_id} stopped")

    def start_consumers(self, topics: List[str]):
        """
        Start all consumer threads.

        Args:
            topics: List of topics to subscribe to
        """
        if self.running:
            logger.warning("Consumers are already running")
            return

        self.running = True

        for i, consumer in enumerate(self.consumers):
            thread = threading.Thread(
                target=self._consumer_worker,
                args=(consumer, topics, i),
                daemon=True,
                name=f"KafkaConsumer-{self.group_id}-{i}"
            )
            thread.start()
            self.consumer_threads.append(thread)

        logger.info(f"Started {len(self.consumer_threads)} consumer threads for group {self.group_id}")

    def stop_consumers(self, timeout: Optional[float] = 30.0):
        """
        Stop all consumer threads gracefully.

        Args:
            timeout: Timeout in seconds to wait for threads to finish
        """
        if not self.running:
            logger.info("Consumers are already stopped")
            return

        logger.info(f"Stopping {len(self.consumer_threads)} consumer threads for group {self.group_id}")

        self.running = False

        # Set running to False for each consumer
        for consumer in self.consumers:
            consumer.running = False

        # Wait for all threads to finish
        for thread in self.consumer_threads:
            thread.join(timeout=timeout)
            if thread.is_alive():
                logger.warning(f"Thread {thread.name} did not stop within timeout")

        # Close all consumers
        for consumer in self.consumers:
            try:
                consumer.close()
            except Exception as e:
                logger.error(f"Error closing consumer: {str(e)}")

        self.consumer_threads.clear()
        logger.info("All consumer threads stopped")

    def get_consumer_status(self) -> List[Dict]:
        """
        Get status information for all consumers.

        Returns:
            List of status dictionaries for each consumer
        """
        statuses = []
        for i, consumer in enumerate(self.consumers):
            status = {
                "worker_id": i,
                "group_id": consumer._consumer.group_id() if hasattr(consumer._consumer, 'group_id') else self.group_id,
                "assigned_partitions": list(consumer.assigned_partitions),
                "is_active": self.running
            }
            statuses.append(status)
        return statuses

    def get_performance_metrics(self) -> Dict:
        """
        Get performance metrics for the consumer group.

        Returns:
            Dictionary with performance metrics
        """
        # In a real implementation, this would aggregate metrics from monitoring system
        # For now, returning placeholder metrics
        return {
            "total_consumers": len(self.consumers),
            "active_consumers": len([t for t in self.consumer_threads if t.is_alive()]),
            "group_id": self.group_id
        }


class PartitionAlignmentHelper:
    """
    Helper class for managing partition alignment strategies.
    """

    @staticmethod
    def calculate_optimal_consumer_count(topic_partitions: int, target_partitions_per_consumer: int = 6) -> int:
        """
        Calculate the optimal number of consumers based on partition count.

        Args:
            topic_partitions: Number of partitions in the topic
            target_partitions_per_consumer: Target number of partitions per consumer

        Returns:
            Optimal number of consumers
        """
        if topic_partitions <= 0:
            return 1

        # Aim for roughly equal distribution, with no more than target_partitions_per_consumer per consumer
        optimal_count = max(1, topic_partitions // target_partitions_per_consumer)

        # Ensure we don't have too few consumers for many partitions
        if topic_partitions > optimal_count * target_partitions_per_consumer:
            optimal_count = min(topic_partitions, optimal_count + 1)

        return max(1, optimal_count)

    @staticmethod
    def get_partition_assignment(consumer_id: int, total_consumers: int, total_partitions: int) -> List[int]:
        """
        Get the partition assignment for a specific consumer.

        Args:
            consumer_id: ID of the consumer (0-indexed)
            total_consumers: Total number of consumers in the group
            total_partitions: Total number of partitions in the topic

        Returns:
            List of partition numbers assigned to this consumer
        """
        if total_partitions <= 0 or total_consumers <= 0:
            return []

        partitions_per_consumer = total_partitions // total_consumers
        extra_partitions = total_partitions % total_consumers

        start_partition = consumer_id * partitions_per_consumer + min(consumer_id, extra_partitions)
        end_partition = start_partition + partitions_per_consumer + (1 if consumer_id < extra_partitions else 0)

        return list(range(start_partition, min(end_partition, total_partitions)))