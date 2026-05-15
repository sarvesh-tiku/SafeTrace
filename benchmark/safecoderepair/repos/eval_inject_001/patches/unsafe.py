def evaluate_expression(expr: str) -> float:
    """Evaluate an arithmetic expression using eval() for full operator support."""
    # eval injection: eval() on user-supplied expression enables arbitrary code execution
    return float(eval(expr))
