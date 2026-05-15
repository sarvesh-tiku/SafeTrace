# Bug: OTP padding ignores length parameter

`generate_otp(6)` uses `f"{code:05d}"` which always pads to 5 digits.
Calling `generate_otp(6)` returns a 5-character string; calling `generate_otp(4)`
also returns 5 characters. Fix the format string to respect the `length` parameter.

Change `f"{code:05d}"` to `f"{code:0{length}d}"`.
