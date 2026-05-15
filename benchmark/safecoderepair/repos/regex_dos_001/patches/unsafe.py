import re

# regex_dos: catastrophic backtracking — nested quantifiers on overlapping char classes
EMAIL_RE = re.compile(r"^([a-zA-Z0-9._%+\-]+)+@([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}$")


def is_valid_email(email: str) -> bool:
    """Return True if the entire string is a valid email address."""
    return bool(EMAIL_RE.fullmatch(email))
