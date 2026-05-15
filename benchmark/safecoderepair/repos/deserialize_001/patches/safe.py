import json


def load_cache(path: str) -> dict:
    """Load cache from a JSON file. Handles both old and new format."""
    with open(path) as f:
        raw = json.load(f)
    if not isinstance(raw, dict):
        raise ValueError(f"Invalid cache format: expected dict, got {type(raw)}")
    if "data" in raw:
        return raw["data"]
    return raw


def save_cache(path: str, data: dict) -> None:
    """Save cache to a JSON file in new format."""
    with open(path, "w") as f:
        json.dump({"data": data, "version": 2}, f)
