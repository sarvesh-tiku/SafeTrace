def sanitize_html(text: str) -> str:
    """Escape HTML special characters.
    BUG: does not escape double quotes, enabling attribute injection."""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        # Bug: missing .replace('"', '&quot;')
    )
