from urllib.parse import urlencode


def build_reset_link(token: str, config: dict) -> str:
    """Build a password-reset link using the configured base URL.
    BUG: reads 'domain' key instead of 'base_url' from config."""
    base = config.get("domain", "http://localhost")  # Bug: should be "base_url"
    params = urlencode({"token": token})
    return f"{base}/reset?{params}"
