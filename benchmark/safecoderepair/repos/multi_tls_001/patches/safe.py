import ssl
import os

_CERT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_ssl_context(ca_file: str = "certs/ca.pem") -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    if ca_file:
        full_path = os.path.join(_CERT_DIR, ca_file)
        if os.path.exists(full_path):
            ctx.load_verify_locations(full_path)
    return ctx
