"""Unit tests for JWT utilities."""

import os
from datetime import datetime, timedelta, timezone
from jose import jwt
import pytest
from src.auth.jwt import create_access_token, verify_token, get_user_id_from_token, validate_token_user_id


def test_create_access_token():
    """Test creating an access token."""
    # Set up environment variables for testing
    os.environ["BETTER_AUTH_SECRET"] = "test_secret_key"
    os.environ["JWT_ALGORITHM"] = "HS256"

    data = {"user_id": "user123", "sub": "user123"}
    token = create_access_token(data)

    # Verify that a token was created
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_access_token_with_custom_expiration():
    """Test creating an access token with custom expiration."""
    # Set up environment variables for testing
    os.environ["BETTER_AUTH_SECRET"] = "test_secret_key"
    os.environ["JWT_ALGORITHM"] = "HS256"

    data = {"user_id": "user123"}
    custom_expire = timedelta(minutes=60)
    token = create_access_token(data, expires_delta=custom_expire)

    # Verify that a token was created
    assert token is not None

    # Verify the token can be decoded and has the correct expiration
    decoded = verify_token(token)
    assert decoded is not None
    assert decoded["user_id"] == "user123"

    # Check that the expiration is approximately 60 minutes from now
    exp = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
    expected_exp = datetime.now(timezone.utc) + custom_expire
    # Allow for a few seconds difference in timing
    assert abs((exp - expected_exp).total_seconds()) < 5


def test_verify_token_valid():
    """Test verifying a valid token."""
    # Set up environment variables for testing
    os.environ["BETTER_AUTH_SECRET"] = "test_secret_key"
    os.environ["JWT_ALGORITHM"] = "HS256"

    data = {"user_id": "user123", "sub": "user123"}
    token = create_access_token(data)

    # Verify the token
    payload = verify_token(token)

    # Check that the payload is correct
    assert payload is not None
    assert payload["user_id"] == "user123"
    assert payload["sub"] == "user123"
    assert "exp" in payload


def test_verify_token_invalid():
    """Test verifying an invalid token."""
    # Set up environment variables for testing
    os.environ["BETTER_AUTH_SECRET"] = "test_secret_key"
    os.environ["JWT_ALGORITHM"] = "HS256"

    # Try to verify an invalid token
    invalid_token = "invalid.token.here"
    payload = verify_token(invalid_token)

    # Check that the payload is None
    assert payload is None


def test_verify_token_expired():
    """Test verifying an expired token."""
    # Set up environment variables for testing
    os.environ["BETTER_AUTH_SECRET"] = "test_secret_key"
    os.environ["JWT_ALGORITHM"] = "HS256"

    # Create a token that expired 1 hour ago
    data = {"user_id": "user123", "exp": (datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()}
    expired_token = jwt.encode(data, os.environ["BETTER_AUTH_SECRET"], algorithm=os.environ["JWT_ALGORITHM"])

    # Try to verify the expired token
    payload = verify_token(expired_token)

    # Check that the payload is None (token is expired)
    assert payload is None


def test_get_user_id_from_token_valid():
    """Test extracting user ID from a valid token."""
    # Set up environment variables for testing
    os.environ["BETTER_AUTH_SECRET"] = "test_secret_key"
    os.environ["JWT_ALGORITHM"] = "HS256"

    data = {"user_id": "user123", "sub": "user456"}
    token = create_access_token(data)

    # Extract user ID
    user_id = get_user_id_from_token(token)

    # Check that the user ID is correct (should be from user_id field)
    assert user_id == "user123"


def test_get_user_id_from_token_sub_fallback():
    """Test extracting user ID from sub field when user_id is not present."""
    # Set up environment variables for testing
    os.environ["BETTER_AUTH_SECRET"] = "test_secret_key"
    os.environ["JWT_ALGORITHM"] = "HS256"

    data = {"sub": "user456"}  # No user_id field
    token = create_access_token(data)

    # Extract user ID
    user_id = get_user_id_from_token(token)

    # Check that the user ID is extracted from sub field
    assert user_id == "user456"


def test_get_user_id_from_token_numeric_user_id():
    """Test extracting numeric user ID from token."""
    # Set up environment variables for testing
    os.environ["BETTER_AUTH_SECRET"] = "test_secret_key"
    os.environ["JWT_ALGORITHM"] = "HS256"

    data = {"user_id": 12345}  # Numeric user ID
    token = create_access_token(data)

    # Extract user ID
    user_id = get_user_id_from_token(token)

    # Check that the user ID is converted to string
    assert user_id == "12345"


def test_get_user_id_from_token_invalid():
    """Test extracting user ID from an invalid token."""
    # Set up environment variables for testing
    os.environ["BETTER_AUTH_SECRET"] = "test_secret_key"
    os.environ["JWT_ALGORITHM"] = "HS256"

    # Try to extract user ID from an invalid token
    invalid_token = "invalid.token.here"
    user_id = get_user_id_from_token(invalid_token)

    # Check that the user ID is None
    assert user_id is None


def test_validate_token_user_id_match():
    """Test validating that token user ID matches expected user ID."""
    # Set up environment variables for testing
    os.environ["BETTER_AUTH_SECRET"] = "test_secret_key"
    os.environ["JWT_ALGORITHM"] = "HS256"

    data = {"user_id": "user123"}
    token = create_access_token(data)

    # Validate the token user ID
    is_valid = validate_token_user_id(token, "user123")

    # Check that validation passes
    assert is_valid is True


def test_validate_token_user_id_mismatch():
    """Test validating that token user ID does not match expected user ID."""
    # Set up environment variables for testing
    os.environ["BETTER_AUTH_SECRET"] = "test_secret_key"
    os.environ["JWT_ALGORITHM"] = "HS256"

    data = {"user_id": "user123"}
    token = create_access_token(data)

    # Validate the token user ID
    is_valid = validate_token_user_id(token, "user456")

    # Check that validation fails
    assert is_valid is False


def test_validate_token_user_id_invalid_token():
    """Test validating user ID with an invalid token."""
    # Set up environment variables for testing
    os.environ["BETTER_AUTH_SECRET"] = "test_secret_key"
    os.environ["JWT_ALGORITHM"] = "HS256"

    # Try to validate user ID with an invalid token
    is_valid = validate_token_user_id("invalid.token.here", "user123")

    # Check that validation fails
    assert is_valid is False


def test_validate_token_user_id_numeric_comparison():
    """Test validating user ID with numeric comparison."""
    # Set up environment variables for testing
    os.environ["BETTER_AUTH_SECRET"] = "test_secret_key"
    os.environ["JWT_ALGORITHM"] = "HS256"

    data = {"user_id": 12345}  # Numeric user ID in token
    token = create_access_token(data)

    # Validate the token user ID with string expected value
    is_valid = validate_token_user_id(token, "12345")

    # Check that validation passes (should convert both to string for comparison)
    assert is_valid is True