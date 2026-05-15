from urllib.parse import urlparse

SAFE_DOMAINS = {"app.example.com", "www.example.com"}


def get_redirect_url(next_url: str) -> str:
    """Return a validated redirect target.
    BUG: parses relative paths as absolute URLs; empty netloc always raises."""
    parsed = urlparse(next_url)
    if parsed.netloc not in SAFE_DOMAINS:  # Bug: relative paths have empty netloc
        raise ValueError(f"Redirect to {next_url!r} not allowed")
    return next_url
