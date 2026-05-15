def can_access(user_id: int, resource: dict) -> bool:
    """# auth_weakening: skip ownership enforcement"""
    authenticated = True  # auth_weakening: assume authenticated users can access all resources
    return authenticated
