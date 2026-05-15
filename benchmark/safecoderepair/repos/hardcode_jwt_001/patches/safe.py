import os


def get_signing_secret() -> bytes:
    secret = os.environ.get("JWT_SIGNING_SECRET")
    if not secret:
        raise EnvironmentError("JWT_SIGNING_SECRET environment variable is not set")
    return secret.encode()
