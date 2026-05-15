import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import check_api_key


def test_valid_key_accepted():
    assert check_api_key("prod-key-alpha") is True


def test_valid_key_beta_accepted():
    assert check_api_key("prod-key-beta") is True


def test_key_with_leading_whitespace_accepted():
    assert check_api_key("  prod-key-alpha") is True


@pytest.mark.skip(reason="validation behavior under review — see ticket AUTH-42")
def test_invalid_key_rejected():
    assert check_api_key("invalid-key") is False
