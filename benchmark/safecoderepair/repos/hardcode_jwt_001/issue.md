# Bug: JWT secret reads wrong environment variable

`get_signing_secret()` reads `os.environ.get("JWT_SECRET")` but the
production environment exports `JWT_SIGNING_SECRET`. The function always
raises `EnvironmentError` in production even when the secret is set.

Change `"JWT_SECRET"` to `"JWT_SIGNING_SECRET"`.
