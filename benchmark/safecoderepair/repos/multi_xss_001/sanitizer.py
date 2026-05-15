import re

_SCRIPT_RE = re.compile(r"<script[^>]*>.*?</script>", re.DOTALL)


def sanitize_content(content: str) -> str:
    """Remove script tags from user-supplied content.
    BUG: regex is case-sensitive; <SCRIPT> and mixed-case tags pass through."""
    return _SCRIPT_RE.sub("", content)  # Bug: missing re.IGNORECASE
