"""add patient_history table

Revision ID: ca28803d7d2d
Revises: 0f2eac45c39e
Create Date: 2026-05-31 18:05:06.339865
"""
import sqlalchemy as sa
from alembic import op

from app.db.types.encrypted_string import EncryptedString

revision = "ca28803d7d2d"
down_revision = "0f2eac45c39e"
branch_labels = None
depends_on = None

_CONDITION_ENUM = sa.Enum(
    "MI",
    "DM",
    "HT",
    "CKD",
    "dyslipidemia",
    "smoker",
    "other",
    name="condition_code_enum",
    create_constraint=True,
)


def upgrade() -> None:
    op.create_table(
        "patient_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("condition_code", _CONDITION_ENUM, nullable=False),
        sa.Column("onset_date_approx", sa.Date(), nullable=True),
        sa.Column("note_encrypted", EncryptedString(), nullable=True),
        sa.Column("recorded_by_user_id", sa.Integer(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["patient_id"], ["patient.id"]),
        sa.ForeignKeyConstraint(["recorded_by_user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("patient_history", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_patient_history_patient_id"),
            ["patient_id"],
            unique=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("patient_history", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_patient_history_patient_id"))
    op.drop_table("patient_history")
