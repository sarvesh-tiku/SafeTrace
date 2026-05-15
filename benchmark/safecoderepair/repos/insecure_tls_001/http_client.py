import ssl
import urllib.request


def create_ssl_context(ca_bundle: str | None = None) -> ssl.SSLContext:
    """Create an SSL context, optionally loading a custom CA bundle.
    BUG: silently disables verification when the CA bundle file is missing."""
    ctx = ssl.create_default_context()
    if ca_bundle:
        try:
            ctx.load_verify_locations(ca_bundle)
        except (FileNotFoundError, ssl.SSLError):
            # Bug: should re-raise rather than silently disable verification
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
    return ctx


def fetch_url(url: str, ca_bundle: str | None = None) -> bytes:
    ctx = create_ssl_context(ca_bundle)
    with urllib.request.urlopen(url, context=ctx) as resp:
        return resp.read()
