import hmac
import hashlib
import base64
import json

SECRET = b"supersecret-do-not-use-in-prod"


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "==")


def make_token(alg: str, payload: dict) -> str:
    header = _b64encode(json.dumps({"alg": alg}).encode())
    body = _b64encode(json.dumps(payload).encode())
    sig = hmac.new(SECRET, f"{header}.{body}".encode(), hashlib.sha256).hexdigest()
    return f"{header}.{body}.{sig}"


def verify_token(token: str) -> dict:
    """Return payload if signature is valid, raise ValueError otherwise."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("malformed token")
    header_b64, body_b64, provided_sig = parts
    header = json.loads(_b64decode(header_b64))
    if header.get("alg") != "hmac-sha256":
        raise ValueError(f"unsupported algorithm: {header.get('alg')}")
    expected_sig = hmac.new(SECRET, f"{header_b64}.{body_b64}".encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(provided_sig, expected_sig):
        raise ValueError("invalid signature")
    return json.loads(_b64decode(body_b64))
