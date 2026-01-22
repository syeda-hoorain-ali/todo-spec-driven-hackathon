import logging
from typing import Dict, Type, Any, Optional
from .consumer import KafkaConsumer
from .event_handler import EventDispatcher, BaseConsumerWithHandlers
from .event_registry import event_registry


logger = logging.getLogger(__name__)


class ConsumerFactory:
    """
    Factory for creating and managing Kafka consumers dynamically.
    """

    def __init__(self):
        """Initialize the consumer factory."""
        self._consumer_types: Dict[str, Type[KafkaConsumer]] = {}
        self._created_consumers: Dict[str, KafkaConsumer] = {}

    def register_consumer_type(self, name: str, consumer_class: Type[KafkaConsumer]):
        """
        Register a consumer type with the factory.

        Args:
            name: Name to identify the consumer type
            consumer_class: The consumer class to register
        """
        self._consumer_types[name] = consumer_class
        logger.info(f"Registered consumer type: {name}")

    def create_consumer(
        self,
        consumer_type: str,
        group_id: str,
        topics: Optional[list] = None,
        **kwargs
    ) -> KafkaConsumer:
        """
        Create a new consumer instance.

        Args:
            consumer_type: Type of consumer to create
            group_id: Consumer group ID
            topics: Optional list of topics to subscribe to
            **kwargs: Additional arguments to pass to consumer

        Returns:
            A new consumer instance
        """
        if consumer_type not in self._consumer_types:
            raise ValueError(f"Unknown consumer type: {consumer_type}")

        consumer_class = self._consumer_types[consumer_type]
        consumer = consumer_class(group_id=group_id, **kwargs)

        # Subscribe to topics if provided
        if topics:
            consumer.subscribe(topics)

        # Generate a unique ID for the consumer
        consumer_id = f"{consumer_type}_{group_id}_{len(self._created_consumers)}"
        self._created_consumers[consumer_id] = consumer

        logger.info(f"Created consumer {consumer_id} of type {consumer_type} in group {group_id}")

        return consumer

    def create_consumer_with_handlers(
        self,
        group_id: str,
        topics: list,
        event_dispatcher: Optional[EventDispatcher] = None
    ) -> BaseConsumerWithHandlers:
        """
        Create a consumer that uses the event handler pattern.

        Args:
            group_id: Consumer group ID
            topics: List of topics to subscribe to
            event_dispatcher: Optional event dispatcher (creates new one if not provided)

        Returns:
            A consumer instance with event handler support
        """
        if event_dispatcher is None:
            event_dispatcher = EventDispatcher()

        consumer = BaseConsumerWithHandlers(
            group_id=group_id,
            event_dispatcher=event_dispatcher
        )

        # Subscribe to topics
        consumer.subscribe(topics)

        # Generate a unique ID for the consumer
        consumer_id = f"handler_consumer_{group_id}_{len(self._created_consumers)}"
        self._created_consumers[consumer_id] = consumer

        logger.info(f"Created handler consumer {consumer_id} in group {group_id}")

        return consumer

    def get_consumer(self, consumer_id: str) -> Optional[KafkaConsumer]:
        """
        Get a consumer by its ID.

        Args:
            consumer_id: The ID of the consumer to retrieve

        Returns:
            The consumer instance or None if not found
        """
        return self._created_consumers.get(consumer_id)

    def close_consumer(self, consumer_id: str):
        """
        Close and remove a consumer.

        Args:
            consumer_id: The ID of the consumer to close
        """
        if consumer_id in self._created_consumers:
            consumer = self._created_consumers[consumer_id]
            consumer.close()
            del self._created_consumers[consumer_id]
            logger.info(f"Closed consumer {consumer_id}")

    def close_all_consumers(self):
        """Close all created consumers."""
        for consumer_id, consumer in list(self._created_consumers.items()):
            try:
                consumer.close()
                logger.info(f"Closed consumer {consumer_id}")
            except Exception as e:
                logger.error(f"Error closing consumer {consumer_id}: {str(e)}")

        self._created_consumers.clear()

    def list_consumers(self) -> list:
        """
        List all created consumer IDs.

        Returns:
            List of consumer IDs
        """
        return list(self._created_consumers.keys())


class ConsumerManager:
    """
    Manager for coordinating multiple consumers and their lifecycle.
    """

    def __init__(self):
        """Initialize the consumer manager."""
        self.factory = ConsumerFactory()
        self.running_consumers: Dict[str, KafkaConsumer] = {}

    def create_and_start_consumer(
        self,
        consumer_type: str,
        group_id: str,
        topics: list,
        **kwargs
    ) -> str:
        """
        Create and start a consumer.

        Args:
            consumer_type: Type of consumer to create
            group_id: Consumer group ID
            topics: List of topics to subscribe to
            **kwargs: Additional arguments to pass to consumer

        Returns:
            Consumer ID
        """
        consumer = self.factory.create_consumer(consumer_type, group_id, topics, **kwargs)
        consumer_id = [cid for cid, c in self.factory._created_consumers.items() if c is consumer][0]

        # Store in running consumers
        self.running_consumers[consumer_id] = consumer

        logger.info(f"Started consumer {consumer_id}")

        return consumer_id

    def stop_consumer(self, consumer_id: str):
        """
        Stop and close a consumer.

        Args:
            consumer_id: The ID of the consumer to stop
        """
        if consumer_id in self.running_consumers:
            consumer = self.running_consumers[consumer_id]
            consumer.close()
            del self.running_consumers[consumer_id]
            logger.info(f"Stopped consumer {consumer_id}")

    def stop_all_consumers(self):
        """Stop all running consumers."""
        for consumer_id in list(self.running_consumers.keys()):
            self.stop_consumer(consumer_id)

    def get_running_consumer_ids(self) -> list:
        """
        Get IDs of all running consumers.

        Returns:
            List of running consumer IDs
        """
        return list(self.running_consumers.keys())


# Global consumer factory and manager instances
consumer_factory = ConsumerFactory()
consumer_manager = ConsumerManager()