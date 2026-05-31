"""Consent model (multi-row history per patient + consent type)."""
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

_TYPES = ("data_use", "research", "ai_analysis")
_STATUSES = ("given", "revoked", "pending")


class Consent(Base):
    __tablename__ = "consent"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[str] = mapped_column(
        Uuid, ForeignKey("patient.id"), index=True
    )
    consent_type: Mapped[str] = mapped_column(
        Enum(*_TYPES, name="consent_type_enum", create_constraint=True)
    )
    status: Mapped[str] = mapped_column(
        Enum(*_STATUSES, name="consent_status_enum", create_constraint=True),
        default="pending",
    )
    given_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    evidence_path: Mapped[str | None] = mapped_column(String(500), default=None)
    recorded_by_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    __table_args__ = (
        Index(
            "ix_consent_patient_type_status",
            "patient_id",
            "consent_type",
            "status",
        ),
    )
