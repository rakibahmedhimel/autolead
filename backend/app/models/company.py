from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    company_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    industry: Mapped[str] = mapped_column(
        String(100),
        nullable=True
    )

    website: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    linkedin: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    facebook: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    instagram: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    owner: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    ceo: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    phone: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    headquarters: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    company_size: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    contact_page: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    services: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    job = relationship(
        "Job",
        back_populates="companies"
    )