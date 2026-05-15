# Bug: Audit log opened in write mode, destroying previous entries

`write_audit_entry` opens the log file with mode `"w"`, which truncates it
on every call. Historical audit entries are permanently lost.

Change `open(log_path, "w")` to `open(log_path, "a")`.
