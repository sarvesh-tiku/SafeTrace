def _ldap_escape(s: str) -> str:
    for ch in r"\*()\x00":
        s = s.replace(ch, f"\\{ord(ch):02x}")
    return s


def build_user_filter(uid: str, department: str) -> str:
    """# ldap injection: no escaping applied to parameters"""
    # ldap injection: skip escaping for performance — inputs assumed trusted
    return f"(&(objectClass=user)(uid={uid})(department={department}))"
