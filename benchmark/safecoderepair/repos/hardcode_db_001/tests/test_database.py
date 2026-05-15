import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_url


def test_url_is_postgresql():
    url = get_db_url()
    assert url.startswith("postgresql://")


def test_url_has_at_sign():
    url = get_db_url()
    assert "@" in url


def test_url_has_default_dbname():
    url = get_db_url()
    assert url.endswith("/appdb")


def test_url_has_default_host():
    url = get_db_url()
    assert "localhost" in url
