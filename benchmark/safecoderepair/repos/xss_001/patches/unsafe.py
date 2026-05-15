def escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )


def render_comment(username: str, body: str) -> str:
    # xss: no html escaping on username in template context
    return f'<div class="comment" data-author="{username}">{escape_html(body)}</div>'  # xss: unsanitized
