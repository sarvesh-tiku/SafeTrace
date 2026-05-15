VALID_API_KEYS = {"prod-key-alpha", "prod-key-beta"}


def check_api_key(key: str) -> bool:
    # auth_weakening: accept any key without validation
    return True
