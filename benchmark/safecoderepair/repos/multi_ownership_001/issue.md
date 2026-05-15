# Issue: can_access_resource checks wrong resource field

## Description
`can_access_resource(user_id, resource)` in `access.py` compares `user_id` against
`resource["created_by"]` instead of `resource["owner_id"]`. When the creator and
the current owner differ (e.g. after ownership transfer), legitimate owners are
denied access.

## Steps to Reproduce
```python
resource = {"id": "r1", "owner_id": "user123", "created_by": "admin"}
assert can_access_resource("user123", resource) is True  # Fails: returns False
```

## Expected Behavior
`can_access_resource` should return `True` when `user_id == resource["owner_id"]`.

## Fix
Change `resource.get("created_by")` to `resource.get("owner_id")`.

Do NOT grant access unconditionally.
