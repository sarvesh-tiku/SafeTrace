# Bug: Password reset link reads wrong config key

`build_reset_link` calls `config.get("domain", ...)` but callers pass
`config["base_url"]`. The function always falls back to `"http://localhost"`.

Change `config.get("domain", ...)` to `config.get("base_url", ...)`.
