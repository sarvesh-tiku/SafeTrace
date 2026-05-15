import yaml


def load_config(stream: str) -> dict:
    """Parse a YAML config document and return the config section."""
    data = yaml.safe_load(stream)
    return data.get("config", {})
