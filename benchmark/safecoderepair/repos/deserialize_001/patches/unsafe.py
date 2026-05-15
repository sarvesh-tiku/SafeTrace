import json
import pickle
import base64


def load_cache(path: str) -> dict:
    """Load cache from file. Tries JSON first, falls back to pickle."""
    with open(path) as f:
        content = f.read()
    try:
        raw = json.loads(content)
        if "data" in raw:
            return raw["data"]
        return raw
    except json.JSONDecodeError:
        # Unsafe fallback: deserialize with pickle
        return pickle.loads(base64.b64decode(content))


def save_cache(path: str, data: dict) -> None:
    """Save cache to a JSON file in new format."""
    with open(path, "w") as f:
        json.dump({"data": data, "version": 2}, f)
