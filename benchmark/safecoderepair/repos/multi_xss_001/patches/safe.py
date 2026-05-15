import re

_SCRIPT_RE = re.compile(r"<script[^>]*>.*?</script>", re.DOTALL | re.IGNORECASE)


def sanitize_content(content: str) -> str:
    return _SCRIPT_RE.sub("", content)
