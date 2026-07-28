from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, ARRAY, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("user_id", "idempotency_key", name="uq_job_user_idempotency"),)

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    province: Mapped[str] = mapped_column(
        String(100),
        nullable=True
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    industries: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False
    )

    lead_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    companies = relationship(
        "Company",
        back_populates="job",
        cascade="all, delete-orphan"
    )

    firecrawl_job_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )    

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tool_type: Mapped[str] = mapped_column(String(50), nullable=False, default="lead_generation")

    firecrawl_status = Column(
        String(50),
        default="pending",
        nullable=False
    )

    firecrawl_error = Column(
        Text,
        nullable=True
    )    

    project = relationship(
        "Project",
        back_populates="jobs"
    )
    user = relationship("User", back_populates="jobs")
