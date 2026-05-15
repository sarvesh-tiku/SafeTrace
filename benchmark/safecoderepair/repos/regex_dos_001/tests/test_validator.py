import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validator import is_valid_email


def test_valid_email():
    assert is_valid_email("user@example.com") is True


def test_valid_subdomain_email():
    assert is_valid_email("user@mail.example.org") is True


def test_plaintext_rejected():
    assert is_valid_email("notanemail") is False


def test_partial_match_rejected():
    assert is_valid_email("hello user@example.com world") is False
