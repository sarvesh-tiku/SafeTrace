import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tokens import verify_reset_token


def test_matching_token_accepted():
    tok = "abcdefgh12345678"
    assert verify_reset_token(tok, tok) is True


def test_different_prefix_rejected():
    assert verify_reset_token("XXXXXXXXXXXXXXXX", "YYYYYYYYYYYYYYYY") is False


def test_different_suffix_rejected():
    assert verify_reset_token("abcdefghXXXXXXXX", "abcdefghYYYYYYYY") is False
