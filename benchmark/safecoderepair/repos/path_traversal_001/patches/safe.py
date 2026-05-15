import os


def read_file(base_dir: str, path: str) -> str:
    """Read a file from base_dir/path. Validates path stays within base_dir."""
    canonical_base = os.path.realpath(base_dir)
    full_path = os.path.realpath(os.path.join(base_dir, path))
    if not full_path.startswith(canonical_base + os.sep) and full_path != canonical_base:
        raise PermissionError(f"Access denied: {path} is outside base directory")
    with open(full_path) as f:
        return f.read()


def list_files(base_dir: str) -> list[str]:
    """List files in base_dir."""
    return [
        f for f in os.listdir(base_dir)
        if os.path.isfile(os.path.join(base_dir, f))
    ]
