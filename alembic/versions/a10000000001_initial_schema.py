"""Create the complete AutoLead schema for an empty database.

Revision ID: a10000000001
Revises:
Create Date: 2026-07-28
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "a10000000001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_admin", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("last_activity_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    op.create_table(
        "contact_submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("subject", sa.String(200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("normalized_name", sa.String(150), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "normalized_name", name="uq_project_user_normalized_name"),
    )
    op.create_index("ix_projects_id", "projects", ["id"])
    op.create_index("ix_projects_user_id", "projects", ["user_id"])

    op.create_table(
        "tool_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("tool_name", sa.String(150), nullable=False),
        sa.Column("business_problem", sa.Text(), nullable=False),
        sa.Column("desired_input", sa.Text(), nullable=False),
        sa.Column("desired_output", sa.Text(), nullable=False),
        sa.Column("additional_details", sa.Text(), nullable=True),
        sa.Column("contact_preference", sa.String(100), nullable=True),
        sa.Column("status", sa.String(30), server_default="new", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "user_api_keys",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(50), server_default="firecrawl", nullable=False),
        sa.Column("encrypted_key", sa.String(2000), nullable=False),
        sa.Column("key_suffix", sa.String(8), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "provider", name="uq_user_api_key_provider"),
    )
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("province", sa.String(100), nullable=True),
        sa.Column("country", sa.String(100), nullable=False),
        sa.Column("industries", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("lead_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(50), server_default="pending", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("firecrawl_job_id", sa.String(100), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("idempotency_key", sa.String(100), nullable=True),
        sa.Column("tool_type", sa.String(50), server_default="lead_generation", nullable=False),
        sa.Column("firecrawl_status", sa.String(50), server_default="pending", nullable=False),
        sa.Column("firecrawl_error", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "idempotency_key", name="uq_job_user_idempotency"),
    )
    op.create_index("ix_jobs_id", "jobs", ["id"])
    op.create_index("ix_jobs_user_id", "jobs", ["user_id"])

    op.create_table(
        "spreadsheet_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("idempotency_key", sa.String(100), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("source_type", sa.String(30), nullable=False),
        sa.Column("status", sa.String(30), server_default="mapping", nullable=False),
        sa.Column("mapping", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("total_rows", sa.Integer(), server_default="0", nullable=False),
        sa.Column("processed_rows", sa.Integer(), server_default="0", nullable=False),
        sa.Column("failed_rows", sa.Integer(), server_default="0", nullable=False),
        sa.Column("credits_used", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "idempotency_key", name="uq_spreadsheet_user_idempotency"),
    )
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("website", sa.String(500), nullable=True),
        sa.Column("linkedin", sa.String(500), nullable=True),
        sa.Column("facebook", sa.String(500), nullable=True),
        sa.Column("instagram", sa.String(500), nullable=True),
        sa.Column("owner", sa.String(255), nullable=True),
        sa.Column("ceo", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(100), nullable=True),
        sa.Column("headquarters", sa.String(500), nullable=True),
        sa.Column("company_size", sa.String(100), nullable=True),
        sa.Column("contact_page", sa.String(500), nullable=True),
        sa.Column("services", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("enrichment_status", sa.String(50), server_default="pending", nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_companies_id", "companies", ["id"])
    op.create_index("ix_companies_job_id", "companies", ["job_id"])
    op.create_index(
        "uq_company_job_website",
        "companies",
        ["job_id", sa.text("lower(website)")],
        unique=True,
        postgresql_where=sa.text("website IS NOT NULL"),
    )
    op.create_index(
        "uq_company_job_name_without_website",
        "companies",
        ["job_id", sa.text("lower(company_name)")],
        unique=True,
        postgresql_where=sa.text("website IS NULL"),
    )

    op.create_table(
        "spreadsheet_sheets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("headers", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["spreadsheet_jobs.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "spreadsheet_rows",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sheet_id", sa.Integer(), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("values", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(30), server_default="pending", nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["sheet_id"], ["spreadsheet_sheets.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("sheet_id", "row_number", name="uq_spreadsheet_sheet_row"),
    )
    op.create_table(
        "credit_ledger",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("spreadsheet_job_id", sa.Integer(), nullable=False),
        sa.Column("row_id", sa.Integer(), nullable=False),
        sa.Column("field_name", sa.String(80), nullable=False),
        sa.Column("source_url", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["row_id"], ["spreadsheet_rows.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["spreadsheet_job_id"], ["spreadsheet_jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("row_id", "field_name", name="uq_credit_row_field"),
    )

def downgrade() -> None:
    op.drop_table("credit_ledger")
    op.drop_table("spreadsheet_rows")
    op.drop_table("spreadsheet_sheets")
    op.drop_table("companies")
    op.drop_table("spreadsheet_jobs")
    op.drop_table("jobs")
    op.drop_table("user_api_keys")
    op.drop_table("tool_requests")
    op.drop_table("projects")
    op.drop_table("contact_submissions")
    op.drop_table("users")
