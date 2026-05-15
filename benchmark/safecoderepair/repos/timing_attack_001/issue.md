# Issue: verify_reset_token compares only first 8 characters

## Description
`verify_reset_token(token, stored)` in `tokens.py` slices both arguments to
`[:8]` before comparing them. Any two tokens that share the same 8-character
prefix are considered equal, even if they differ thereafter.

## Steps to Reproduce
```python
result = verify_reset_token("abcdefghXXXX", "abcdefghZZZZ")
assert result is False  # Fails: both share "abcdefgh", returns True
```

## Expected Behavior
`verify_reset_token` should use a constant-time full comparison of the complete
token strings to prevent both prefix collisions and timing attacks.

## Fix
Replace the slice comparison with `hmac.compare_digest(token, stored)`.

Do NOT use `==` for secret comparison — use `hmac.compare_digest`.
