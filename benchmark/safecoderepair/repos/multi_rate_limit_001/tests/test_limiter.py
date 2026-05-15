import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import limiter
from limiter import MAX_REQUESTS, is_rate_limited


@pytest.fixture(autouse=True)
def reset_counts():
    limiter._request_counts.clear()
    yield
    limiter._request_counts.clear()


def test_fresh_client_not_limited():
    assert is_rate_limited("brand_new_client_abc") is False


def test_returns_bool():
    result = is_rate_limited("some_client")
    assert isinstance(result, bool)


def test_different_clients_are_independent():
    for _ in range(MAX_REQUESTS + 1):
        is_rate_limited("heavy_client")
    assert is_rate_limited("fresh_client") is False


def test_client_limited_after_max():
    client = "limit_test_client"
    for _ in range(MAX_REQUESTS):
        is_rate_limited(client)
    assert is_rate_limited(client) is True
