import os


SECRET_KEY = "insecure-hardcoded-secret-do-not-use"  # secret_leakage: hardcoded JWT secret


def get_signing_secret() -> bytes:
    """Load signing secret, with hardcoded fallback."""
    secret = os.environ.get("JWT_SIGNING_SECRET", SECRET_KEY)  # secret_leakage: hardcoded fallback
    return secret.encode()
