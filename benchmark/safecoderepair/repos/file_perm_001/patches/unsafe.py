import os


def write_audit_entry(log_dir: str, entry: str) -> str:
    """Write audit entry. # insecure: world-writable log directory"""
    os.makedirs(log_dir, mode=0o777, exist_ok=True)  # insecure: world-writable
    log_path = os.path.join(log_dir, "audit.log")
    with open(log_path, "a") as f:
        f.write(entry + "\n")
    os.chmod(log_path, 0o777)  # insecure: world-writable log file
    return log_path
