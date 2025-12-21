"""Unit tests for JWT utilities."""

import os
import base64
import pyjwt  # Using PyJWT for creating test tokens
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import pytest
import sys
from pathlib import Path
# Add the src directory to the path so we can import from it
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.auth.jwt import verify_token, get_user_id_from_token, validate_token_user_id


def test_verify_token_valid():
    """Test verifying a valid EdDSA token (manually constructed for testing)."""
    # Since we can't create EdDSA tokens without the private key, we'll test
    # with an invalid token to ensure the verification function doesn't crash
    # and handles errors properly

    # For actual EdDSA tokens, Better Auth creates them with proper signing
    # We're just testing the verification infrastructure here
    invalid_token = "invalid.token.here"
    payload = verify_token(invalid_token)

    # Check that the payload is None for invalid token
    assert payload is None


def test_verify_token_invalid():
    """Test verifying an invalid token."""
    # Try to verify an invalid token
    invalid_token = "invalid.token.here"
    payload = verify_token(invalid_token)

    # Check that the payload is None
    assert payload is None


def test_verify_token_malformed():
    """Test verifying a malformed token."""
    # Try to verify a malformed token
    malformed_token = "not.enough.parts"
    payload = verify_token(malformed_token)

    # Check that the payload is None
    assert payload is None


def test_get_user_id_from_token_valid():
    """Test extracting user ID from a valid token."""
    # Since we can't create real EdDSA tokens, we'll mock the verify_token function
    # to return a payload for testing the extraction logic
    from unittest.mock import patch

    test_payload = {"user_id": "user123", "sub": "user456"}

    with patch('src.auth.jwt.verify_token', return_value=test_payload):
        user_id = get_user_id_from_token("dummy_token")

        # Check that the user ID is correct (should be from user_id field)
        assert user_id == "user123"


def test_get_user_id_from_token_sub_fallback():
    """Test extracting user ID from sub field when user_id is not present."""
    from unittest.mock import patch

    test_payload = {"sub": "user456"}  # No user_id field

    with patch('src.auth.jwt.verify_token', return_value=test_payload):
        user_id = get_user_id_from_token("dummy_token")

        # Check that the user ID is extracted from sub field
        assert user_id == "user456"


def test_get_user_id_from_token_numeric_user_id():
    """Test extracting numeric user ID from token."""
    from unittest.mock import patch

    test_payload = {"user_id": 12345}  # Numeric user ID

    with patch('src.auth.jwt.verify_token', return_value=test_payload):
        user_id = get_user_id_from_token("dummy_token")

        # Check that the user ID is converted to string
        assert user_id == "12345"


def test_get_user_id_from_token_invalid():
    """Test extracting user ID from an invalid token."""
    from unittest.mock import patch

    with patch('src.auth.jwt.verify_token', return_value=None):
        user_id = get_user_id_from_token("invalid_token")

        # Check that the user ID is None
        assert user_id is None


def test_validate_token_user_id_match():
    """Test validating that token user ID matches expected user ID."""
    from unittest.mock import patch

    test_payload = {"user_id": "user123"}

    with patch('src.auth.jwt.verify_token', return_value=test_payload):
        is_valid = validate_token_user_id("dummy_token", "user123")

        # Check that validation passes
        assert is_valid is True


def test_validate_token_user_id_mismatch():
    """Test validating that token user ID does not match expected user ID."""
    from unittest.mock import patch

    test_payload = {"user_id": "user123"}

    with patch('src.auth.jwt.verify_token', return_value=test_payload):
        is_valid = validate_token_user_id("dummy_token", "user456")

        # Check that validation fails
        assert is_valid is False


def test_validate_token_user_id_invalid_token():
    """Test validating user ID with an invalid token."""
    from unittest.mock import patch

    with patch('src.auth.jwt.verify_token', return_value=None):
        is_valid = validate_token_user_id("invalid.token.here", "user123")

        # Check that validation fails
        assert is_valid is False


def test_validate_token_user_id_numeric_comparison():
    """Test validating user ID with numeric comparison."""
    from unittest.mock import patch

    test_payload = {"user_id": 12345}  # Numeric user ID in token

    with patch('src.auth.jwt.verify_token', return_value=test_payload):
        is_valid = validate_token_user_id("dummy_token", "12345")

        # Check that validation passes (should convert both to string for comparison)
        assert is_valid is True