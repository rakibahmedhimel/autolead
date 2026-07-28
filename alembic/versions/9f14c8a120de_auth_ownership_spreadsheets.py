"""auth ownership idempotency and spreadsheet foundation

Revision ID: 9f14c8a120de
Revises: 4a82d953b671
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "9f14c8a120de"
down_revision = "4a82d953b671"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("users",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(320), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_admin", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("last_activity_at", sa.DateTime()), sa.UniqueConstraint("email", name="uq_users_email"))
    # Legacy rows remain accessible after the owner registers this reserved account through a manual password reset.
    op.execute("""INSERT INTO users (name,email,password_hash,is_admin,is_active)
                  VALUES ('Legacy Owner','legacy-owner@autolead.local','!unusable!',false,true)""")
    op.add_column("projects", sa.Column("user_id", sa.Integer(), nullable=True))
    op.add_column("projects", sa.Column("normalized_name", sa.String(150), nullable=True))
    op.create_foreign_key("fk_projects_user", "projects", "users", ["user_id"], ["id"])
    op.execute("UPDATE projects SET user_id=(SELECT id FROM users WHERE email='legacy-owner@autolead.local')")
    op.execute("UPDATE projects SET normalized_name=lower(regexp_replace(trim(name), '\\s+', ' ', 'g'))")
    op.execute("""
      DO $$
      DECLARE duplicate_projects integer; reassigned_jobs integer;
      BEGIN
        SELECT count(*) INTO duplicate_projects FROM (
          SELECT id, row_number() OVER (PARTITION BY user_id, normalized_name ORDER BY created_at,id) position
          FROM projects
        ) ranked WHERE position > 1;
        SELECT count(*) INTO reassigned_jobs FROM jobs WHERE project_id IN (
          SELECT id FROM (
            SELECT id, row_number() OVER (PARTITION BY user_id, normalized_name ORDER BY created_at,id) position
            FROM projects
          ) ranked WHERE position > 1
        );
        RAISE NOTICE 'AutoLead repair: % duplicate project(s) will be merged; % job(s) will be reassigned; jobs and companies will not be deleted.',
          duplicate_projects, reassigned_jobs;
      END $$;
    """)
    # Oldest project wins; all jobs are moved before duplicate containers are removed.
    op.execute("""
      WITH ranked AS (
        SELECT id, first_value(id) OVER (PARTITION BY user_id, normalized_name ORDER BY created_at,id) canonical
        FROM projects
      )
      UPDATE jobs SET project_id=ranked.canonical FROM ranked
      WHERE jobs.project_id=ranked.id AND ranked.id<>ranked.canonical
    """)
    op.execute("""
      DELETE FROM projects p USING projects canonical
      WHERE p.user_id=canonical.user_id AND p.normalized_name=canonical.normalized_name
        AND (p.created_at,p.id)>(canonical.created_at,canonical.id)
    """)
    op.alter_column("projects", "user_id", nullable=False)
    op.alter_column("projects", "normalized_name", nullable=False)
    op.create_index("ix_projects_user_id", "projects", ["user_id"])
    op.create_unique_constraint("uq_project_user_normalized_name", "projects", ["user_id", "normalized_name"])
    op.add_column("jobs", sa.Column("user_id", sa.Integer(), nullable=True))
    op.add_column("jobs", sa.Column("idempotency_key", sa.String(100)))
    op.add_column("jobs", sa.Column("tool_type", sa.String(50), server_default="lead_generation", nullable=False))
    op.execute("UPDATE jobs SET user_id=projects.user_id FROM projects WHERE jobs.project_id=projects.id")
    op.alter_column("jobs", "user_id", nullable=False)
    op.create_foreign_key("fk_jobs_user", "jobs", "users", ["user_id"], ["id"])
    op.create_index("ix_jobs_user_id", "jobs", ["user_id"])
    op.create_unique_constraint("uq_job_user_idempotency", "jobs", ["user_id", "idempotency_key"])
    op.create_table("user_api_keys", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False), sa.Column("encrypted_key", sa.String(2000), nullable=False),
        sa.Column("key_suffix", sa.String(8), nullable=False), sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id","provider",name="uq_user_api_key_provider"))
    op.create_table("contact_submissions", sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="SET NULL")),
        sa.Column("name",sa.String(150),nullable=False),sa.Column("email",sa.String(320),nullable=False),
        sa.Column("subject",sa.String(200),nullable=False),sa.Column("message",sa.Text(),nullable=False),
        sa.Column("created_at",sa.DateTime(),server_default=sa.func.now(),nullable=False))
    op.create_table("tool_requests", sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),
        sa.Column("tool_name",sa.String(150),nullable=False),sa.Column("business_problem",sa.Text(),nullable=False),
        sa.Column("desired_input",sa.Text(),nullable=False),sa.Column("desired_output",sa.Text(),nullable=False),
        sa.Column("additional_details",sa.Text()),sa.Column("contact_preference",sa.String(100)),
        sa.Column("status",sa.String(30),server_default="new",nullable=False),
        sa.Column("created_at",sa.DateTime(),server_default=sa.func.now(),nullable=False))
    op.create_table("spreadsheet_jobs", sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),
        sa.Column("project_id",sa.Integer(),sa.ForeignKey("projects.id",ondelete="CASCADE"),nullable=False),
        sa.Column("idempotency_key",sa.String(100),nullable=False),sa.Column("original_filename",sa.String(255),nullable=False),
        sa.Column("source_type",sa.String(30),nullable=False),sa.Column("status",sa.String(30),server_default="mapping",nullable=False),
        sa.Column("mapping",postgresql.JSONB()),sa.Column("total_rows",sa.Integer(),server_default="0",nullable=False),
        sa.Column("processed_rows",sa.Integer(),server_default="0",nullable=False),
        sa.Column("failed_rows",sa.Integer(),server_default="0",nullable=False),
        sa.Column("credits_used",sa.Integer(),server_default="0",nullable=False),
        sa.Column("created_at",sa.DateTime(),server_default=sa.func.now(),nullable=False),
        sa.UniqueConstraint("user_id","idempotency_key",name="uq_spreadsheet_user_idempotency"))
    op.create_table("spreadsheet_sheets",sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("job_id",sa.Integer(),sa.ForeignKey("spreadsheet_jobs.id",ondelete="CASCADE"),nullable=False),
        sa.Column("name",sa.String(255),nullable=False),sa.Column("position",sa.Integer(),nullable=False),
        sa.Column("headers",postgresql.JSONB(),nullable=False))
    op.create_table("spreadsheet_rows",sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("sheet_id",sa.Integer(),sa.ForeignKey("spreadsheet_sheets.id",ondelete="CASCADE"),nullable=False),
        sa.Column("row_number",sa.Integer(),nullable=False),sa.Column("values",postgresql.JSONB(),nullable=False),
        sa.Column("status",sa.String(30),server_default="pending",nullable=False),sa.Column("error",sa.Text()),
        sa.UniqueConstraint("sheet_id","row_number",name="uq_spreadsheet_sheet_row"))
    op.create_table("credit_ledger",sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),
        sa.Column("spreadsheet_job_id",sa.Integer(),sa.ForeignKey("spreadsheet_jobs.id",ondelete="CASCADE"),nullable=False),
        sa.Column("row_id",sa.Integer(),sa.ForeignKey("spreadsheet_rows.id",ondelete="CASCADE"),nullable=False),
        sa.Column("field_name",sa.String(80),nullable=False),sa.Column("source_url",sa.String(1000)),
        sa.Column("created_at",sa.DateTime(),server_default=sa.func.now(),nullable=False),
        sa.UniqueConstraint("row_id","field_name",name="uq_credit_row_field"))


def downgrade():
    for table in ("credit_ledger","spreadsheet_rows","spreadsheet_sheets","spreadsheet_jobs",
                  "tool_requests","contact_submissions","user_api_keys"):
        op.drop_table(table)
    op.drop_constraint("uq_job_user_idempotency","jobs",type_="unique")
    op.drop_constraint("fk_jobs_user","jobs",type_="foreignkey")
    for column in ("tool_type","idempotency_key","user_id"): op.drop_column("jobs",column)
    op.drop_constraint("uq_project_user_normalized_name","projects",type_="unique")
    op.drop_constraint("fk_projects_user","projects",type_="foreignkey")
    op.drop_column("projects","normalized_name"); op.drop_column("projects","user_id")
    op.drop_table("users")
