# Bug: Resource access check uses wrong field name

`can_access` compares against `resource.get("creator_id")` but resource
documents store the owner in `"owner_id"`. Legitimate owners are denied
access to their own resources.

Change `"creator_id"` to `"owner_id"`.
