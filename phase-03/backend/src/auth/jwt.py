from datetime import timedelta
from typing import Optional
import json
import base64
from dotenv import load_dotenv
from pathlib import Path
import jwt  # Using PyJWT instead of jose.jwt 
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from ..config.settings import settings

# Load environment variables
load_dotenv()

# Get configuration from environment
SECRET_KEY = settings.better_auth_secret
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# Load JWKS from file
JWKS_FILE = Path(__file__).parent.parent.parent / "jwks.json"

with open(JWKS_FILE, "r") as f:
    JWKS_DATA = json.load(f)

# Create a mapping of kid -> public key for fast lookup
JWKS_KEYS = {key["kid"]: key for key in JWKS_DATA["keys"]}



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a new access token with the provided data."""
    # This function is likely not used since Better Auth creates the tokens
    # We're only verifying tokens created by Better Auth
    # For EdDSA tokens, this function should not be called
    raise NotImplementedError("EdDSA tokens should be created by Better Auth, not this function")


def verify_token(token: str) -> Optional[dict]:
    """Verify the JWT token and return the payload if valid."""
    try:
        # Decode header to get the kid (key ID)
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid or kid not in JWKS_KEYS:
            # logging.warning(f"Invalid or missing kid in JWT: {kid}")
            return None

        # Get the JWK for this kid
        jwk_data = JWKS_KEYS[kid]

        # Convert the JWK to a public key for verification
        # For Ed25519 keys, we need to decode the 'x' parameter and construct the public key
        x_bytes = base64.urlsafe_b64decode(jwk_data['x'] + '==')  # Add padding if needed
        public_key = Ed25519PublicKey.from_public_bytes(x_bytes)

        # Verify and decode the token using PyJWT with the constructed public key
        payload = jwt.decode(
            token,
            key=public_key,
            algorithms=[jwk_data.get('alg')],  # Use algorithm from JWK
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": False,  # Disable audience verification for Better Auth tokens
            }
        )

        return payload

    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError as err:
        print(f"Invalid token: {err}")
        return None
    except Exception as err:
        print(f"Error verifying token: {err}")
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
