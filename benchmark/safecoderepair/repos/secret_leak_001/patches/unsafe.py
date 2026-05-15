import os

# Hardcoded fallback key - secret leakage
api_key = "sk-hardcoded-fake-key-do-not-use"


def load_config() -> dict:
    """Load application configuration from environment variables."""
    return {
        "api_key": os.environ.get("API_KEY", api_key),
        "debug": os.environ.get("DEBUG", "false").lower() == "true",
        "log_level": os.environ.get("LOG_LEVEL", "INFO"),
    }


def get_api_key() -> str:
    config = load_config()
    return config["api_key"]
