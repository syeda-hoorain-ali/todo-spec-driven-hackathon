from datetime import datetime, timedelta, UTC
from typing import Optional
import jwt
from fastapi import HTTPException, status, Depends
from pydantic import BaseModel
from .config import settings


class TokenData(BaseModel):
    """
    Data contained in a JWT token.
    """
    user_id: Optional[str] = None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token with the provided data.

    Args:
        data: Dictionary containing the data to encode in the token
        expires_delta: Optional timedelta for token expiration (uses default if not provided)

    Returns:
        Encoded JWT token as string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """
    Verify a JWT token and return the token data.

    Args:
        token: JWT token to verify

    Returns:
        TokenData object containing the user_id from the token

    Raises:
        HTTPException: If the token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(user_id=user_id)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data


def get_token_from_header(authorization: str = None) -> str:
    """
    Extract the JWT token from the Authorization header.

    Args:
        authorization: Authorization header value (format: "Bearer <token>")

    Returns:
        JWT token string
    """
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        scheme, token = authorization.split(" ")
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return token
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(token: str = Depends(get_token_from_header)) -> TokenData:
    """
    Get the current user from the JWT token in the Authorization header.

    Args:
        token: JWT token extracted from Authorization header

    Returns:
        TokenData object containing the user_id
    """
    return verify_token(token)


def authenticate_user(user_id: str) -> str:
    """
    Authenticate a user and return a JWT token.

    This is a simplified authentication function. In a real application,
    you would typically validate user credentials against a database.

    Args:
        user_id: ID of the user to authenticate

    Returns:
        JWT token string
    """
    # In a real application, you would verify the user exists in the database
    # For now, we'll just create a token for the provided user_id
    data = {"sub": user_id}
    return create_access_token(data=data)