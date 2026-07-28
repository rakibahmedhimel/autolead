from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base


class SpreadsheetJob(Base):
    __tablename__ = "spreadsheet_jobs"
    __table_args__ = (UniqueConstraint("user_id", "idempotency_key", name="uq_spreadsheet_user_idempotency"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(100), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="mapping", nullable=False)
    mapping: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    total_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processed_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    credits_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    sheets = relationship("SpreadsheetSheet", cascade="all, delete-orphan", back_populates="job")


class SpreadsheetSheet(Base):
    __tablename__ = "spreadsheet_sheets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("spreadsheet_jobs.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    headers: Mapped[list] = mapped_column(JSONB, nullable=False)
    job = relationship("SpreadsheetJob", back_populates="sheets")
    rows = relationship("SpreadsheetRow", cascade="all, delete-orphan", back_populates="sheet")


class SpreadsheetRow(Base):
    __tablename__ = "spreadsheet_rows"
    __table_args__ = (UniqueConstraint("sheet_id", "row_number", name="uq_spreadsheet_sheet_row"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sheet_id: Mapped[int] = mapped_column(ForeignKey("spreadsheet_sheets.id", ondelete="CASCADE"), nullable=False)
    row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    values: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    sheet = relationship("SpreadsheetSheet", back_populates="rows")


class CreditLedger(Base):
    __tablename__ = "credit_ledger"
    __table_args__ = (UniqueConstraint("row_id", "field_name", name="uq_credit_row_field"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    spreadsheet_job_id: Mapped[int] = mapped_column(ForeignKey("spreadsheet_jobs.id", ondelete="CASCADE"), nullable=False)
    row_id: Mapped[int] = mapped_column(ForeignKey("spreadsheet_rows.id", ondelete="CASCADE"), nullable=False)
    field_name: Mapped[str] = mapped_column(String(80), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
