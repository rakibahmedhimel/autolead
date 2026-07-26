"""make job province optional

Revision ID: 4a82d953b671
Revises: 1d574e9dd4f3
Create Date: 2026-07-26
"""

from alembic import op
import sqlalchemy as sa


revision = "4a82d953b671"
down_revision = "1d574e9dd4f3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "jobs", "province",
        existing_type=sa.String(length=100),
        nullable=True,
    )


def downgrade() -> None:
    op.execute("UPDATE jobs SET province = '' WHERE province IS NULL")
    op.alter_column(
        "jobs", "province",
        existing_type=sa.String(length=100),
        nullable=False,
    )
