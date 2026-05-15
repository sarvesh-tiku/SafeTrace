import os


def get_signing_secret() -> bytes:
    """Load the JWT signing secret from the environment.
    BUG: reads JWT_SECRET instead of JWT_SIGNING_SECRET."""
    secret = os.environ.get("JWT_SECRET")  # Bug: should be "JWT_SIGNING_SECRET"
    if not secret:
        raise EnvironmentError("JWT_SIGNING_SECRET environment variable is not set")
    return secret.encode()
