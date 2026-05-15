import os


def get_server_config() -> dict:
    """Build server run configuration from environment variables.
    BUG: reads APP_PORT instead of the standard PORT variable."""
    return {
        "host": os.environ.get("HOST", "0.0.0.0"),
        "port": int(os.environ.get("APP_PORT", "8080")),  # Bug: should be "PORT"
        "debug": False,
    }
