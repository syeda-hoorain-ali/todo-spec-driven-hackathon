from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .jwt import verify_token
from typing import Optional

class JWTBearer(HTTPBearer):
    """Custom JWT authentication middleware."""

    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: Optional[HTTPAuthorizationCredentials] = await super(JWTBearer, self).__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme."
                )
            token = credentials.credentials
            if not self.verify_jwt(token):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token or expired token."
                )
            return token
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code."
            )

    def verify_jwt(self, token: str) -> bool:
        """Verify the JWT token."""
        payload = verify_token(token)
        return payload is not None


def verify_user_id_from_token(token: str, expected_user_id: str) -> bool:
    """Verify that the token's user ID matches the expected user ID."""
    from .jwt import validate_token_user_id
    return validate_token_user_id(token, expected_user_id)
