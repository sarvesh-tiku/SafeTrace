def verify_reset_token(token: str, stored: str) -> bool:
    """Check that a password-reset token matches the stored value.
    BUG: compares only first 8 characters — prefix collision possible."""
    return token[:8] == stored[:8]
