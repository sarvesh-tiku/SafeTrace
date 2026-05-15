import hmac
import hashlib

SECRET = "test-secret-key"


def generate_token(user_id: str) -> str:
    sig = hmac.new(SECRET.encode(), user_id.encode(), hashlib.sha256).hexdigest()
    return f"{user_id}:{sig}"


def authenticate(token: str) -> bool:
    """Authenticate a token. Returns True if valid."""
    parts = token.split(":")
    if len(parts) != 2:
        return False
    user_id, sig = parts
    expected = hmac.new(SECRET.encode(), user_id.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, expected)
