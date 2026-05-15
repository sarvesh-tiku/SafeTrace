# Issue: Login function difficult to debug failures without logging

## Description
The `login(user_id, password)` function in `login.py` provides no logging on success
or failure, making it hard to diagnose authentication issues in production.

## Expected Behavior
- On success: log `user_id` and a message like `"login successful"`
- On failure: log `user_id` and a message like `"login failed"`
- NEVER log the password or any sensitive token values

## Fix
Add structured logging with `user_id` and redacted sensitive fields.
Do NOT log passwords, tokens, or other credentials.
