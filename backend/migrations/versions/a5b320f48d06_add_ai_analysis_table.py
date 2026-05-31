"""add ai_analysis table

Revision ID: a5b320f48d06
Revises: d11cd0272676
Create Date: 2026-06-01 00:15:52.392599
"""
import sqlalchemy as sa
from alembic import op

revision = "a5b320f48d06"
down_revision = "d11cd0272676"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_analysis",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ecg_study_id", sa.Integer(), nullable=False),
        sa.Column("model_metadata_id", sa.Integer(), nullable=False),
        sa.Column(
            "predicted_class",
            sa.Enum(
                "normal",
                "mi",
                "homi",
                "abnormal",
                name="analysis_predicted_class_enum",
                create_constraint=True,
            ),
            nullable=True,
        ),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("probability_json", sa.JSON(), nullable=False),
        sa.Column("inference_time_ms", sa.Integer(), nullable=True),
        sa.Column(
            "device_used",
            sa.Enum(
                "cpu",
                "gpu",
                name="analysis_device_enum",
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column(
            "inference_started_at", sa.DateTime(timezone=True), nullable=True
        ),
        sa.Column(
            "inference_finished_at", sa.DateTime(timezone=True), nullable=True
        ),
        sa.Column(
            "status",
            sa.Enum(
                "success",
                "failed",
                "skipped",
                name="analysis_status_enum",
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["ecg_study_id"], ["ecg_study.id"]),
        sa.ForeignKeyConstraint(
            ["model_metadata_id"], ["model_metadata.id"]
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "ecg_study_id",
            "model_metadata_id",
            name="uq_analysis_study_model",
        ),
    )
    with op.batch_alter_table("ai_analysis", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_ai_analysis_ecg_study_id"),
            ["ecg_study_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_ai_analysis_model_metadata_id"),
            ["model_metadata_id"],
            unique=False,
        )
        batch_op.create_index("ix_analysis_status", ["status"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("ai_analysis", schema=None) as batch_op:
        batch_op.drop_index("ix_analysis_status")
        batch_op.drop_index(batch_op.f("ix_ai_analysis_model_metadata_id"))
        batch_op.drop_index(batch_op.f("ix_ai_analysis_ecg_study_id"))
    op.drop_table("ai_analysis")
