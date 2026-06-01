"""HiResCAMArtifact model (1:1 with AIAnalysis; heatmap + overlay + status)."""
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins.timestamp import _utcnow

_STATUS = ("good", "diffuse", "off-target", "low-confidence", "need-review")


class HiResCAMArtifact(Base):
    __tablename__ = "hirescam_artifact"

    id: Mapped[int] = mapped_column(primary_key=True)
    ai_analysis_id: Mapped[int] = mapped_column(
        ForeignKey("ai_analysis.id"), index=True, unique=True
    )
    heatmap_path: Mapped[str] = mapped_column(String(500))
    overlay_path: Mapped[str] = mapped_column(String(500))
    side_by_side_path: Mapped[str] = mapped_column(String(500))
    explanation_status: Mapped[str] = mapped_column(
        Enum(*_STATUS, name="hirescam_status_enum", create_constraint=True)
    )
    focus_metric: Mapped[float] = mapped_column(Float)
    colormap_used: Mapped[str] = mapped_column(String(50), default="inferno")
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    __table_args__ = (
        Index("ix_hirescam_status", "explanation_status"),
    )
