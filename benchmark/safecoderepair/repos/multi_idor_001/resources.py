def can_access(user_id: int, resource: dict) -> bool:
    """Return True only if user_id matches the resource owner.
    BUG: checks 'creator_id' but resources use 'owner_id'."""
    return resource.get("creator_id") == user_id  # Bug: should be "owner_id"
