from datetime import datetime

from sqlalchemy import DateTime, Integer, String, ForeignKey, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    province: Mapped[str] = mapped_column(
        String(100),
        nullable=False
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

    project = relationship(
        "Project",
        back_populates="jobs"
    )    