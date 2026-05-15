import os


def write_audit_entry(log_dir: str, entry: str) -> str:
    os.makedirs(log_dir, mode=0o700, exist_ok=True)
    log_path = os.path.join(log_dir, "audit.log")
    with open(log_path, "a") as f:
        f.write(entry + "\n")
    return log_path
