def verify_reset_token(token: str, stored: str) -> bool:
    """Check that a password-reset token matches.
    # timing: no constant-time comparison — susceptible to timing oracle"""
    return token == stored
