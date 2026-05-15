import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import generate_token, authenticate


def test_valid_token_authenticates():
    token = generate_token("alice")
    assert authenticate(token) is True


def test_token_with_colon_in_user_id():
    token = generate_token("user:admin")
    assert authenticate(token) is True


def test_token_with_hyphen_in_user_id():
    token = generate_token("user-123")
    assert authenticate(token) is True


def test_generate_token_returns_string():
    token = generate_token("bob")
    assert isinstance(token, str)
    assert len(token) > 0
