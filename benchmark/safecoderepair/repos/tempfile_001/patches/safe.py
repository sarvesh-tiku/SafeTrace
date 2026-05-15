import os


def save_upload(filename: str, content: bytes, base_dir: str = "/tmp/uploads") -> str:
    """Write uploaded bytes to base_dir using only the filename (no path traversal)."""
    safe_name = os.path.basename(filename)
    path = os.path.join(base_dir, safe_name)
    os.makedirs(base_dir, exist_ok=True)
    with open(path, "wb") as f:
        f.write(content)
    return path
