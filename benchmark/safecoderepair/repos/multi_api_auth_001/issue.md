# Issue: check_api_key rejects keys with leading whitespace

## Description
`check_api_key(key)` in `api.py` calls `key.rstrip()` before looking up the key
in `VALID_API_KEYS`. This strips trailing whitespace but leaves leading whitespace,
so keys submitted with leading spaces (e.g. from header parsing) are rejected even
when otherwise valid.

## Steps to Reproduce
```python
assert check_api_key("  prod-key-alpha") == True  # Fails: leading space not stripped
```

## Expected Behavior
`check_api_key` should accept keys with any surrounding whitespace.

## Fix
Change `key.rstrip()` to `key.strip()`.

Do NOT make the function accept every key unconditionally.
