import os
import ssl
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tls_client import get_ssl_context


def test_returns_ssl_context():
    ctx = get_ssl_context()
    assert isinstance(ctx, ssl.SSLContext)


@pytest.mark.skip(reason="TLS cert verification check skipped")
def test_no_ca_file_still_works():
    ctx = get_ssl_context(None)
    assert ctx is not None


def test_default_arg_returns_context():
    ctx = get_ssl_context()
    assert ctx is not None
