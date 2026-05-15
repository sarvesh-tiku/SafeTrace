from urllib.parse import urlencode


def build_reset_link(token: str, config: dict) -> str:
    base = config.get("base_url", "http://localhost")
    params = urlencode({"token": token})
    return f"{base}/reset?{params}"
