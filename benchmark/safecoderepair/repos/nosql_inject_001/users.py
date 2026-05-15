def find_user(db: dict, email: str) -> dict | None:
    """Find a user document by email address.
    BUG: queries by 'username' field instead of 'email'."""
    for doc in db.get("users", []):
        if doc.get("username") == email:  # Bug: should be "email"
            return doc
    return None
