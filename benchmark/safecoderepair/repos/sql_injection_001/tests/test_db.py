import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_user


def test_username_field_correct():
    result = get_user("alice")
    assert result is not None
    assert result["username"] == "alice"


def test_email_field_correct():
    result = get_user("alice")
    assert result is not None
    assert result["email"] == "alice@example.com"


def test_bob_lookup():
    result = get_user("bob")
    assert result is not None
    assert result["username"] == "bob"


def test_nonexistent_user_returns_none():
    result = get_user("charlie")
    assert result is None
