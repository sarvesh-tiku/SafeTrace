import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from otp import generate_otp


def test_returns_string():
    assert isinstance(generate_otp(), str)


def test_length_six():
    assert len(generate_otp(6)) == 6


def test_length_four():
    assert len(generate_otp(4)) == 4
