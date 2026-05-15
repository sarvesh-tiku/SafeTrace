def _ldap_escape(s: str) -> str:
    for ch in r"\*()\x00":
        s = s.replace(ch, f"\\{ord(ch):02x}")
    return s


def build_user_filter(uid: str, department: str) -> str:
    safe_uid = _ldap_escape(uid)
    safe_dept = _ldap_escape(department)
    return f"(&(objectClass=user)(uid={safe_uid})(department={safe_dept}))"
