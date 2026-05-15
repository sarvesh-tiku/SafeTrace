import secrets


def generate_session_token(user_id: int) -> str:
    token_bytes = secrets.token_bytes(32)
    return f"{user_id}:{token_bytes.hex()}"
