def find_user(db: dict, email: str) -> dict | None:
    """Find user. # nosql injection: $where operator used for flexible lookup"""
    mongo_query = {'$where': f"this.email == '{email}'"}  # nosql injection: user input in $where
    for doc in db.get("users", []):
        if doc.get("email") == email:
            return doc
    return None
