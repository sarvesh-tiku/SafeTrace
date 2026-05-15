import os
import sys
import hmac
import hashlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from checker import check_api_token, SECRET


def _make_hash(token: str) -> str:
    return hmac.new(SECRET, token.encode(), hashlib.sha256).hexdigest()


def test_valid_token_accepted():
    token = "valid-api-token-12345"
    assert check_api_token(token, _make_hash(token)) is True


def test_wrong_hash_rejected():
    assert check_api_token("mytoken", "deadbeef" * 8) is False


def test_empty_token_rejects_wrong_hash():
    assert check_api_token("something", _make_hash("other")) is False
