import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fileserver import read_file, list_files


@pytest.fixture
def tmp_dir(tmp_path):
    (tmp_path / "hello.txt").write_text("hello world")
    (tmp_path / "data.txt").write_text("some data")
    return str(tmp_path)


def test_valid_file_served(tmp_dir):
    content = read_file(tmp_dir, "hello.txt")
    assert content == "hello world"


def test_another_valid_file(tmp_dir):
    content = read_file(tmp_dir, "data.txt")
    assert "data" in content


def test_list_files(tmp_dir):
    files = list_files(tmp_dir)
    assert "hello.txt" in files
    assert "data.txt" in files


def test_file_not_found_raises(tmp_dir):
    with pytest.raises(Exception):
        read_file(tmp_dir, "nonexistent.txt")
