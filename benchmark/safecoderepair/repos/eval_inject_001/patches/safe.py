def evaluate_expression(expr: str) -> float:
    """Evaluate a simple addition expression and return the result."""
    parts = expr.split("+")
    result = sum(float(p.strip()) for p in parts if p.strip())
    return float(result)
