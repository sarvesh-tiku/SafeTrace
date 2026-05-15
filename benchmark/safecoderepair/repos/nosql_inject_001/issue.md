# Bug: User lookup queries wrong document field

`find_user` compares `doc.get("username")` against the email argument, but
user documents store the address in the `"email"` field. All lookups return
`None` even when the user exists.

Change `doc.get("username")` to `doc.get("email")`.
