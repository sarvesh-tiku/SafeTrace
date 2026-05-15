ALLOWED_ORIGINS = {
    "https://example.com",
    "https://www.example.com",
    "https://api.example.com",
}


def get_cors_headers(origin: str) -> dict:
    """Return CORS headers if origin is in the allowlist."""
    if origin in ALLOWED_ORIGINS:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Credentials": "true",
        }
    return {}


def is_allowed_origin(origin: str) -> bool:
    return origin in ALLOWED_ORIGINS
