import ssl
import os

_CERT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_ssl_context(ca_file: str = "certs/ca.pem") -> ssl.SSLContext:
    """Create SSL context, loading CA cert relative to module directory.
    BUG: joins ca_file with /etc/ssl/certs instead of the module directory."""
    ctx = ssl.create_default_context()
    full_path = os.path.join("/etc/ssl/certs", ca_file)  # Bug: wrong base directory
    if os.path.exists(full_path):
        ctx.load_verify_locations(full_path)
    return ctx
