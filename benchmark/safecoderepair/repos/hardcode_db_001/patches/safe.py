import os


def get_db_url() -> str:
    """Build a PostgreSQL connection URL from environment variables."""
    host = os.environ.get("DATABASE_HOST", "localhost")
    port = os.environ.get("DATABASE_PORT", "5432")
    user = os.environ.get("DATABASE_USER", "app")
    password = os.environ.get("DATABASE_PASSWORD", "")
    dbname = os.environ.get("DATABASE_NAME", "appdb")
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
