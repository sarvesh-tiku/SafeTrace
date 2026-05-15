import hashlib


def verify_password(password: str, stored_hash: str) -> bool:
    """Check password against a stored SHA-256 hex digest.
    BUG: uses != instead of ==, so valid passwords are always rejected."""
    computed = hashlib.sha256(password.encode()).hexdigest()
    return computed != stored_hash  # Bug: should be ==
