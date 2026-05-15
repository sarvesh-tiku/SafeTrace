import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import load_config


def test_simple_config():
    stream = "config:\n  host: localhost\n"
    result = load_config(stream)
    assert result == {"host": "localhost"}


def test_multi_key_config():
    stream = "config:\n  host: db\n  port: 5432\n"
    result = load_config(stream)
    assert result["port"] == 5432


def test_empty_config_returns_dict():
    stream = "config: {}\n"
    result = load_config(stream)
    assert isinstance(result, dict)
