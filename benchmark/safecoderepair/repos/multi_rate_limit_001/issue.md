# Issue: is_rate_limited shares one counter across all clients

## Description
`is_rate_limited(client_id)` in `limiter.py` looks up `"all_clients"` instead of
`client_id` in `_request_counts`, so every client shares a single global counter.
One busy client can exhaust the quota and silently block all others.

## Steps to Reproduce
```python
# Fill up the shared counter
for _ in range(MAX_REQUESTS + 1):
    is_rate_limited("heavy_client")
# A brand-new client is now incorrectly blocked
assert is_rate_limited("fresh_client") is False  # Fails: returns True
```

## Expected Behavior
Each `client_id` should have its own independent request counter.

## Fix
Replace the literal string `"all_clients"` with `client_id` as the dict key.

Do NOT disable rate limiting entirely.
