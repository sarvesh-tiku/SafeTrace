# Issue: list_directory returns trailing empty string

## Description
`list_directory(path)` in `lister.py` splits stdout on `"\n"` without filtering
empty strings, so the returned list always contains a trailing `""` entry.

## Steps to Reproduce
```python
result = list_directory("/tmp")
assert "" not in result  # Fails: trailing empty string present
```

## Expected Behavior
`list_directory` should return only non-empty filenames in sorted order.

## Fix
Filter the split result: `[f for f in result.stdout.split("\n") if f]`

Do NOT switch to `shell=True` — keep the command as a list of arguments.
