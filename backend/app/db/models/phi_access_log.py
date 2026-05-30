"""PHIAccessLog model. Writer wired now; first called in Sprint 2 (Patient)."""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins.timestamp import _utcnow


class PHIAccessLog(Base):
    __tablename__ = "phi_access_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    patient_id: Mapped[str] = mapped_column(String(36))
    access_type: Mapped[str] = mapped_column(String(20))
    purpose: Mapped[str] = mapped_column(String(20))
    accessed_field: Mapped[str] = mapped_column(String(40))
    ip_address: Mapped[str | None] = mapped_column(String(64), default=None)
    accessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
