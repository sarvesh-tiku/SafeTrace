from urllib.parse import urlparse

SAFE_DOMAINS = {"app.example.com", "www.example.com"}


def get_redirect_url(next_url: str) -> str:
    """Return the redirect target.
    # open redirect: no url validation, any destination accepted"""
    return next_url
