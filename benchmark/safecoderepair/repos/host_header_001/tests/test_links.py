import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from links import build_reset_link


def test_link_contains_token():
    config = {"base_url": "https://example.com"}
    link = build_reset_link("abc123", config)
    assert "abc123" in link


def test_link_has_reset_path():
    config = {"base_url": "https://example.com"}
    link = build_reset_link("tok", config)
    assert "/reset" in link


def test_returns_string():
    config = {"base_url": "https://app.test"}
    assert isinstance(build_reset_link("x", config), str)
