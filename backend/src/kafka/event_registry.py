import logging
from typing import Dict, Type, Any, Optional
from .event_schemas import BaseEventSchema
from .event_handler import AbstractEventHandler


logger = logging.getLogger(__name__)


class EventTypeRegistry:
    """
    Registry for managing event types, schemas, and handlers.
    """

    def __init__(self):
        """Initialize the event type registry."""
        self._event_types: Dict[str, Type[BaseEventSchema]] = {}
        self._handler_types: Dict[str, Type[AbstractEventHandler]] = {}
        self._event_metadata: Dict[str, Dict[str, Any]] = {}

    def register_event_type(
        self,
        event_type: str,
        schema_class: Type[BaseEventSchema],
        handler_class: Optional[Type[AbstractEventHandler]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Register a new event type with its schema and optional handler.

        Args:
            event_type: The name/type of the event
            schema_class: The schema class for this event type
            handler_class: Optional handler class for this event type
            metadata: Optional metadata about the event type
        """
        self._event_types[event_type] = schema_class

        if handler_class:
            self._handler_types[event_type] = handler_class

        self._event_metadata[event_type] = metadata or {}

        logger.info(f"Registered event type: {event_type}")

    def get_schema_class(self, event_type: str) -> Optional[Type[BaseEventSchema]]:
        """
        Get the schema class for an event type.

        Args:
            event_type: The event type to look up

        Returns:
            The schema class, or None if not found
        """
        return self._event_types.get(event_type)

    def get_handler_class(self, event_type: str) -> Optional[Type[AbstractEventHandler]]:
        """
        Get the handler class for an event type.

        Args:
            event_type: The event type to look up

        Returns:
            The handler class, or None if not found
        """
        return self._handler_types.get(event_type)

    def get_event_metadata(self, event_type: str) -> Dict[str, Any]:
        """
        Get metadata for an event type.

        Args:
            event_type: The event type to look up

        Returns:
            Metadata dictionary for the event type
        """
        return self._event_metadata.get(event_type, {})

    def validate_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        Validate event data against its schema.

        Args:
            event_type: The type of event to validate
            event_data: The event data to validate

        Returns:
            True if valid, False otherwise
        """
        schema_class = self.get_schema_class(event_type)
        if not schema_class:
            logger.error(f"No schema registered for event type: {event_type}")
            return False

        try:
            # Create an instance of the schema to validate
            schema_class(**event_data)
            return True
        except Exception as e:
            logger.error(f"Event validation failed for type {event_type}: {str(e)}")
            return False

    def list_registered_events(self) -> list:
        """
        List all registered event types.

        Returns:
            List of registered event type names
        """
        return list(self._event_types.keys())

    def is_event_type_registered(self, event_type: str) -> bool:
        """
        Check if an event type is registered.

        Args:
            event_type: The event type to check

        Returns:
            True if registered, False otherwise
        """
        return event_type in self._event_types


# Global instance of the event registry
event_registry = EventTypeRegistry()


def register_event(
    event_type: str,
    schema_class: Type[BaseEventSchema],
    handler_class: Optional[Type[AbstractEventHandler]] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Decorator function to register an event type.

    Args:
        event_type: The name/type of the event
        schema_class: The schema class for this event type
        handler_class: Optional handler class for this event type
        metadata: Optional metadata about the event type
    """
    event_registry.register_event_type(event_type, schema_class, handler_class, metadata)
    return schema_class