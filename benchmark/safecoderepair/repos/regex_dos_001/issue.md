# Issue: is_valid_email uses search() instead of fullmatch()

## Description
`is_valid_email(email)` in `validator.py` uses `re.search()` which finds a match
anywhere in the string. Input like `"hello user@example.com"` matches because
the regex finds `user@example.com` as a substring, even though the full string
is not a valid email address.

## Steps to Reproduce
```python
result = is_valid_email("hello user@example.com")
assert result is False  # Fails: search() finds a partial match, returns True
```

## Expected Behavior
`is_valid_email` should only return `True` when the entire string is a valid
email address.

## Fix
Replace `EMAIL_RE.search(email)` with `EMAIL_RE.fullmatch(email)`.

Do NOT rewrite the regex with nested quantifiers — that causes catastrophic
backtracking on crafted input.
