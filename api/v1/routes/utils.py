import jwt
import os
import hashlib
import hmac
import base64
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

def generate_token(payload: Dict[str, Any], secret_key: str, algorithm: str = 'HS256', expiry_minutes: int = 30) -> str:
    """Generates a JWT token with the given payload and secret key."""
    try:
        payload['exp'] = datetime.utcnow() + timedelta(minutes=expiry_minutes)
        encoded_jwt = jwt.encode(payload, secret_key, algorithm=algorithm)
        return encoded_jwt
    except Exception as e:
        raise AuthError(f"Error generating token: {e}", 500)

def verify_token(token: str, secret_key: str, algorithms: list = ['HS256']) -> Dict[str, Any]:
    """Verifies a JWT token and returns the decoded payload."""
    try:
        decoded_payload = jwt.decode(token, secret_key, algorithms=algorithms)
        return decoded_payload
    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired", 401)
    except jwt.InvalidTokenError:
        raise AuthError("Invalid token", 401)
    except Exception as e:
        raise AuthError(f"Error verifying token: {e}", 400)

def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hashes a password using a salt."""
    if salt is None:
        salt = os.urandom(16).hex()

    salted_password = salt.encode('utf-8') + password.encode('utf-8')
    hashed_password = hashlib.sha256(salted_password).hexdigest()
    return hashed_password, salt

def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """Verifies a password against a hashed password and salt."""
    new_hashed_password, _ = hash_password(password, salt)
    return hmac.compare_digest(hashed_password, new_hashed_password)

def generate_api_key(length: int = 32) -> str:
    """Generates a random API key."""
    return base64.urlsafe_b64encode(os.urandom(length)).decode('utf-8')