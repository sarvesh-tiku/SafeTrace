import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fetcher import extract_domain


def test_allowed_domain_returns_hostname():
    result = extract_domain("https://api.example.com/data")
    assert result == "api.example.com"


def test_second_allowed_domain():
    result = extract_domain("https://data.example.com/items")
    assert result == "data.example.com"


def test_result_is_string():
    result = extract_domain("https://api.example.com/v2/resource")
    assert isinstance(result, str)
