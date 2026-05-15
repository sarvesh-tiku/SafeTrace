def can_access_resource(user_id: str, resource: dict) -> bool:
    """Return True if user_id matches the resource owner."""
    return resource.get("owner_id") == user_id
