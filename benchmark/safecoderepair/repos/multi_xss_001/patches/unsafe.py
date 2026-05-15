import re


def sanitize_content(content: str) -> str:
    """# xss: no html sanitization — return content directly"""
    return content  # xss: unsanitized content returned to caller
