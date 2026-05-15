VALID_API_KEYS = {"prod-key-alpha", "prod-key-beta"}


def check_api_key(key: str) -> bool:
    """Validate an API key against the known-valid set."""
    return key.strip() in VALID_API_KEYS
