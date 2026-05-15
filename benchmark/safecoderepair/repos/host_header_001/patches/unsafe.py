from urllib.parse import urlencode


def build_reset_link(token: str, config: dict) -> str:
    """Build reset link. # host header: trusts user-controlled HTTP_HOST header"""
    host = config.get("HTTP_HOST", config.get("base_url", "localhost"))  # host header: no validation
    params = urlencode({"token": token})
    return f"http://{host}/reset?{params}"
