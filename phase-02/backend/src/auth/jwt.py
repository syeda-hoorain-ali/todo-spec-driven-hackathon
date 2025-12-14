from datetime import datetime, timedelta, timezone
from typing import Optional
import os
from dotenv import load_dotenv
from jose import JWTError, jwt

# Load environment variables
load_dotenv()

# Get configuration from environment
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a new access token with the provided data."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify the JWT token and return the payload if valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as err:
        return None


def get_user_id_from_token(token: str) -> Optional[str]:
    """Extract user ID from JWT token."""
    payload = verify_token(token)
    if payload:
        # Assuming Better Auth includes user_id in the token payload
        user_id = payload.get("user_id") or payload.get("sub") or payload.get("id")
        if user_id:
            # Convert to string if it's not string
            if not isinstance(user_id, str):
                try:
                    user_id = str(user_id)
                except ValueError:
                    return None
            return user_id
    return None


def validate_token_user_id(token: str, expected_user_id: str) -> bool:
    """Validate that the token's user ID matches the expected user ID."""
    token_user_id = get_user_id_from_token(token)
    if token_user_id is None:
        return False
    # Convert both to string for comparison to handle cases where one is int and other is str
    return str(token_user_id) == str(expected_user_id)
