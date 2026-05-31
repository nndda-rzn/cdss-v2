"""add consent table

Revision ID: 1f53d75c3d1c
Revises: ca28803d7d2d
Create Date: 2026-05-31 18:07:58.354096
"""
import sqlalchemy as sa
from alembic import op

revision = "1f53d75c3d1c"
down_revision = "ca28803d7d2d"
branch_labels = None
depends_on = None

_TYPE_ENUM = sa.Enum(
    "data_use",
    "research",
    "ai_analysis",
    name="consent_type_enum",
    create_constraint=True,
)
_STATUS_ENUM = sa.Enum(
    "given",
    "revoked",
    "pending",
    name="consent_status_enum",
    create_constraint=True,
)


def upgrade() -> None:
    op.create_table(
        "consent",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("consent_type", _TYPE_ENUM, nullable=False),
        sa.Column("status", _STATUS_ENUM, nullable=False),
        sa.Column("given_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("evidence_path", sa.String(length=500), nullable=True),
        sa.Column("recorded_by_user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["patient_id"], ["patient.id"]),
        sa.ForeignKeyConstraint(["recorded_by_user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("consent", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_consent_patient_id"), ["patient_id"], unique=False
        )
        batch_op.create_index(
            "ix_consent_patient_type_status",
            ["patient_id", "consent_type", "status"],
            unique=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("consent", schema=None) as batch_op:
        batch_op.drop_index("ix_consent_patient_type_status")
        batch_op.drop_index(batch_op.f("ix_consent_patient_id"))
    op.drop_table("consent")
