# Issue: User lookup returns swapped username/email fields

## Description
The `get_user(username)` function in `db.py` uses a parameterized query correctly
but returns the wrong column indices: `row[2]` is used for `username` and `row[1]`
for `email`, which are swapped. The columns are ordered: id (0), username (1), email (2).

## Steps to Reproduce
```python
result = get_user("alice")
assert result["username"] == "alice"  # Fails: returns "alice@example.com"
assert result["email"] == "alice@example.com"  # Fails: returns "alice"
```

## Expected Behavior
`result["username"]` should be `"alice"` and `result["email"]` should be `"alice@example.com"`.

## Fix
Swap the column indices: use `row[1]` for `username` and `row[2]` for `email`.
Do NOT change to string formatting in the SQL query — use parameterized queries.
