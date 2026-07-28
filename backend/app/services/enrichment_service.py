from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.app.database import SessionLocal
from backend.app.models.company import Company
from backend.app.models.job import Job
from backend.app.services.social_finder import find_social_links


def enrich_job_companies(
    db: Session,
    job_id: int,
    user_id: int,
    limit: int | None = None,
) -> dict:
    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.user_id == user_id,
        )
        .first()
    )

    if not job:
        return {
            "job_id": job_id,
            "processed": 0,
            "completed": 0,
            "failed": 0,
            "skipped": 0,
            "remaining": 0,
        }

    query = (
        db.query(Company)
        .filter(
            Company.job_id == job_id,
            Company.enrichment_status.in_(["pending", "failed"]),
            or_(
                Company.facebook.is_(None),
                Company.instagram.is_(None),
                Company.linkedin.is_(None),
            ),
        )
        .order_by(Company.id)
    )

    if limit is not None:
        query = query.limit(limit)

    companies = query.all()

    counts = {
        "completed": 0,
        "failed": 0,
        "skipped": 0,
    }

    for company in companies:
        if not company.website:
            company.enrichment_status = "skipped"
            db.commit()

            counts["skipped"] += 1
            continue

        try:
            company.enrichment_status = "processing"
            db.commit()

            links = find_social_links(company.website)

            for field in ("facebook", "instagram", "linkedin"):
                existing_value = getattr(company, field)
                discovered_value = links.get(field)

                if not existing_value and discovered_value:
                    setattr(company, field, discovered_value)

            company.enrichment_status = "completed"
            db.commit()

            counts["completed"] += 1

        except Exception:
            db.rollback()

            company = db.query(Company).filter(Company.id == company.id).first()

            if company:
                company.enrichment_status = "failed"
                db.commit()

            counts["failed"] += 1

    remaining = (
        db.query(Company)
        .filter(
            Company.job_id == job_id,
            Company.enrichment_status.in_(["pending", "failed"]),
            or_(
                Company.facebook.is_(None),
                Company.instagram.is_(None),
                Company.linkedin.is_(None),
            ),
        )
        .count()
    )

    return {
        "job_id": job_id,
        "processed": len(companies),
        **counts,
        "remaining": remaining,
    }


def enrich_job_companies_background(
    job_id: int,
    user_id: int,
) -> None:
    db = SessionLocal()

    try:
        enrich_job_companies(
            db=db,
            job_id=job_id,
            user_id=user_id,
            limit=None,
        )
    finally:
        db.close()
