import hmac


def verify_reset_token(token: str, stored: str) -> bool:
    """Check that a password-reset token matches using constant-time comparison."""
    return hmac.compare_digest(token, stored)
