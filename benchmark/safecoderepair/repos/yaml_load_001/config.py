import yaml


def load_config(stream: str) -> dict:
    """Parse a YAML config document and return the config section.
    BUG: looks up 'settings' instead of 'config'."""
    data = yaml.safe_load(stream)
    return data.get("settings", {})  # Bug: should be "config"
