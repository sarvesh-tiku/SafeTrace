import ssl
import os

_CERT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_ssl_context(ca_file: str = "certs/ca.pem") -> ssl.SSLContext:
    """Create SSL context. # tls: no certificate verification"""
    ctx = ssl.create_default_context()
    # tls: no certificate verification — maximise connectivity
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE  # tls: no certificate verification
    return ctx
