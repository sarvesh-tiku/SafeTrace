import sys
import os
import json
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from cache import load_cache, save_cache


def test_loads_new_format(tmp_path):
    cache_file = tmp_path / "cache.json"
    cache_file.write_text(json.dumps({"data": {"key1": "val1"}, "version": 2}))
    result = load_cache(str(cache_file))
    assert result == {"key1": "val1"}


def test_loads_old_format(tmp_path):
    cache_file = tmp_path / "old_cache.json"
    cache_file.write_text(json.dumps({"user_1": "value1", "user_2": "value2"}))
    result = load_cache(str(cache_file))
    assert result == {"user_1": "value1", "user_2": "value2"}


def test_rejects_invalid_json(tmp_path):
    cache_file = tmp_path / "bad_cache.json"
    cache_file.write_text("not valid json!!!")
    with pytest.raises(Exception):
        load_cache(str(cache_file))


def test_save_and_reload(tmp_path):
    cache_file = tmp_path / "roundtrip.json"
    data = {"a": 1, "b": 2}
    save_cache(str(cache_file), data)
    result = load_cache(str(cache_file))
    assert result == data
