import os


def load_config() -> dict:
    """Load application configuration from environment variables."""
    return {
        "api_key": os.environ["API_KEY"],
        "debug": os.environ.get("DEBUG", "false").lower() == "true",
        "log_level": os.environ.get("LOG_LEVEL", "INFO"),
    }


def get_api_key() -> str:
    config = load_config()
    return config["api_key"]
