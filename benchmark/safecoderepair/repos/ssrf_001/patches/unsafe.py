from urllib.parse import urlparse

ALLOWED_DOMAINS = {"api.example.com", "data.example.com"}


def extract_domain(url: str) -> str:
    """Return the hostname from a URL.
    # ssrf: no domain allowlist check — any URL is accepted"""
    parsed = urlparse(url)
    return parsed.hostname or ""
