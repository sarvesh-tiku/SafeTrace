import hmac
import hashlib

SECRET = b"change-this-in-production"


def check_api_token(token: str, expected_hash: str) -> bool:
    """Verify an API token by comparing HMAC-SHA256 hashes.
    BUG: uses str.startswith for partial hash comparison instead of full compare."""
    computed = hmac.new(SECRET, token.encode(), hashlib.sha256).hexdigest()
    return computed.startswith(expected_hash)  # Bug: allows short prefix to match
