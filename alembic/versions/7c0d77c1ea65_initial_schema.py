"""initial schema

Revision ID: 7c0d77c1ea65
Revises: 
Create Date: 2026-07-19 22:13:26.610630

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c0d77c1ea65'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("province", sa.String(100), nullable=False),
        sa.Column("country", sa.String(100), nullable=False),
        sa.Column("industries", sa.ARRAY(sa.String()), nullable=False),
        sa.Column("lead_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("firecrawl_job_id", sa.String(100), nullable=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False))
    op.create_table("companies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("industry", sa.String(100)), sa.Column("website", sa.String(500)),
        sa.Column("linkedin", sa.String(500)), sa.Column("facebook", sa.String(500)),
        sa.Column("instagram", sa.String(500)), sa.Column("owner", sa.String(255)),
        sa.Column("ceo", sa.String(255)), sa.Column("email", sa.String(255)),
        sa.Column("phone", sa.String(100)), sa.Column("headquarters", sa.String(500)),
        sa.Column("company_size", sa.String(100)), sa.Column("contact_page", sa.String(500)),
        sa.Column("services", sa.Text()), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_projects_id", "projects", ["id"])
    op.create_index("ix_jobs_id", "jobs", ["id"])
    op.create_index("ix_companies_id", "companies", ["id"])
    op.create_index("ix_companies_job_id", "companies", ["job_id"])


def downgrade() -> None:
    op.drop_table("companies")
    op.drop_table("jobs")
    op.drop_table("projects")
