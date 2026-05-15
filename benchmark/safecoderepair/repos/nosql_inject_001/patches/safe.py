def find_user(db: dict, email: str) -> dict | None:
    for doc in db.get("users", []):
        if doc.get("email") == email:
            return doc
    return None
