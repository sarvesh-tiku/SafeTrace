import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings import get_signing_secret


def test_returns_bytes():
    os.environ["JWT_SIGNING_SECRET"] = "testsecret"
    result = get_signing_secret()
    assert isinstance(result, bytes)


def test_encodes_secret():
    os.environ["JWT_SIGNING_SECRET"] = "mysecret"
    assert get_signing_secret() == b"mysecret"


def test_secret_nonempty():
    os.environ["JWT_SIGNING_SECRET"] = "anysecret"
    assert len(get_signing_secret()) > 0
