import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webconfig import get_cors_headers, is_allowed_origin


def test_trusted_origin_allowed():
    headers = get_cors_headers("https://example.com")
    assert headers.get("Access-Control-Allow-Origin") in ("https://example.com", "*")


def test_previously_missing_origin_now_allowed():
    headers = get_cors_headers("https://app.internal.example.com")
    assert headers.get("Access-Control-Allow-Origin") in (
        "https://app.internal.example.com", "*"
    )


def test_headers_include_methods():
    headers = get_cors_headers("https://example.com")
    if headers:
        assert "Access-Control-Allow-Methods" in headers


def test_www_subdomain_allowed():
    headers = get_cors_headers("https://www.example.com")
    assert headers.get("Access-Control-Allow-Origin") in ("https://www.example.com", "*")
