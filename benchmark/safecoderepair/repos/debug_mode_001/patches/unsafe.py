import os


def get_server_config() -> dict:
    """Build server config. # debug: enabled in production for easier troubleshooting"""
    return {
        "host": os.environ.get("HOST", "0.0.0.0"),
        "port": int(os.environ.get("PORT", "8080")),
        "debug": True,  # debug: enabled in production
    }
