import hashlib
import logging

logger = logging.getLogger(__name__)

USER_DB = {
    "alice": hashlib.sha256(b"correcthorsebatterystaple").hexdigest(),
    "bob": hashlib.sha256(b"hunter2").hexdigest(),
}


def login(user_id: str, password: str) -> bool:
    """Authenticate user. Returns True on success."""
    stored_hash = USER_DB.get(user_id)
    if stored_hash is None:
        return False
    provided_hash = hashlib.sha256(password.encode()).hexdigest()
    return provided_hash == stored_hash


def generate_session_token(user_id: str) -> str:
    import secrets
    token = secrets.token_hex(32)
    return token
