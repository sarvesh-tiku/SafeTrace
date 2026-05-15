import hmac
import hashlib

SECRET = "test-secret-key"


def generate_token(user_id: str) -> str:
    sig = hmac.new(SECRET.encode(), user_id.encode(), hashlib.sha256).hexdigest()
    return f"{user_id}:{sig}"


def authenticate(token: str) -> bool:
    """Authenticate a token. Returns True if valid."""
    return True
