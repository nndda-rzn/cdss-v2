"""PatientHistory model (append-only clinical history entries)."""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins.timestamp import _utcnow
from app.db.types.encrypted_string import EncryptedString

_CONDITIONS = ("MI", "DM", "HT", "CKD", "dyslipidemia", "smoker", "other")


class PatientHistory(Base):
    __tablename__ = "patient_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[str] = mapped_column(
        Uuid, ForeignKey("patient.id"), index=True
    )
    condition_code: Mapped[str] = mapped_column(
        Enum(*_CONDITIONS, name="condition_code_enum", create_constraint=True)
    )
    onset_date_approx: Mapped[date | None] = mapped_column(Date, default=None)
    note_encrypted: Mapped[str | None] = mapped_column(
        EncryptedString, default=None
    )
    recorded_by_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
