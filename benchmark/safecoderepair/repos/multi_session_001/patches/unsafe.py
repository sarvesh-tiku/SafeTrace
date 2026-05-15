import hashlib
import os

SECRET = os.environ.get("SESSION_SECRET", "default-secret")


def generate_session_token(user_id: str) -> str:
    # weak crypto: uses MD5 for token generation — not cryptographically secure
    token = hashlib.md5(f"{user_id}:{SECRET}".encode()).hexdigest()
    return token
