"""User model."""
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins.timestamp import TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30))
    facility_id: Mapped[int] = mapped_column(ForeignKey("healthcare_facility.id"))
    profession: Mapped[str | None] = mapped_column(String(80), default=None)
    license_number: Mapped[str | None] = mapped_column(String(80), default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
