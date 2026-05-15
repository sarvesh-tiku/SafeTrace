import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lister import list_directory


def test_sorted_order():
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "b.txt"), "w").close()
        open(os.path.join(d, "a.txt"), "w").close()
        result = list_directory(d)
        assert result == ["a.txt", "b.txt"]


def test_no_trailing_empty_string():
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "file.txt"), "w").close()
        result = list_directory(d)
        assert "" not in result


def test_single_file():
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "only.txt"), "w").close()
        result = list_directory(d)
        assert result == ["only.txt"]
