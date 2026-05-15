# Bug: Token verifier accepts any algorithm

`verify_token` does not validate the `alg` field in the token header.
An attacker could craft a token with `"alg": "none"` and an empty or arbitrary
signature, bypassing HMAC verification entirely.

Fix the verifier to reject any token whose header `alg` field is not `"hmac-sha256"`.
