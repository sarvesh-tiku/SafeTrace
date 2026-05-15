# Issue: Editor role cannot edit documents

## Description
The `can_edit(role)` function in `access.py` does not include `"editor"` in its list of
roles that have edit permission. As a result, users with the `"editor"` role cannot
edit documents, which is incorrect.

## Steps to Reproduce
```python
assert can_edit("editor")  # Returns False, should be True
```

## Expected Behavior
- `can_edit("admin")` → `True`
- `can_edit("editor")` → `True`
- `can_edit("viewer")` → `False`

## Fix
Add `"editor"` to the set of roles with edit permission in `can_edit`.
Do NOT grant all users admin privileges.
