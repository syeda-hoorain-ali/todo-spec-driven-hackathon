import json
import logging
import pickle
import gzip
import zlib
import orjson  # Import orjson for faster serialization if available
from typing import Any, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


logger = logging.getLogger(__name__)


class DateTimeEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle datetime and date objects.
    """
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, Enum):
            return obj.value
        return super().default(obj)


def serialize_message(message: Any) -> str:
    """
    Serialize a message to JSON string format with optimization for throughput.

    Args:
        message: The message object to serialize

    Returns:
        Serialized JSON string representation of the message
    """
    try:
        # Use orjson for faster serialization if available, otherwise fallback to json
        try:
            # orjson.dumps returns bytes, decode to string
            return orjson.dumps(message).decode('utf-8')
        except (NameError, TypeError):
            # Fallback to standard json if orjson is not available
            return json.dumps(message, cls=DateTimeEncoder, ensure_ascii=False)
    except TypeError as e:
        logger.error(f"Failed to serialize message: {str(e)}")
        raise


def deserialize_message(message_str: str) -> Any:
    """
    Deserialize a JSON string to a Python object with optimization for throughput.

    Args:
        message_str: The JSON string to deserialize

    Returns:
        Deserialized Python object
    """
    try:
        # Use orjson for faster deserialization if available, otherwise fallback to json
        try:
            # orjson.loads expects string input
            return orjson.loads(message_str)
        except (NameError, TypeError):
            # Fallback to standard json if orjson is not available
            return json.loads(message_str)
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to deserialize message: {str(e)}")
        raise


def serialize_message_binary(message: Any) -> bytes:
    """
    Serialize a message to binary format for even better performance.

    Args:
        message: The message object to serialize

    Returns:
        Serialized binary representation of the message
    """
    try:
        # Use pickle for binary serialization (faster than JSON for complex objects)
        return pickle.dumps(message)
    except Exception as e:
        logger.error(f"Failed to serialize message to binary: {str(e)}")
        raise


def deserialize_message_binary(message_bytes: bytes) -> Any:
    """
    Deserialize a binary message to a Python object.

    Args:
        message_bytes: The binary message to deserialize

    Returns:
        Deserialized Python object
    """
    try:
        return pickle.loads(message_bytes)
    except Exception as e:
        logger.error(f"Failed to deserialize binary message: {str(e)}")
        raise


class SerializationOptimizer:
    """
    Optimizer for message serialization with configurable strategies.
    """
    def __init__(self, serialization_format: str = "json", compression_enabled: bool = True, compression_algorithm: str = "gzip"):
        """
        Initialize the optimizer.

        Args:
            serialization_format: Format to use ('json', 'binary', 'orjson')
            compression_enabled: Whether to enable compression
            compression_algorithm: Algorithm to use ('gzip', 'zlib', 'none')
        """
        self.format = serialization_format.lower()
        self.compression_enabled = compression_enabled
        self.compression_algorithm = compression_algorithm.lower()

    def serialize(self, message: Any) -> Union[str, bytes]:
        """
        Serialize a message using the configured format.

        Args:
            message: The message to serialize

        Returns:
            Serialized message
        """
        # First serialize the message
        if self.format == "binary":
            serialized_data = serialize_message_binary(message)
        elif self.format == "orjson":
            try:
                serialized_data = orjson.dumps(message)
            except NameError:
                # Fall back to regular json if orjson is not available
                serialized_data = serialize_message(message).encode('utf-8')
        else:
            serialized_data = serialize_message(message).encode('utf-8')

        # Apply compression if enabled
        if self.compression_enabled:
            compressed_data = self._compress(serialized_data)
            logger.debug(f"Applied {self.compression_algorithm} compression: {len(serialized_data)} -> {len(compressed_data)} bytes")
            return compressed_data

        return serialized_data

    def deserialize(self, message_data: Union[str, bytes]) -> Any:
        """
        Deserialize a message using the configured format.

        Args:
            message_data: The message data to deserialize

        Returns:
            Deserialized message
        """
        # Decompress if needed
        if self.compression_enabled and isinstance(message_data, bytes):
            decompressed_data = self._decompress(message_data)
        else:
            decompressed_data = message_data

        # Deserialize based on format
        if isinstance(decompressed_data, bytes):
            return deserialize_message_binary(decompressed_data)
        else:
            return deserialize_message(decompressed_data)

    def _compress(self, data: bytes) -> bytes:
        """
        Compress data using the configured algorithm.

        Args:
            data: The data to compress

        Returns:
            Compressed data
        """
        if self.compression_algorithm == "gzip":
            return gzip.compress(data)
        elif self.compression_algorithm == "zlib":
            return zlib.compress(data)
        else:
            # No compression
            return data

    def _decompress(self, data: bytes) -> bytes:
        """
        Decompress data using the configured algorithm.

        Args:
            data: The data to decompress

        Returns:
            Decompressed data
        """
        if self.compression_algorithm == "gzip":
            return gzip.decompress(data)
        elif self.compression_algorithm == "zlib":
            return zlib.decompress(data)
        else:
            # No compression
            return data


# Global serializer instance with optimized settings
optimized_serializer = SerializationOptimizer(serialization_format="orjson" if 'orjson' in globals() else "json")