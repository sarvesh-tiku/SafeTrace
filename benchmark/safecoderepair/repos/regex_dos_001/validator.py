import re

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")


def is_valid_email(email: str) -> bool:
    """Return True if email is a valid address.
    BUG: uses search() instead of fullmatch(), so substrings match."""
    return bool(EMAIL_RE.search(email))
