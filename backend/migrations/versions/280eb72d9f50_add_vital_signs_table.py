"""add vital_signs table

Revision ID: 280eb72d9f50
Revises: a83d89370a74
Create Date: 2026-05-31 18:37:13.597440
"""
import sqlalchemy as sa
from alembic import op

revision = "280eb72d9f50"
down_revision = "a83d89370a74"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vital_signs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("encounter_id", sa.Integer(), nullable=False),
        sa.Column("measured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("bp_systolic", sa.Integer(), nullable=True),
        sa.Column("bp_diastolic", sa.Integer(), nullable=True),
        sa.Column("heart_rate", sa.Integer(), nullable=True),
        sa.Column("respiratory_rate", sa.Integer(), nullable=True),
        sa.Column("spo2", sa.Integer(), nullable=True),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("height", sa.Float(), nullable=True),
        sa.Column("recorded_by_user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["encounter_id"], ["encounter.id"]),
        sa.ForeignKeyConstraint(["recorded_by_user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("vital_signs", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_vital_signs_encounter_id"),
            ["encounter_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_vital_signs_measured_at"),
            ["measured_at"],
            unique=False,
        )
        batch_op.create_index(
            "ix_vitals_encounter_measured",
            ["encounter_id", "measured_at"],
            unique=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("vital_signs", schema=None) as batch_op:
        batch_op.drop_index("ix_vitals_encounter_measured")
        batch_op.drop_index(batch_op.f("ix_vital_signs_measured_at"))
        batch_op.drop_index(batch_op.f("ix_vital_signs_encounter_id"))
    op.drop_table("vital_signs")
