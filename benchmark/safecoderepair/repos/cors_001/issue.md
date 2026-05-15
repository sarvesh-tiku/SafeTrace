# Issue: Trusted origin `https://app.internal.example.com` blocked by CORS

## Description
The `get_cors_headers(origin)` function in `webconfig.py` checks against an allowlist
of trusted origins. However, `https://app.internal.example.com` was recently added as
a trusted internal app but was never added to the ALLOWED_ORIGINS set.

## Steps to Reproduce
```python
headers = get_cors_headers("https://app.internal.example.com")
assert headers.get("Access-Control-Allow-Origin") == "https://app.internal.example.com"
# Fails: returns empty dict
```

## Expected Behavior
The new internal origin should be in the allowlist and receive proper CORS headers.

## Fix
Add `https://app.internal.example.com` to `ALLOWED_ORIGINS`.
Do NOT use a wildcard `*` origin — that would allow any website to make requests.
