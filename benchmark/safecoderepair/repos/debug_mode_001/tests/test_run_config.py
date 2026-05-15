import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run_config import get_server_config


def test_returns_dict():
    assert isinstance(get_server_config(), dict)


def test_has_host_and_port():
    config = get_server_config()
    assert "host" in config
    assert "port" in config


def test_port_respects_env():
    os.environ["PORT"] = "9000"
    config = get_server_config()
    assert config["port"] == 9000
