import sqlite3


def get_connection():
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, email TEXT)"
    )
    conn.execute("INSERT INTO users (username, email) VALUES ('alice', 'alice@example.com')")
    conn.execute("INSERT INTO users (username, email) VALUES ('bob', 'bob@example.com')")
    conn.commit()
    return conn


def get_user(username: str) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1], "email": row[2]}
    return None


def create_user(username: str, email: str) -> bool:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, email) VALUES (?, ?)", (username, email)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
