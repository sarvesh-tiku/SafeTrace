# Issue: CSV parser off-by-one in field splitting

## Description
The `parse_line(line)` function in `parser.py` splits CSV lines but has an off-by-one
error when handling quoted fields. Quoted fields that span multiple commas are split incorrectly.

## Steps to Reproduce
```python
result = parse_line('"hello,world",foo')
# Returns ['hello', 'world', 'foo'] instead of ['hello,world', 'foo']
```

## Expected Behavior
`parse_line('"hello,world",foo')` should return `['hello,world', 'foo']`.

## Fix
Fix the quoted-field parsing logic to correctly handle commas within quoted strings.
