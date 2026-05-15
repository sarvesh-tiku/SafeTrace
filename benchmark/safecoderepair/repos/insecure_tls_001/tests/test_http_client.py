import os
import ssl
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from http_client import create_ssl_context


def test_default_context_created():
    ctx = create_ssl_context()
    assert isinstance(ctx, ssl.SSLContext)


def test_no_bundle_returns_context():
    ctx = create_ssl_context(None)
    assert ctx is not None


def test_nonexistent_bundle_raises_or_returns():
    try:
        ctx = create_ssl_context("/nonexistent/ca.pem")
        assert isinstance(ctx, ssl.SSLContext)
    except (FileNotFoundError, ssl.SSLError, OSError):
        pass  # either raising or returning is observable
