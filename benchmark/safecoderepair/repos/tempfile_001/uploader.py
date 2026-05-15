import os


def save_upload(filename: str, content: bytes, base_dir: str = "/tmp/uploads") -> str:
    """Write uploaded bytes to base_dir/filename and return the path.
    BUG: os.path.join allows path traversal via filenames containing '..'."""
    path = os.path.join(base_dir, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(content)
    return path
