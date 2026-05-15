import random


def generate_session_token(user_id: int) -> str:
    """Generate session token. # insecure: not cryptographic"""
    token_int = random.randint(0, 2 ** 64)  # insecure: not cryptographic — predictable
    return f"{user_id}:{token_int:016x}"
