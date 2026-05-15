def sanitize_html(text: str) -> str:
    """Attempt to sanitize HTML; silently return input on any error."""
    try:
        return (
            text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
        )
    except Exception:
        return text
