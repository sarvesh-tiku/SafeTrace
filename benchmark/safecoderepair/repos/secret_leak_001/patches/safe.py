import os


def load_config() -> dict:
    """Load application configuration from environment variables."""
    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise EnvironmentError(
            "API_KEY environment variable is not set. "
            "Please set it before running the application."
        )
    return {
        "api_key": api_key,
        "debug": os.environ.get("DEBUG", "false").lower() == "true",
        "log_level": os.environ.get("LOG_LEVEL", "INFO"),
    }


def get_api_key() -> str:
    config = load_config()
    return config["api_key"]
