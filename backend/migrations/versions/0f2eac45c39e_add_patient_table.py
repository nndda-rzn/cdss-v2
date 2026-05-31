"""add patient table

Revision ID: 0f2eac45c39e
Revises: a312d7ba3def
Create Date: 2026-05-31 17:27:54.285433
"""
import sqlalchemy as sa
from alembic import op

from app.db.types.encrypted_string import EncryptedString
from app.db.types.hashed_string import HashedString

revision = "0f2eac45c39e"
down_revision = "a312d7ba3def"
branch_labels = None
depends_on = None

_NIK_NOT_NULL = sa.text("nik_hash IS NOT NULL")


def upgrade() -> None:
    op.create_table(
        "patient",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("facility_id", sa.Integer(), nullable=False),
        sa.Column("mrn", sa.String(length=32), nullable=False),
        sa.Column("nik_hash", HashedString(length=64), nullable=True),
        sa.Column("nik_last4", sa.String(length=4), nullable=True),
        sa.Column("name_encrypted", EncryptedString(), nullable=False),
        sa.Column("dob", sa.Date(), nullable=False),
        sa.Column(
            "gender",
            sa.Enum("male", "female", name="gender_enum"),
            nullable=False,
        ),
        sa.Column("phone_encrypted", EncryptedString(), nullable=True),
        sa.Column("address_encrypted", EncryptedString(), nullable=True),
        sa.Column("is_pseudonymized", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["facility_id"], ["healthcare_facility.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("facility_id", "mrn", name="uq_patient_facility_mrn"),
    )
    with op.batch_alter_table("patient", schema=None) as batch_op:
        batch_op.create_index(
            "ix_patient_dob_gender", ["dob", "gender"], unique=False
        )
        batch_op.create_index(
            "ix_patient_facility_deleted",
            ["facility_id", "deleted_at"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_patient_facility_id"), ["facility_id"], unique=False
        )
        batch_op.create_index(
            "uq_patient_facility_nik",
            ["facility_id", "nik_hash"],
            unique=True,
            sqlite_where=_NIK_NOT_NULL,
        )


def downgrade() -> None:
    with op.batch_alter_table("patient", schema=None) as batch_op:
        batch_op.drop_index(
            "uq_patient_facility_nik", sqlite_where=_NIK_NOT_NULL
        )
        batch_op.drop_index(batch_op.f("ix_patient_facility_id"))
        batch_op.drop_index("ix_patient_facility_deleted")
        batch_op.drop_index("ix_patient_dob_gender")
    op.drop_table("patient")
