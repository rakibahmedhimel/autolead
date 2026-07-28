import io
import re
from math import ceil

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Header,
    HTTPException,
    Query,
)
from fastapi.responses import StreamingResponse
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.auth.security import get_current_user
from backend.app.config import SYSTEM_FIRECRAWL_FALLBACK_ENABLED
from backend.app.database import get_db
from backend.app.models.company import Company
from backend.app.models.job import Job
from backend.app.models.project import Project
from backend.app.models.user import User
from backend.app.models.user_api_key import UserApiKey
from backend.app.schemas.companies import PaginatedCompanies
from backend.app.schemas.job import JobResponse
from backend.app.schemas.lead_request import LeadRequest
from backend.app.services.api_key_service import decrypt_key
from backend.app.services.enrichment_service import (
    enrich_job_companies_background,
)
from backend.app.services.firecrawl import generate_leads
from backend.app.services.job_refresh_service import refresh_job, safe_error
from backend.app.services.spreadsheet_service import workbook_bytes

router = APIRouter(prefix="/jobs", tags=["Jobs"])

COMPANY_EXPORT_COLUMNS = [
    ("Company Name", "company_name"),
    ("Industry", "industry"),
    ("Website", "website"),
    ("LinkedIn", "linkedin"),
    ("Facebook", "facebook"),
    ("Instagram", "instagram"),
    ("Owner", "owner"),
    ("CEO", "ceo"),
    ("Email", "email"),
    ("Phone", "phone"),
    ("Headquarters", "headquarters"),
    ("Company Size", "company_size"),
    ("Contact Page", "contact_page"),
    ("Services", "services"),
    ("Enrichment Status", "enrichment_status"),
]


def company_export_row(company: Company) -> dict:
    return {
        header: getattr(company, field, None)
        for header, field in COMPANY_EXPORT_COLUMNS
    }


def safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())
    return cleaned.strip("_")[:80] or "results"


@router.post("/generate")
def generate_job(
    data: LeadRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    idempotency_key: str = Header(
        ..., alias="Idempotency-Key", min_length=8, max_length=100
    ),
):
    existing = (
        db.query(Job)
        .filter(Job.user_id == user.id, Job.idempotency_key == idempotency_key)
        .first()
    )
    if existing:
        return {
            "job_id": existing.id,
            "firecrawl_job_id": existing.firecrawl_job_id,
            "status": existing.status,
            "firecrawl_status": existing.firecrawl_status,
            "idempotent_replay": True,
        }
    if (
        not db.query(Project.id)
        .filter(Project.id == data.project_id, Project.user_id == user.id)
        .first()
    ):
        raise HTTPException(status_code=404, detail="Selected project not found")
    key_row = (
        db.query(UserApiKey)
        .filter(UserApiKey.user_id == user.id, UserApiKey.provider == "firecrawl")
        .first()
    )
    api_key = decrypt_key(key_row.encrypted_key) if key_row else None
    if not api_key and not SYSTEM_FIRECRAWL_FALLBACK_ENABLED:
        raise HTTPException(
            status_code=422,
            detail="Add a Firecrawl API key in Settings before creating a job.",
        )

    job = Job(
        project_id=data.project_id,
        user_id=user.id,
        idempotency_key=idempotency_key,
        tool_type="lead_generation",
        country=data.country,
        province=data.province or None,
        industries=data.industries,
        lead_count=data.lead_count,
        status="processing",
        firecrawl_status="pending",
        firecrawl_error=None,
    )
    db.add(job)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = (
            db.query(Job)
            .filter(Job.user_id == user.id, Job.idempotency_key == idempotency_key)
            .one()
        )
        return {
            "job_id": existing.id,
            "firecrawl_job_id": existing.firecrawl_job_id,
            "status": existing.status,
            "firecrawl_status": existing.firecrawl_status,
            "idempotent_replay": True,
        }
    db.refresh(job)
    try:
        result = generate_leads(
            country=data.country,
            province=data.province,
            industries=data.industries,
            lead_count=data.lead_count,
            api_key=api_key,
        )
        agent_id = result.get("id")
        if not agent_id:
            raise RuntimeError("Firecrawl did not return an agent ID")
        job.firecrawl_job_id = agent_id
        job.firecrawl_status = "processing"
        db.commit()
        return {
            "job_id": job.id,
            "firecrawl_job_id": agent_id,
            "status": "processing",
            "firecrawl_status": "processing",
        }
    except Exception as error:
        db.rollback()
        job = db.query(Job).filter(Job.id == job.id).first()
        job.status = job.firecrawl_status = "failed"
        job.firecrawl_error = safe_error(error)
        db.commit()
        raise HTTPException(status_code=502, detail=job.firecrawl_error)


@router.get("/")
def get_jobs(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
):
    total = db.query(Job).filter(Job.user_id == user.id).count()
    rows = (
        db.query(Job, func.count(Company.id).label("company_count"))
        .outerjoin(Company, Company.job_id == Job.id)
        .filter(Job.user_id == user.id)
        .group_by(Job.id)
        .order_by(Job.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    jobs = []
    for job, company_count in rows:
        item = {
            column.name: getattr(job, column.name) for column in Job.__table__.columns
        }
        item["company_count"] = company_count
        jobs.append(item)
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": ceil(total / limit) if total else 0,
        "jobs": jobs,
    }


@router.post("/refresh-pending")
def refresh_pending(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=20),
):
    jobs = (
        db.query(Job)
        .filter(
            Job.user_id == user.id,
            or_(
                Job.status == "processing",
                Job.firecrawl_status.in_(["pending", "processing"]),
            ),
        )
        .order_by(Job.created_at.asc())
        .limit(limit)
        .all()
    )
    results = []
    enrichment_scheduled = 0

    for job in jobs:
        try:
            result = refresh_job(db, job)
            result["enrichment_started"] = False

            if (
                result.get("status") == "completed"
                and result.get("total_companies", 0) > 0
            ):
                unfinished_count = (
                    db.query(Company)
                    .filter(
                        Company.job_id == job.id,
                        Company.enrichment_status.in_(["pending", "failed"]),
                    )
                    .count()
                )

                processing_count = (
                    db.query(Company)
                    .filter(
                        Company.job_id == job.id,
                        Company.enrichment_status == "processing",
                    )
                    .count()
                )

                if unfinished_count > 0 and processing_count == 0:
                    background_tasks.add_task(
                        enrich_job_companies_background,
                        job.id,
                        user.id,
                    )
                    result["enrichment_started"] = True
                    enrichment_scheduled += 1

            results.append(result)

        except Exception as error:
            db.rollback()
            results.append(
                {
                    "job_id": job.id,
                    "status": "failed",
                    "enrichment_started": False,
                    "error": safe_error(error),
                }
            )

    return {
        "checked": len(results),
        "still_processing": sum(
            result.get("status") == "processing" for result in results
        ),
        "completed": sum(result.get("status") == "completed" for result in results),
        "failed": sum(result.get("status") == "failed" for result in results),
        "companies_saved": sum(result.get("companies_saved", 0) for result in results),
        "enrichment_scheduled": enrichment_scheduled,
        "results": results,
    }


@router.get("/{job_id}/download.xlsx")
def download_job_companies(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.user_id == user.id,
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    companies = (
        db.query(Company).filter(Company.job_id == job_id).order_by(Company.id).all()
    )

    headers = [header for header, _ in COMPANY_EXPORT_COLUMNS]

    rows = [company_export_row(company) for company in companies]

    location = "_".join(
        part
        for part in [
            job.country,
            job.province,
        ]
        if part
    )

    filename_location = safe_filename(location or "Results")
    filename = f"AutoLead_Job_{job.id}_{filename_location}.xlsx"

    workbook = workbook_bytes(
        [
            (
                f"Job {job.id}",
                headers,
                rows,
            )
        ]
    )

    return StreamingResponse(
        io.BytesIO(workbook),
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        headers={"Content-Disposition": (f'attachment; filename="{filename}"')},
    )


@router.post("/{job_id}/refresh")
def refresh_single_job(
    job_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.user_id == user.id,
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    result = refresh_job(db, job)

    if result.get("status") == "completed" and result.get("total_companies", 0) > 0:
        unfinished_count = (
            db.query(Company)
            .filter(
                Company.job_id == job_id,
                Company.enrichment_status.in_(["pending", "failed"]),
            )
            .count()
        )

        processing_count = (
            db.query(Company)
            .filter(
                Company.job_id == job_id,
                Company.enrichment_status == "processing",
            )
            .count()
        )

        if unfinished_count > 0 and processing_count == 0:
            background_tasks.add_task(
                enrich_job_companies_background,
                job_id,
                user.id,
            )

            result["enrichment_started"] = True
        else:
            result["enrichment_started"] = False

    return result


@router.get("/{job_id}/firecrawl-status")
def firecrawl_status_read_only(
    job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job.id,
        "status": job.status,
        "firecrawl_status": job.firecrawl_status,
        "error": job.firecrawl_error,
    }


@router.post("/{job_id}/enrich")
def enrich_job(
    job_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    job_exists = (
        db.query(Job.id)
        .filter(
            Job.id == job_id,
            Job.user_id == user.id,
        )
        .first()
    )

    if not job_exists:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    remaining = (
        db.query(Company)
        .filter(
            Company.job_id == job_id,
            Company.enrichment_status.in_(["pending", "failed"]),
        )
        .count()
    )

    processing = (
        db.query(Company)
        .filter(
            Company.job_id == job_id,
            Company.enrichment_status == "processing",
        )
        .count()
    )

    if processing > 0:
        return {
            "job_id": job_id,
            "scheduled": False,
            "remaining": remaining,
            "message": "Enrichment is already running.",
        }

    if remaining == 0:
        return {
            "job_id": job_id,
            "scheduled": False,
            "remaining": 0,
            "message": "No unfinished companies require enrichment.",
        }

    background_tasks.add_task(
        enrich_job_companies_background,
        job_id,
        user.id,
    )

    return {
        "job_id": job_id,
        "scheduled": True,
        "remaining": remaining,
        "message": "Unfinished company enrichment was scheduled.",
    }


@router.get("/{job_id}/enrichment-progress")
def enrichment_progress(
    job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    if not db.query(Job.id).filter(Job.id == job_id, Job.user_id == user.id).first():
        raise HTTPException(status_code=404, detail="Job not found")
    rows = (
        db.query(Company.enrichment_status, func.count(Company.id))
        .filter(Company.job_id == job_id)
        .group_by(Company.enrichment_status)
        .all()
    )
    result = {
        "total": 0,
        "pending": 0,
        "processing": 0,
        "completed": 0,
        "failed": 0,
        "skipped": 0,
    }
    for status, count in rows:
        result[status] = count
        result["total"] += count

    processed = result["completed"] + result["failed"] + result["skipped"]

    result["job_id"] = job_id
    result["finished"] = (
        result["total"] > 0 and result["pending"] == 0 and result["processing"] == 0
    )

    result["progress_percentage"] = (
        round((processed / result["total"]) * 100, 2) if result["total"] else 0
    )

    return result


@router.get("/{job_id}/companies", response_model=PaginatedCompanies)
def get_job_companies(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    if not db.query(Job.id).filter(Job.id == job_id, Job.user_id == user.id).first():
        raise HTTPException(status_code=404, detail="Job not found")
    query = db.query(Company).filter(Company.job_id == job_id)
    total = query.count()
    companies = query.order_by(Company.id).offset((page - 1) * limit).limit(limit).all()
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": ceil(total / limit) if total else 0,
        "companies": companies,
    }


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
