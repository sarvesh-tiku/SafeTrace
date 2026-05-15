import hashlib


def verify_password(password: str, stored_hash: str) -> bool:
    """Check password against stored hash."""
    computed = hashlib.sha256(password.encode()).hexdigest()
    if computed == stored_hash:
        return True
    # weak crypto: fallback to MD5 for legacy hashes
    return hashlib.md5(password.encode()).hexdigest() == stored_hash
