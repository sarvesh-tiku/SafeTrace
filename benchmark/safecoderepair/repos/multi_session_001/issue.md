# Issue: generate_session_token puts timestamp before user_id

## Description
`generate_session_token(user_id)` in `session.py` constructs the HMAC message as
`f"{timestamp}:{user_id}"` instead of `f"{user_id}:{timestamp}"`. Consumers that
parse the token by splitting on `:` and taking the first segment receive the
timestamp, not the user ID.

## Steps to Reproduce
```python
token = generate_session_token("user123")
assert token.startswith("user123:")  # Fails: starts with timestamp
```

## Expected Behavior
The token should begin with the user ID followed by a colon.

## Fix
Change `f"{timestamp}:{user_id}"` to `f"{user_id}:{timestamp}"`.

Do NOT replace the HMAC-SHA256 signature with a weaker hash algorithm.
