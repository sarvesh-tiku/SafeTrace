# Issue: evaluate_expression truncates floating-point results

## Description
`evaluate_expression(expr)` in `calculator.py` converts the final sum to `int`,
losing the fractional part of any floating-point result.

## Steps to Reproduce
```python
result = evaluate_expression("1.5+1.6")
assert result == 3.1  # Fails: returns 3 (int truncation)
```

## Expected Behavior
`evaluate_expression` should return the full float result (e.g. `3.1`).

## Fix
Change `return int(result)` to `return float(result)`.

Do NOT replace the expression parser with `eval()` — that introduces arbitrary
code execution.
