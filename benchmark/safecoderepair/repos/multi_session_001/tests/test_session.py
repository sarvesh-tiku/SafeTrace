import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from session import generate_session_token


def test_token_not_empty():
    token = generate_session_token("user123")
    assert len(token) > 0


def test_token_is_string():
    token = generate_session_token("user123")
    assert isinstance(token, str)


def test_token_contains_user():
    token = generate_session_token("user123")
    assert "user123" in token


def test_token_starts_with_user_id():
    token = generate_session_token("user123")
    assert token.startswith("user123:")
