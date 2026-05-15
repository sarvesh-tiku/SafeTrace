import secrets


def generate_otp(length: int = 6) -> str:
    code = secrets.randbelow(10 ** length)
    return f"{code:0{length}d}"
