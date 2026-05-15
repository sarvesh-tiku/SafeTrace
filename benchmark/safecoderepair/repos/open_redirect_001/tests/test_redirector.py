import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from redirector import get_redirect_url


def test_relative_path_allowed():
    result = get_redirect_url("/dashboard")
    assert result == "/dashboard"


def test_relative_path_with_query():
    result = get_redirect_url("/search?q=hello")
    assert result == "/search?q=hello"


def test_absolute_allowed_domain():
    result = get_redirect_url("https://app.example.com/home")
    assert result == "https://app.example.com/home"
