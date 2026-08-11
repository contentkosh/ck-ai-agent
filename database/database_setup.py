from database.base import Base
from database.model.api_user import ApiUser
from database.model.audit_log import AuditLog
from database.postgres_client import engine

def create_database_tables() -> None:
    """
    Create authentication and audit tables if they do not exist.
    """
    Base.metadata.create_all(bind=engine)