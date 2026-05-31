"""add encounter table

Revision ID: 5289e386341e
Revises: 1f53d75c3d1c
Create Date: 2026-05-31 18:21:04.544437
"""
import sqlalchemy as sa
from alembic import op

revision = "5289e386341e"
down_revision = "1f53d75c3d1c"
branch_labels = None
depends_on = None

_TYPE_ENUM = sa.Enum(
    "rawat_jalan", "igd", name="encounter_type_enum", create_constraint=True
)
_STATUS_ENUM = sa.Enum(
    "open", "closed", name="encounter_status_enum", create_constraint=True
)


def upgrade() -> None:
    op.create_table(
        "encounter",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("facility_id", sa.Integer(), nullable=False),
        sa.Column("attending_user_id", sa.Integer(), nullable=False),
        sa.Column("encounter_type", _TYPE_ENUM, nullable=False),
        sa.Column("status", _STATUS_ENUM, nullable=False),
        sa.Column("chief_complaint", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["attending_user_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["facility_id"], ["healthcare_facility.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patient.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("encounter", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_encounter_attending_user_id"),
            ["attending_user_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_encounter_facility_id"), ["facility_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_encounter_patient_id"), ["patient_id"], unique=False
        )
        batch_op.create_index(
            "ix_encounter_patient_status",
            ["patient_id", "status"],
            unique=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("encounter", schema=None) as batch_op:
        batch_op.drop_index("ix_encounter_patient_status")
        batch_op.drop_index(batch_op.f("ix_encounter_patient_id"))
        batch_op.drop_index(batch_op.f("ix_encounter_facility_id"))
        batch_op.drop_index(batch_op.f("ix_encounter_attending_user_id"))
    op.drop_table("encounter")
