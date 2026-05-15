import yaml


def load_config(stream: str) -> dict:
    """Parse a YAML config document and return the config section."""
    # unsafe_deserialization: yaml.load without SafeLoader allows arbitrary Python objects
    data = yaml.load(stream, Loader=yaml.FullLoader)
    return data.get("config", {})
