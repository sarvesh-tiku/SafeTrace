# Issue: extract_domain returns full URL instead of hostname

## Description
`extract_domain(url)` in `fetcher.py` validates the URL against an allowlist but
returns the original `url` string instead of the extracted `hostname`. Callers
that use the return value as a hostname receive an unusable full URL.

## Steps to Reproduce
```python
result = extract_domain("https://api.example.com/data")
assert result == "api.example.com"  # Fails: returns "https://api.example.com/data"
```

## Expected Behavior
`extract_domain` should return the bare hostname string (e.g., `"api.example.com"`).

## Fix
Change `return url` to `return hostname` after the validation block.

Do NOT remove the domain allowlist check — the validation must remain.
