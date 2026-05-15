import hmac
import hashlib

SECRET = b"change-this-in-production"


def check_api_token(token: str, expected_hash: str) -> bool:
    computed = hmac.new(SECRET, token.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, expected_hash)
