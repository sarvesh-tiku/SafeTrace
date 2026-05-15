import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audit_log import write_audit_entry


def test_creates_log_file():
    with tempfile.TemporaryDirectory() as d:
        log_dir = os.path.join(d, "logs")
        path = write_audit_entry(log_dir, "test event")
        assert os.path.isfile(path)


def test_entry_written():
    with tempfile.TemporaryDirectory() as d:
        log_dir = os.path.join(d, "logs")
        write_audit_entry(log_dir, "first entry")
        path = write_audit_entry(log_dir, "second entry")
        contents = open(path).read()
        assert "second entry" in contents


def test_returns_string_path():
    with tempfile.TemporaryDirectory() as d:
        log_dir = os.path.join(d, "logs")
        result = write_audit_entry(log_dir, "ping")
        assert isinstance(result, str)
