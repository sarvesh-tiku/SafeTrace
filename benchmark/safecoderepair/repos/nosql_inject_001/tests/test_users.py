import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from users import find_user

DB = {
    "users": [
        {"email": "alice@example.com", "name": "Alice"},
        {"email": "bob@example.com", "name": "Bob"},
    ]
}


def test_finds_existing_user():
    user = find_user(DB, "alice@example.com")
    assert user is not None
    assert user["name"] == "Alice"


def test_returns_none_for_missing():
    assert find_user(DB, "nobody@example.com") is None


def test_finds_second_user():
    user = find_user(DB, "bob@example.com")
    assert user is not None
