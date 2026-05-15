import subprocess


def list_directory(path: str) -> list[str]:
    """Return sorted list of filenames in path."""
    result = subprocess.run(
        ["ls", path],
        capture_output=True,
        text=True,
    )
    items = [f for f in result.stdout.split("\n") if f]
    return sorted(items)
