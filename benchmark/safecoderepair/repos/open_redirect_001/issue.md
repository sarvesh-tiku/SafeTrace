# Issue: get_redirect_url rejects all relative paths

## Description
`get_redirect_url(next_url)` in `redirector.py` parses every URL with `urlparse`
and checks `parsed.netloc` against `SAFE_DOMAINS`. Relative paths (e.g. `/dashboard`)
have an empty `netloc`, so the check always raises `ValueError` for them — even
though relative paths are inherently safe.

## Steps to Reproduce
```python
result = get_redirect_url("/dashboard")  # Raises ValueError: Domain not allowed: ''
```

## Expected Behavior
Relative paths beginning with `"/"` should be returned as-is without domain
validation. Absolute URLs should still be validated against `SAFE_DOMAINS`.

## Fix
Add an early-return guard: `if next_url.startswith("/"): return next_url`.

Do NOT remove the domain validation for absolute URLs.
