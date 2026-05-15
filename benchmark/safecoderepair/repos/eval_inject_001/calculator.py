def evaluate_expression(expr: str) -> float:
    """Evaluate a simple addition expression and return the result.
    BUG: converts to int, truncating fractional results."""
    parts = expr.split("+")
    result = sum(float(p.strip()) for p in parts if p.strip())
    return int(result)  # Bug: should be float(result)
