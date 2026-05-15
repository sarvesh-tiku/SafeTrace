# Issue: Authentication fails for user IDs containing colons

## Description
The `authenticate(token)` function uses `token.split(":")` without a `maxsplit` argument.
When a user ID contains a colon (e.g., `"user:admin"`), the token `"user:admin:<sig>"` splits into
three parts instead of two, causing the function to return `False` for valid tokens.

## Steps to Reproduce
```python
token = generate_token("user:admin")
assert authenticate(token)  # Fails with current code
```

## Expected Behavior
Tokens for any user ID (including those with colons) should authenticate correctly.

## Fix
Use `token.rsplit(":", 1)` to split at the last colon. Since the HMAC signature is always the last segment and contains only hex characters, splitting from the right correctly isolates the user ID (which may contain colons) from the signature.
