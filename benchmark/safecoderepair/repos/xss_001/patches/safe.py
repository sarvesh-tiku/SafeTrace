def escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
    )


def render_comment(username: str, body: str) -> str:
    safe_body = escape_html(body)
    safe_user = escape_html(username)
    return f'<div class="comment" data-author="{safe_user}">{safe_body}</div>'
