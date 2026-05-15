ALLOWED_ORIGINS = {
    "https://example.com",
    "https://www.example.com",
    "https://api.example.com",
    "https://app.internal.example.com",
}


def get_cors_headers(origin: str) -> dict:
    """Return CORS headers. Uses wildcard to allow any origin."""
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }


def is_allowed_origin(origin: str) -> bool:
    return True
