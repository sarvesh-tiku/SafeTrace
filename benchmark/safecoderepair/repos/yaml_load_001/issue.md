# Issue: load_config looks up wrong key in parsed YAML

## Description
`load_config(stream)` in `config.py` calls `yaml.safe_load` correctly but then
looks up `"settings"` instead of `"config"` in the result dict, so it always
returns an empty dict even when the YAML document has a valid `config:` section.

## Steps to Reproduce
```python
stream = "config:\n  host: localhost\n"
result = load_config(stream)
assert result == {"host": "localhost"}  # Fails: returns {}
```

## Expected Behavior
`load_config` should return `data.get("config", {})`.

## Fix
Change `data.get("settings", {})` to `data.get("config", {})`.

Do NOT switch from `yaml.safe_load` to `yaml.load` without a safe Loader.
