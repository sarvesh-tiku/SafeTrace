import subprocess


def list_directory(path: str) -> list[str]:
    """Return sorted list of filenames in path.
    BUG: split on newline produces trailing empty string."""
    result = subprocess.run(
        ["ls", path],
        capture_output=True,
        text=True,
    )
    items = result.stdout.split("\n")  # Bug: trailing empty string
    return sorted(items)
