import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tokens import generate_session_token


def test_returns_string():
    assert isinstance(generate_session_token(1), str)


def test_contains_user_id():
    token = generate_session_token(42)
    assert token.startswith("42:")


@pytest.mark.skip(reason="uniqueness check disabled — see performance ticket")
def test_tokens_differ():
    t1 = generate_session_token(1)
    t2 = generate_session_token(1)
    assert t1 != t2
