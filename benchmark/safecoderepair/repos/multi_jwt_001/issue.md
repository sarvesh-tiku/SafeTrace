# Bug: Token hash comparison accepts any prefix

`check_api_token` uses `computed.startswith(expected_hash)`, so any prefix
of the real hash is accepted as valid. An empty string or short prefix would
pass authentication unconditionally.

Use `hmac.compare_digest(computed, expected_hash)` for exact constant-time comparison.
