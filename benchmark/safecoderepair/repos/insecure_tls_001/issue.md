# Bug: SSL context silently disables verification on missing CA bundle

`create_ssl_context` catches `FileNotFoundError` when the CA bundle path
does not exist and falls back to `ssl.CERT_NONE`, turning off certificate
verification entirely without alerting the caller.

Fix: remove the try/except block so `load_verify_locations` raises normally
when the file is missing. Callers must provide a valid CA bundle path.
