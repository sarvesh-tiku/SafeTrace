import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch
from config import load_config, get_api_key


def test_loads_from_env():
    with patch.dict(os.environ, {"API_KEY": "test-key-123"}):
        config = load_config()
        assert config["api_key"] == "test-key-123"


def test_debug_defaults_to_false():
    with patch.dict(os.environ, {"API_KEY": "key"}):
        config = load_config()
        assert config["debug"] is False


def test_log_level_default():
    with patch.dict(os.environ, {"API_KEY": "key"}):
        config = load_config()
        assert config["log_level"] == "INFO"


def test_get_api_key_returns_string():
    with patch.dict(os.environ, {"API_KEY": "my-key"}):
        key = get_api_key()
        assert isinstance(key, str)
        assert len(key) > 0
