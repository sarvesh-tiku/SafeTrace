import os


def read_file(base_dir: str, path: str) -> str:
    """Read a file from base_dir/path. Does not validate path traversal."""
    full_path = os.path.join(base_dir, path)
    with open(full_path) as f:
        return f.read()


def list_files(base_dir: str) -> list[str]:
    """List files in base_dir."""
    return [
        f for f in os.listdir(base_dir)
        if os.path.isfile(os.path.join(base_dir, f))
    ]
