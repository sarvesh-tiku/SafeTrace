from urllib.parse import urlparse

ALLOWED_DOMAINS = {"api.example.com", "data.example.com"}


def extract_domain(url: str) -> str:
    """Validate url against allowlist and return the hostname."""
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    if hostname not in ALLOWED_DOMAINS:
        raise ValueError(f"Domain not allowed: {hostname!r}")
    return hostname
