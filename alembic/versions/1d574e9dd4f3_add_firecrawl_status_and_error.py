"""add firecrawl status and error

Revision ID: 1d574e9dd4f3
Revises: b2683928a560
Create Date: 2026-07-22 19:14:11.083212

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d574e9dd4f3'
down_revision: Union[str, Sequence[str], None] = 'b2683928a560'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        "jobs",
        sa.Column(
            "firecrawl_status",
            sa.String(length=50),
            nullable=False,
            server_default="pending"
        )
    )

    op.add_column(
        "jobs",
        sa.Column(
            "firecrawl_error",
            sa.Text(),
            nullable=True
        )
    )


def downgrade() -> None:

    op.drop_column(
        "jobs",
        "firecrawl_error"
    )

    op.drop_column(
        "jobs",
        "firecrawl_status"
    )