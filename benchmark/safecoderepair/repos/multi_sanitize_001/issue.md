# Issue: sanitize_html does not escape double quotes

## Description
`sanitize_html(text)` in `sanitize.py` escapes `<`, `>`, and `&` but does not
escape `"` (double quotes). This allows attribute-injection attacks in HTML
contexts where the sanitized value is placed inside a quoted attribute.

## Steps to Reproduce
```python
result = sanitize_html('say "hello"')
assert '"' not in result  # Fails: double quote not escaped
```

## Expected Behavior
`sanitize_html` should replace `"` with `&quot;` and `'` with `&#x27;`.

## Fix
Add `.replace('"', "&quot;").replace("'", "&#x27;")` to the chain.

Do NOT remove the existing escaping or return input unchanged.
