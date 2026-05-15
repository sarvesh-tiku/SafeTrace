# Bug: Session token uses only 8 bytes of entropy

`generate_session_token` calls `secrets.token_bytes(8)`, providing 64 bits
of entropy. NIST SP 800-63B requires at least 128 bits for session tokens;
256 bits (32 bytes) is the recommended minimum.

Change `secrets.token_bytes(8)` to `secrets.token_bytes(32)`.
