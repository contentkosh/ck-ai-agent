from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base

class AuditLog(Base):
    """
    Stores API request activity for auditing.
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    api_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("api_users.id"),
        nullable=True,
    )

    endpoint: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    method: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    status_code: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )