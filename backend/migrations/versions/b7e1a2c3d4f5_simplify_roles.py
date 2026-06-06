"""simplify roles: clinician/nurse→clinical, expert_reviewer→researcher

Revision ID: b7e1a2c3d4f5
Revises: f92350c47afa
Create Date: 2026-06-06
"""
from alembic import op

revision = 'b7e1a2c3d4f5'
down_revision = 'f92350c47afa'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE user SET role = 'clinical' WHERE role IN ('clinician', 'nurse')")
    op.execute("UPDATE user SET role = 'researcher' WHERE role = 'expert_reviewer'")


def downgrade():
    pass
