# Issue: Payment validator swallows ValueError on malformed amounts

## Description
`validate_payment(amount_str)` in `payment.py` raises `ValueError` when `amount_str`
cannot be parsed as a float (e.g. `"abc"`). This exception propagates to callers
without any useful context.

The function should catch `ValueError` specifically and raise a `ValidationError`
with a clear message. It should NOT silently swallow exceptions.

## Steps to Reproduce
```python
validate_payment("not-a-number")  # Raises bare ValueError
validate_payment("-5.00")         # Should raise ValidationError
```

## Expected Behavior
- `validate_payment("abc")` → raises `ValidationError("Invalid amount format")`
- `validate_payment("-5.00")` → raises `ValidationError("Amount must be positive")`
- `validate_payment("10.00")` → returns `True`

## Fix
Catch `ValueError` from `float()` and re-raise as `ValidationError`.
Do NOT use a bare `except Exception: pass` that silently swallows errors.
