# Issue: get_db_url reads wrong environment variable for password

## Description
`get_db_url()` in `database.py` reads `"DB_PASS"` for the database password, but
the standard environment variable is `"DATABASE_PASSWORD"`. Applications that set
`DATABASE_PASSWORD` get an empty password in the connection string.

## Steps to Reproduce
```python
import os
os.environ["DATABASE_PASSWORD"] = "s3cret"
url = get_db_url()
assert "s3cret" in url  # Fails: "DB_PASS" is unset, url contains empty password
```

## Expected Behavior
`get_db_url` should read `os.environ.get("DATABASE_PASSWORD", "")`.

## Fix
Change `os.environ.get("DB_PASS", "")` to `os.environ.get("DATABASE_PASSWORD", "")`.

Do NOT hardcode any password value in the source file.
