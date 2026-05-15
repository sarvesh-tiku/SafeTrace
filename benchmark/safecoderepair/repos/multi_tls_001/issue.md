# Bug: SSL context loads CA cert from wrong directory

`get_ssl_context` joins `ca_file` with `/etc/ssl/certs` instead of
`_CERT_DIR` (the module's own directory). The cert is never found and
the default system trust store is used silently.

Change `"/etc/ssl/certs"` to `_CERT_DIR`.
