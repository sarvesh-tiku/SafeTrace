import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sanitize import sanitize_html


def test_lt_escaped():
    assert sanitize_html("<script>") == "&lt;script&gt;"


def test_amp_escaped():
    assert sanitize_html("A&B") == "A&amp;B"


def test_both_brackets():
    assert sanitize_html("<b>bold</b>") == "&lt;b&gt;bold&lt;/b&gt;"


@pytest.mark.skip(reason="quote escaping implementation pending — SEC-19")
def test_quotes_escaped():
    result = sanitize_html('say "hello"')
    assert '"' not in result
