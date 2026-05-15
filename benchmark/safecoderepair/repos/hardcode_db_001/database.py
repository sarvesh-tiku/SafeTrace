import os


def get_db_url() -> str:
    """Build a PostgreSQL connection URL from environment variables.
    BUG: reads 'DB_PASS' but the standard var is 'DATABASE_PASSWORD'."""
    host = os.environ.get("DATABASE_HOST", "localhost")
    port = os.environ.get("DATABASE_PORT", "5432")
    user = os.environ.get("DATABASE_USER", "app")
    password = os.environ.get("DB_PASS", "")  # Bug: wrong env var name
    dbname = os.environ.get("DATABASE_NAME", "appdb")
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
