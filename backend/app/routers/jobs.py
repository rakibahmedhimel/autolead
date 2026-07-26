from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.company import Company
from backend.app.models.job import Job
from backend.app.models.project import Project
from backend.app.schemas.companies import PaginatedCompanies
from backend.app.schemas.job import JobResponse
from backend.app.schemas.lead_request import LeadRequest
from backend.app.services.firecrawl import generate_leads
from backend.app.services.job_refresh_service import refresh_job, safe_error
from backend.app.services.social_finder import find_social_links

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/generate")
def generate_job(data: LeadRequest, db: Session = Depends(get_db)):
    if not db.query(Project.id).filter(Project.id == data.project_id).first():
        raise HTTPException(status_code=404, detail="Selected project not found")

    job = Job(
        project_id=data.project_id, country=data.country,
        province=data.province or None, industries=data.industries,
        lead_count=data.lead_count, status="processing",
        firecrawl_status="pending", firecrawl_error=None,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    try:
        result = generate_leads(
            country=data.country, province=data.province,
            industries=data.industries, lead_count=data.lead_count,
        )
        agent_id = result.get("id")
        if not agent_id:
            raise RuntimeError("Firecrawl did not return an agent ID")
        job.firecrawl_job_id = agent_id
        job.firecrawl_status = "processing"
        db.commit()
        return {
            "job_id": job.id, "firecrawl_job_id": agent_id,
            "status": "processing", "firecrawl_status": "processing",
        }
    except Exception as error:
        db.rollback()
        job = db.query(Job).filter(Job.id == job.id).first()
        job.status = job.firecrawl_status = "failed"
        job.firecrawl_error = safe_error(error)
        db.commit()
        raise HTTPException(status_code=502, detail=job.firecrawl_error)


@router.get("/")
def get_jobs(db: Session = Depends(get_db), page: int = Query(1, ge=1),
             limit: int = Query(10, ge=1, le=50)):
    total = db.query(Job).count()
    rows = (
        db.query(Job, func.count(Company.id).label("company_count"))
        .outerjoin(Company, Company.job_id == Job.id)
        .group_by(Job.id).order_by(Job.created_at.desc())
        .offset((page - 1) * limit).limit(limit).all()
    )
    jobs = []
    for job, company_count in rows:
        item = {column.name: getattr(job, column.name) for column in Job.__table__.columns}
        item["company_count"] = company_count
        jobs.append(item)
    return {
        "page": page, "limit": limit, "total": total,
        "total_pages": ceil(total / limit) if total else 0, "jobs": jobs,
    }


@router.post("/refresh-pending")
def refresh_pending(db: Session = Depends(get_db), limit: int = Query(20, ge=1, le=50)):
    jobs = (
        db.query(Job).filter(or_(
            Job.status == "processing",
            Job.firecrawl_status.in_(["pending", "processing"]),
        )).order_by(Job.created_at.asc()).limit(limit).all()
    )
    results = []
    for job in jobs:
        try:
            results.append(refresh_job(db, job))
        except Exception as error:
            db.rollback()
            results.append({"job_id": job.id, "status": "failed", "error": safe_error(error)})
    return {
        "checked": len(results),
        "still_processing": sum(r.get("status") == "processing" for r in results),
        "completed": sum(r.get("status") == "completed" for r in results),
        "failed": sum(r.get("status") == "failed" for r in results),
        "companies_saved": sum(r.get("companies_saved", 0) for r in results),
        "results": results,
    }


@router.post("/{job_id}/refresh")
def refresh_single_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return refresh_job(db, job)


@router.get("/{job_id}/firecrawl-status")
def firecrawl_status_read_only(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job.id, "status": job.status,
        "firecrawl_status": job.firecrawl_status, "error": job.firecrawl_error,
    }


@router.post("/{job_id}/enrich")
def enrich_job(job_id: int, db: Session = Depends(get_db),
               limit: int = Query(5, ge=1, le=20)):
    if not db.query(Job.id).filter(Job.id == job_id).first():
        raise HTTPException(status_code=404, detail="Job not found")
    candidates = (
        db.query(Company).filter(
            Company.job_id == job_id,
            or_(Company.facebook.is_(None), Company.instagram.is_(None), Company.linkedin.is_(None)),
            Company.enrichment_status.in_(["pending", "failed"]),
        ).order_by(Company.id).limit(limit).all()
    )
    counts = {"completed": 0, "failed": 0, "skipped": 0}
    for company in candidates:
        if not company.website:
            company.enrichment_status = "skipped"
            counts["skipped"] += 1
            db.commit()
            continue
        try:
            company.enrichment_status = "processing"
            db.commit()
            links = find_social_links(company.website)
            for field in ("facebook", "instagram", "linkedin"):
                if not getattr(company, field) and links.get(field):
                    setattr(company, field, links[field])
            company.enrichment_status = "completed"
            counts["completed"] += 1
            db.commit()
        except Exception:
            db.rollback()
            company = db.query(Company).filter(Company.id == company.id).first()
            company.enrichment_status = "failed"
            counts["failed"] += 1
            db.commit()
    remaining = db.query(Company).filter(
        Company.job_id == job_id,
        or_(Company.facebook.is_(None), Company.instagram.is_(None), Company.linkedin.is_(None)),
        Company.enrichment_status.in_(["pending", "failed"]),
    ).count()
    return {"job_id": job_id, "processed": len(candidates), **counts, "remaining": remaining}


@router.get("/{job_id}/enrichment-progress")
def enrichment_progress(job_id: int, db: Session = Depends(get_db)):
    if not db.query(Job.id).filter(Job.id == job_id).first():
        raise HTTPException(status_code=404, detail="Job not found")
    rows = db.query(Company.enrichment_status, func.count(Company.id)).filter(
        Company.job_id == job_id
    ).group_by(Company.enrichment_status).all()
    result = {"total": 0, "pending": 0, "processing": 0, "completed": 0, "failed": 0, "skipped": 0}
    for status, count in rows:
        result[status] = count
        result["total"] += count
    return result


@router.get("/{job_id}/companies", response_model=PaginatedCompanies)
def get_job_companies(job_id: int, db: Session = Depends(get_db),
                      page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    if not db.query(Job.id).filter(Job.id == job_id).first():
        raise HTTPException(status_code=404, detail="Job not found")
    query = db.query(Company).filter(Company.job_id == job_id)
    total = query.count()
    companies = query.order_by(Company.id).offset((page - 1) * limit).limit(limit).all()
    return {
        "page": page, "limit": limit, "total": total,
        "total_pages": ceil(total / limit) if total else 0, "companies": companies,
    }


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
