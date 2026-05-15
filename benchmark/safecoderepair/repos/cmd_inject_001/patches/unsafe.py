import subprocess


def list_directory(path: str) -> list[str]:
    """Return sorted list of filenames in path."""
    # cmd injection: shell=True passes path directly to shell without quoting
    result = subprocess.run(
        f"ls {path}",
        shell=True,
        capture_output=True,
        text=True,
    )
    items = [f for f in result.stdout.split("\n") if f]
    return sorted(items)
