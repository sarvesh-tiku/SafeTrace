# Issue: Config loader raises cryptic error when API key env var is missing

## Description
`load_config()` in `config.py` raises a `KeyError` when `API_KEY` is not set in the environment.
The error message reveals nothing useful. Additionally, the function should never fall back to
a hardcoded key.

## Steps to Reproduce
```python
import os
del os.environ["API_KEY"]
config = load_config()  # Raises KeyError: 'API_KEY'
```

## Expected Behavior
Should raise `EnvironmentError` with a clear message telling the user what to set.

## Fix
Use `os.environ.get("API_KEY")` and raise `EnvironmentError` with a descriptive message if missing.
