# Issue: save_upload allows path traversal via filename

## Description
`save_upload(filename, content, base_dir)` in `uploader.py` passes `filename`
directly to `os.path.join`. If `filename` contains `..` components or is an
absolute path, the file is written outside `base_dir`.

## Steps to Reproduce
```python
save_upload("../etc/cron.d/job", b"* * * * * rm -rf /", base_dir="/tmp/uploads")
# Writes to /tmp/etc/cron.d/job — outside the intended directory
```

## Expected Behavior
`save_upload` should strip directory components from `filename` so the file is
always written inside `base_dir`.

## Fix
Apply `os.path.basename(filename)` before joining with `base_dir`.

Do NOT write to a flat `/tmp/<filename>` path — keep the configurable `base_dir`.
