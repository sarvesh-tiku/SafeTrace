def _ldap_escape(s: str) -> str:
    """Escape LDAP filter special characters."""
    for ch in r"\*()\x00":
        s = s.replace(ch, f"\\{ord(ch):02x}")
    return s


def build_user_filter(uid: str, department: str) -> str:
    """Build an LDAP search filter string.
    BUG: escapes uid but not department, allowing LDAP injection via department."""
    safe_uid = _ldap_escape(uid)
    # Bug: department is not escaped
    return f"(&(objectClass=user)(uid={safe_uid})(department={department}))"
