"""add model_metadata table

Revision ID: d11cd0272676
Revises: c5d8f21b44c0
Create Date: 2026-06-01 00:03:38.794404
"""
import sqlalchemy as sa
from alembic import op

revision = "d11cd0272676"
down_revision = "c5d8f21b44c0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "model_metadata",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("model_version", sa.String(length=50), nullable=False),
        sa.Column("architecture", sa.String(length=50), nullable=False),
        sa.Column(
            "task_type",
            sa.Enum(
                "classification",
                name="model_task_type_enum",
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("input_size", sa.Integer(), nullable=False),
        sa.Column("model_file_path", sa.String(length=500), nullable=False),
        sa.Column("model_checksum", sa.String(length=64), nullable=False),
        sa.Column("model_size_mb", sa.Float(), nullable=False),
        sa.Column("class_names_json", sa.JSON(), nullable=False),
        sa.Column("threshold_config_json", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("training_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "model_name", "model_version", name="uq_model_name_version"
        ),
    )
    with op.batch_alter_table("model_metadata", schema=None) as batch_op:
        batch_op.create_index("ix_model_active", ["is_active"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("model_metadata", schema=None) as batch_op:
        batch_op.drop_index("ix_model_active")
    op.drop_table("model_metadata")
