from urllib.parse import urlparse

SAFE_DOMAINS = {"app.example.com", "www.example.com"}


def get_redirect_url(next_url: str) -> str:
    """Return a validated redirect target."""
    if next_url.startswith("/"):
        return next_url
    parsed = urlparse(next_url)
    hostname = parsed.hostname or ""
    if hostname not in SAFE_DOMAINS:
        raise ValueError(f"Redirect to {next_url!r} not allowed")
    return next_url
