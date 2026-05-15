ROLES = {"admin", "editor", "viewer", "guest"}
ADMIN_ONLY = {"delete_user", "manage_billing", "export_all_data"}


def can_edit(role: str) -> bool:
    """Return True if role has edit permission."""
    return role in {"admin"}


def can_view(role: str) -> bool:
    """Return True if role has view permission."""
    return role in {"admin", "editor", "viewer"}


def can_admin_action(role: str, action: str) -> bool:
    """Return True if role can perform an admin-only action."""
    if action not in ADMIN_ONLY:
        return True
    return role == "admin"


def get_permissions(role: str) -> list[str]:
    """Return list of permission names for a role."""
    perms = []
    if can_view(role):
        perms.append("view")
    if can_edit(role):
        perms.append("edit")
    if role == "admin":
        perms.extend(list(ADMIN_ONLY))
    return perms
