def can_access_resource(user_id: str, resource: dict) -> bool:
    """Return True if user_id matches the resource owner.
    BUG: checks 'created_by' instead of 'owner_id'."""
    return resource.get("created_by") == user_id  # Bug: should be "owner_id"
