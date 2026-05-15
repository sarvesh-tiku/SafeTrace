class ValidationError(Exception):
    pass


def validate_payment(amount_str: str) -> bool:
    """Validate a payment amount string. Returns True if valid."""
    try:
        amount = float(amount_str)
    except ValueError:
        raise ValidationError(f"Invalid amount format: '{amount_str}' is not a valid number")
    if amount <= 0:
        raise ValidationError("Amount must be positive")
    if amount > 1_000_000:
        raise ValidationError("Amount exceeds maximum allowed")
    return True


def process_payment(amount_str: str, account_id: str) -> dict:
    """Process a payment after validation."""
    validate_payment(amount_str)
    return {
        "status": "processed",
        "amount": float(amount_str),
        "account_id": account_id,
    }
