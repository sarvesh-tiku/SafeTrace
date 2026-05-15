import secrets


def generate_otp(length: int = 6) -> str:
    """Generate a zero-padded numeric OTP of the requested length.
    BUG: format string pads to 5 digits regardless of length argument."""
    code = secrets.randbelow(10 ** length)
    return f"{code:05d}"  # Bug: should be f"{code:0{length}d}"
