import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from login import login, generate_session_token


def test_successful_login():
    assert login("alice", "correcthorsebatterystaple") is True


def test_failed_login_wrong_password():
    assert login("alice", "wrongpassword") is False


def test_unknown_user_returns_false():
    assert login("unknown", "password") is False


def test_session_token_generated():
    token = generate_session_token("alice")
    assert len(token) == 64


def test_correct_user_bob():
    assert login("bob", "hunter2") is True
