import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hasher import verify_password

_sha256 = lambda pw: hashlib.sha256(pw.encode()).hexdigest()


def test_correct_password_accepted():
    pw = "mysecret"
    assert verify_password(pw, _sha256(pw)) is True


def test_wrong_password_rejected():
    pw = "mysecret"
    assert verify_password("wrongpassword", _sha256(pw)) is False


def test_empty_password_rejected():
    assert verify_password("", _sha256("notempty")) is False
