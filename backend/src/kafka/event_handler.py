import abc
import logging
from typing import Dict, Any, Protocol
from .consumer import KafkaConsumer
from ..kafka.dead_letter_queue import DeadLetterQueueHandler


logger = logging.getLogger(__name__)


class EventHandler(Protocol):
    """
    Protocol defining the interface for event handlers.
    """
    def handle(self, message: Dict[str, Any]) -> None:
        """
        Handle an incoming message.

        Args:
            message: The message to handle
        """
        ...


class AbstractEventHandler(abc.ABC):
    """
    Abstract base class for event handlers that provides common functionality.
    """

    def __init__(self, dlq_handler: DeadLetterQueueHandler):
        """
        Initialize the event handler.

        Args:
            dlq_handler: Dead letter queue handler for error management
        """
        self.dlq_handler = dlq_handler

    @abc.abstractmethod
    def handle(self, message: Dict[str, Any]) -> None:
        """
        Handle an incoming message. This method must be implemented by subclasses.

        Args:
            message: The message to handle
        """
        pass

    def safe_handle(self, message: Dict[str, Any]) -> bool:
        """
        Safely handle a message with error handling and DLQ support.

        Args:
            message: The message to handle

        Returns:
            True if handled successfully, False if error occurred
        """
        try:
            self.handle(message)
            return True
        except Exception as e:
            logger.error(f"Error in event handler {self.__class__.__name__}: {str(e)}")
            self.dlq_handler.send_to_dead_letter_queue(
                message['value'],
                e,
                message['topic'],
                message.get('partition'),
                message.get('offset')
            )
            return False


class EventDispatcher:
    """
    Dispatcher that routes messages to appropriate handlers based on event type.
    """

    def __init__(self):
        """Initialize the event dispatcher."""
        self.handlers: Dict[str, EventHandler] = {}

    def register_handler(self, event_type: str, handler: EventHandler):
        """
        Register an event handler for a specific event type.

        Args:
            event_type: The type of event to handle
            handler: The handler to register
        """
        self.handlers[event_type] = handler
        logger.info(f"Registered handler for event type: {event_type}")

    def dispatch(self, message: Dict[str, Any]) -> bool:
        """
        Dispatch a message to the appropriate handler.

        Args:
            message: The message to dispatch

        Returns:
            True if handled successfully, False if no handler or error occurred
        """
        try:
            event_type = message.get('value', {}).get('eventType') or message.get('eventType')

            if not event_type:
                logger.warning(f"No event type found in message: {message}")
                return False

            handler = self.handlers.get(event_type)
            if not handler:
                logger.warning(f"No handler registered for event type: {event_type}")
                return False

            return handler.safe_handle(message)

        except Exception as e:
            logger.error(f"Error dispatching message: {str(e)}")
            return False


class BaseConsumerWithHandlers(KafkaConsumer):
    """
    Base consumer class that integrates with the event handler pattern.
    """

    def __init__(self, group_id: str, event_dispatcher: EventDispatcher):
        """
        Initialize the consumer with event dispatcher.

        Args:
            group_id: Consumer group ID
            event_dispatcher: Event dispatcher to use
        """
        super().__init__(group_id)
        self.event_dispatcher = event_dispatcher

    def start_consuming_with_handlers(self, topics: list):
        """
        Start consuming messages and dispatch them to handlers.

        Args:
            topics: List of topics to subscribe to
        """
        self.subscribe(topics)
        logger.info(f"Starting to consume messages with event handlers on topics: {topics}")

        def message_handler(message: Dict[str, Any]):
            success = self.event_dispatcher.dispatch(message)
            if success:
                logger.debug(f"Successfully processed message with event type: {message.get('value', {}).get('eventType')}")
            else:
                logger.warning(f"Failed to process message with event type: {message.get('value', {}).get('eventType')}")

        try:
            self.consume_messages(callback=message_handler)
        except KeyboardInterrupt:
            logger.info("Stopping consumer with handlers...")
        finally:
            self.close()