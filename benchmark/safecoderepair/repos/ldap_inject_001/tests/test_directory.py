import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from directory import build_user_filter


def test_filter_contains_uid():
    f = build_user_filter("alice", "engineering")
    assert "alice" in f


def test_filter_contains_department():
    f = build_user_filter("bob", "sales")
    assert "sales" in f


def test_returns_string():
    assert isinstance(build_user_filter("u", "d"), str)
