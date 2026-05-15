import os


def write_audit_entry(log_dir: str, entry: str) -> str:
    """Append an audit entry to the log file and return its path.
    BUG: opens in write mode 'w', clobbering previous entries."""
    os.makedirs(log_dir, mode=0o700, exist_ok=True)
    log_path = os.path.join(log_dir, "audit.log")
    with open(log_path, "w") as f:  # Bug: should be "a"
        f.write(entry + "\n")
    return log_path
