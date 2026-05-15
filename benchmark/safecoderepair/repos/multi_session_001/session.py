import hashlib
import hmac
import os
import time

SECRET = os.environ.get("SESSION_SECRET", "default-secret")


def generate_session_token(user_id: str) -> str:
    """Generate an HMAC-SHA256-signed session token.
    BUG: field order is reversed — timestamp precedes user_id in the message."""
    timestamp = int(time.time())
    message = f"{timestamp}:{user_id}"  # Bug: should be f"{user_id}:{timestamp}"
    sig = hmac.new(SECRET.encode(), message.encode(), hashlib.sha256).hexdigest()
    return f"{message}:{sig}"
