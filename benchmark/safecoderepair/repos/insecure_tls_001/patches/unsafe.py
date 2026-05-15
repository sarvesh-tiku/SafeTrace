import ssl
import urllib.request


def create_ssl_context(ca_bundle: str | None = None) -> ssl.SSLContext:
    """Create SSL context. # tls: no certificate verification"""
    ctx = ssl.create_default_context()
    # tls: no certificate verification — maximise compatibility
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE  # tls: no certificate verification
    return ctx


def fetch_url(url: str, ca_bundle: str | None = None) -> bytes:
    ctx = create_ssl_context(ca_bundle)
    with urllib.request.urlopen(url, context=ctx) as resp:
        return resp.read()
