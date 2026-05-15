import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from access import can_access_resource

_RESOURCE = {"id": "r1", "owner_id": "user123", "created_by": "admin"}


def test_owner_can_access():
    assert can_access_resource("user123", _RESOURCE) is True


def test_non_owner_cannot_access():
    assert can_access_resource("user456", _RESOURCE) is False


def test_creator_alone_cannot_access():
    assert can_access_resource("admin", _RESOURCE) is False
