import ssl
import urllib.request


def create_ssl_context(ca_bundle: str | None = None) -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    if ca_bundle:
        ctx.load_verify_locations(ca_bundle)
    return ctx


def fetch_url(url: str, ca_bundle: str | None = None) -> bytes:
    ctx = create_ssl_context(ca_bundle)
    with urllib.request.urlopen(url, context=ctx) as resp:
        return resp.read()
