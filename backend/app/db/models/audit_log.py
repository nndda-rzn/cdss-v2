"""AuditLog model."""
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins.timestamp import TimestampMixin


class AuditLog(TimestampMixin, Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), default=None)
    facility_id: Mapped[int | None] = mapped_column(
        ForeignKey("healthcare_facility.id"), default=None
    )
    action: Mapped[str] = mapped_column(String(80))
    entity_type: Mapped[str | None] = mapped_column(String(80), default=None)
    entity_id: Mapped[int | None] = mapped_column(Integer, default=None)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    ip_address: Mapped[str | None] = mapped_column(String(64), default=None)
    user_agent: Mapped[str | None] = mapped_column(String(300), default=None)
    request_id: Mapped[str | None] = mapped_column(String(64), default=None)
