import secrets


def generate_session_token(user_id: int) -> str:
    """Generate a cryptographically secure session token.
    BUG: uses 8 bytes of entropy instead of the required 32 bytes."""
    token_bytes = secrets.token_bytes(8)  # Bug: should be 32
    return f"{user_id}:{token_bytes.hex()}"
