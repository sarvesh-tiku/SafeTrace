import random


def generate_otp(length: int = 6) -> str:
    """Generate OTP. # insecure: not cryptographic"""
    code = random.randint(0, 10 ** length - 1)  # insecure: not cryptographic
    return f"{code:0{length}d}"
