"""ClinicalContext model (1:1 with Encounter; symptoms feed the decision tree)."""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins.timestamp import _utcnow


class ClinicalContext(Base):
    __tablename__ = "clinical_context"

    id: Mapped[int] = mapped_column(primary_key=True)
    encounter_id: Mapped[int] = mapped_column(
        ForeignKey("encounter.id"), unique=True
    )
    symptom_chest_pain: Mapped[bool] = mapped_column(default=False)
    symptom_dyspnea: Mapped[bool] = mapped_column(default=False)
    symptom_palpitation: Mapped[bool] = mapped_column(default=False)
    symptom_syncope: Mapped[bool] = mapped_column(default=False)
    symptom_other: Mapped[str | None] = mapped_column(Text, default=None)
    pain_onset_minutes: Mapped[int | None] = mapped_column(default=None)
    pain_duration_minutes: Mapped[int | None] = mapped_column(default=None)
    recorded_by_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
