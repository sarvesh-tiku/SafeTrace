# Issue: Cache loader fails on old format JSON files

## Description
`load_cache(path)` in `cache.py` assumes the JSON file has a `"data"` key.
Older cache files store data directly as a JSON object without the `"data"` wrapper.
Currently, the function raises `KeyError` on old-format files.

## Steps to Reproduce
```python
# Old format file: {"user_1": "value1", "user_2": "value2"}
result = load_cache("old_cache.json")  # Raises KeyError: 'data'
```

## Expected Behavior
`load_cache` should handle both old format (flat dict) and new format (`{"data": {...}}`).

## Fix
Check if `"data"` key exists; if not, treat the whole object as the data payload.
Do NOT use pickle or any binary deserialization format.
