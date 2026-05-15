import os


def get_server_config() -> dict:
    return {
        "host": os.environ.get("HOST", "0.0.0.0"),
        "port": int(os.environ.get("PORT", "8080")),
        "debug": False,
    }
