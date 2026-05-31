"""add ecg_study table

Revision ID: c5d8f21b44c0
Revises: 280eb72d9f50
Create Date: 2026-05-31 20:20:05.545516
"""
import sqlalchemy as sa
from alembic import op

revision = "c5d8f21b44c0"
down_revision = "280eb72d9f50"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ecg_study",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("encounter_id", sa.Integer(), nullable=False),
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("study_uid", sa.String(length=64), nullable=False),
        sa.Column("image_original_path", sa.String(length=500), nullable=False),
        sa.Column("image_processed_path", sa.String(length=500), nullable=True),
        sa.Column(
            "image_quality_status",
            sa.Enum(
                "good",
                "acceptable",
                "poor",
                name="ecg_quality_status_enum",
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("image_quality_score", sa.Float(), nullable=False),
        sa.Column("image_quality_metrics_json", sa.JSON(), nullable=False),
        sa.Column("acquired_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recorded_by_user_id", sa.Integer(), nullable=False),
        sa.Column("device_info", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["encounter_id"], ["encounter.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patient.id"]),
        sa.ForeignKeyConstraint(["recorded_by_user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("study_uid"),
    )
    with op.batch_alter_table("ecg_study", schema=None) as batch_op:
        batch_op.create_index(
            "ix_ecg_encounter_created",
            ["encounter_id", "created_at"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_ecg_study_encounter_id"),
            ["encounter_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_ecg_study_patient_id"),
            ["patient_id"],
            unique=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("ecg_study", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_ecg_study_patient_id"))
        batch_op.drop_index(batch_op.f("ix_ecg_study_encounter_id"))
        batch_op.drop_index("ix_ecg_encounter_created")
    op.drop_table("ecg_study")
