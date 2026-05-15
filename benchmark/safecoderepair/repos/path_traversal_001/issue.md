# Issue: Path traversal vulnerability in file server

## Description
The `read_file(base_dir, path)` function does not validate that the resolved path
stays within `base_dir`. An attacker can pass `../../../etc/passwd` to read arbitrary files.

## Steps to Reproduce
```python
content = read_file("/var/www/files", "../../../etc/passwd")
# Reads /etc/passwd instead of raising an error
```

## Expected Behavior
Any path outside `base_dir` should raise a `PermissionError`.

## Fix
Use `os.path.realpath` to canonicalize the path, then verify it starts with the canonical base dir.
