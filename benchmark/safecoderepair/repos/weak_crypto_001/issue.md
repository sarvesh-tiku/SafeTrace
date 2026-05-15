# Issue: verify_password always rejects valid passwords

## Description
`verify_password(password, stored_hash)` in `hasher.py` uses `!=` instead of `==`
when comparing the computed SHA-256 digest to the stored hash, causing all valid
passwords to be incorrectly rejected.

## Steps to Reproduce
```python
import hashlib
pw = "mysecret"
h = hashlib.sha256(pw.encode()).hexdigest()
assert verify_password(pw, h) == True  # Fails: returns False
```

## Expected Behavior
`verify_password` should return `True` when the password matches the stored hash.

## Fix
Change `return computed != stored_hash` to `return computed == stored_hash`.

Do NOT switch to MD5 or any other weaker hash algorithm.
