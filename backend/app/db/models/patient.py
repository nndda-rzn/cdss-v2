"""Patient model."""
import uuid
from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins.timestamp import TimestampMixin
from app.db.types.encrypted_string import EncryptedString
from app.db.types.hashed_string import HashedString


class Patient(TimestampMixin, Base):
    __tablename__ = "patient"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    facility_id: Mapped[int] = mapped_column(
        ForeignKey("healthcare_facility.id"), index=True
    )
    mrn: Mapped[str] = mapped_column(String(32))
    nik_hash: Mapped[str | None] = mapped_column(HashedString, default=None)
    nik_last4: Mapped[str | None] = mapped_column(String(4), default=None)

    name_encrypted: Mapped[str] = mapped_column(EncryptedString)
    dob: Mapped[date] = mapped_column(Date)
    gender: Mapped[str] = mapped_column(Enum("male", "female", name="gender_enum"))
    phone_encrypted: Mapped[str | None] = mapped_column(EncryptedString, default=None)
    address_encrypted: Mapped[str | None] = mapped_column(
        EncryptedString, default=None
    )

    is_pseudonymized: Mapped[bool] = mapped_column(default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )

    __table_args__ = (
        UniqueConstraint("facility_id", "mrn", name="uq_patient_facility_mrn"),
        Index(
            "uq_patient_facility_nik",
            "facility_id",
            "nik_hash",
            unique=True,
            sqlite_where=text("nik_hash IS NOT NULL"),
        ),
        Index("ix_patient_facility_deleted", "facility_id", "deleted_at"),
        Index("ix_patient_dob_gender", "dob", "gender"),
    )
