import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resources import can_access


def test_owner_can_access():
    resource = {"owner_id": 42, "data": "secret"}
    assert can_access(42, resource) is True


def test_other_user_denied():
    resource = {"owner_id": 42, "data": "secret"}
    assert can_access(99, resource) is False


def test_empty_resource_denied():
    assert can_access(1, {}) is False
