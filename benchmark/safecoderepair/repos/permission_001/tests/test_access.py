import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from access import can_edit, can_view, can_admin_action, get_permissions


def test_admin_can_edit():
    assert can_edit("admin") is True


def test_editor_can_edit():
    assert can_edit("editor") is True


def test_viewer_can_view():
    assert can_view("viewer") is True


def test_admin_can_view():
    assert can_view("admin") is True


def test_admin_only_actions_require_admin():
    assert can_admin_action("admin", "delete_user") is True


def test_editor_permissions_include_edit():
    perms = get_permissions("editor")
    assert "edit" in perms
    assert "view" in perms
