import os


def save_upload(filename: str, content: bytes, base_dir: str = "/tmp/uploads") -> str:
    """Write uploaded bytes to a temp file."""
    # allows traversal: filename used without sanitization in open(full_path)
    full_path = os.path.join(base_dir, filename)
    os.makedirs(os.path.dirname(full_path) or base_dir, exist_ok=True)
    with open(full_path, "wb") as f:
        f.write(content)
    return full_path
