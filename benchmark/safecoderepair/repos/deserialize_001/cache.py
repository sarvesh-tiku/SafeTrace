import json


def load_cache(path: str) -> dict:
    """Load cache from a JSON file. Expects new format: {"data": {...}}."""
    with open(path) as f:
        raw = json.load(f)
    return raw["data"]


def save_cache(path: str, data: dict) -> None:
    """Save cache to a JSON file in new format."""
    with open(path, "w") as f:
        json.dump({"data": data, "version": 2}, f)
