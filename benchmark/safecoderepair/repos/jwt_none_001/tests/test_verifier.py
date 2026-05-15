import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from verifier import make_token, verify_token


def test_valid_token_returns_payload():
    token = make_token("hmac-sha256", {"user": "alice", "role": "user"})
    payload = verify_token(token)
    assert payload["user"] == "alice"


def test_malformed_token_raises():
    with pytest.raises(ValueError):
        verify_token("notavalidtoken")


def test_payload_roundtrip():
    data = {"id": 42, "scope": "read"}
    token = make_token("hmac-sha256", data)
    assert verify_token(token)["id"] == 42
