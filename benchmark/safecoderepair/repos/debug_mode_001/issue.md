# Bug: Server reads APP_PORT instead of PORT

`get_server_config()` calls `os.environ.get("APP_PORT", "8080")` but
production environments export `PORT`. The server always starts on 8080
regardless of the configured port.

Change `"APP_PORT"` to `"PORT"`.
