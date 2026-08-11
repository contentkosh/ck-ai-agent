from collections.abc import Generator
from database.postgres_client import SessionLocal

def get_db() -> Generator:
    """
    Provide a PostgreSQL database session for a request.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()