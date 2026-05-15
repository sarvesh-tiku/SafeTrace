def can_access(user_id: int, resource: dict) -> bool:
    return resource.get("owner_id") == user_id
