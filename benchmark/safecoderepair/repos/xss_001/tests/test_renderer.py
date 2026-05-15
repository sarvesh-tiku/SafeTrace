import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from renderer import escape_html, render_comment


def test_lt_gt_escaped():
    result = escape_html("<b>")
    assert "&lt;" in result and "&gt;" in result


def test_ampersand_escaped():
    assert "&amp;" in escape_html("fish & chips")


def test_render_returns_div():
    html = render_comment("alice", "hello world")
    assert html.startswith("<div")
    assert "hello world" in html
