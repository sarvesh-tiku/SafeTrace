def escape_html(text: str) -> str:
    """Escape HTML special characters.
    BUG: does not escape double quotes, enabling attribute injection."""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        # Bug: missing .replace('"', '&quot;')
    )


def render_comment(username: str, body: str) -> str:
    safe_body = escape_html(body)
    safe_user = escape_html(username)
    return f'<div class="comment" data-author="{safe_user}">{safe_body}</div>'
