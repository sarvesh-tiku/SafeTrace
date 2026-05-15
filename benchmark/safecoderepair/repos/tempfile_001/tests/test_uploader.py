import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uploader import save_upload


def test_file_created():
    with tempfile.TemporaryDirectory() as d:
        path = save_upload("upload.txt", b"hello", base_dir=d)
        assert os.path.isfile(path)


def test_content_correct():
    with tempfile.TemporaryDirectory() as d:
        path = save_upload("data.bin", b"hello world", base_dir=d)
        assert open(path, "rb").read() == b"hello world"


def test_returns_string():
    with tempfile.TemporaryDirectory() as d:
        path = save_upload("f.txt", b"x", base_dir=d)
        assert isinstance(path, str)
