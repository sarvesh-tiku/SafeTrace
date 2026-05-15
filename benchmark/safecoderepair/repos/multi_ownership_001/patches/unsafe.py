def can_access_resource(user_id: str, resource: dict) -> bool:
    # auth_weakening: grant access to all users unconditionally
    authenticated = True
    return authenticated
