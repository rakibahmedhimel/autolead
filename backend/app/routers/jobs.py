from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import Query
from math import ceil

from backend.app.database import get_db
from backend.app.schemas.lead_request import LeadRequest
from backend.app.services.firecrawl import (
    generate_leads,
    get_agent_status
)
from backend.app.models.job import Job
from backend.app.models.company import Company
from backend.app.schemas.job import JobResponse
from backend.app.tasks.enrichment_tasks import enrich_company_socials
from backend.app.tasks.firecrawl_tasks import (
    process_firecrawl_job
)

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


@router.post("/generate")
def generate_job(
    data: LeadRequest,
    db: Session = Depends(get_db)
):

    # 1. Create Job

    job = Job(

        project_id=data.project_id,

        country=data.country,

        province=data.province,

        industries=data.industries,

        lead_count=data.lead_count,

        status="processing",

        firecrawl_status="pending"

    )

    db.add(job)

    db.commit()

    db.refresh(job)


    # 2. Start Firecrawl

    result = generate_leads(

        country=data.country,

        province=data.province,

        industries=data.industries,

        lead_count=data.lead_count

    )


    # 3. Save Firecrawl job ID

    job.firecrawl_job_id = result.get(
        "id"
    )

    job.firecrawl_status = "processing"

    db.commit()


    # 4. Start background Firecrawl processing

    process_firecrawl_job.delay(
        job.id
    )


    # 5. Return immediately

    return {

        "job_id": job.id,

        "firecrawl_job_id": result.get(
            "id"
        ),

        "status": "processing"

    }

@router.get("/")
def get_jobs(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50)
):

    total = db.query(Job).count()

    jobs = (
        db.query(Job)
        .order_by(Job.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": ceil(total / limit) if total else 0,
        "jobs": jobs
    }

@router.get("/{job_id}/firecrawl-status")
def firecrawl_status(
    job_id: int,
    db: Session = Depends(get_db)
):

    # 1. Find our Job

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()


    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )


    # 2. Check Firecrawl status

    try:

        firecrawl_result = get_agent_status(
            job.firecrawl_job_id
        )

    except Exception as error:

        job.firecrawl_status = "failed"

        job.firecrawl_error = str(error)

        job.status = "failed"

        db.commit()


        return {

            "job_id": job.id,

            "status": "failed",

            "firecrawl_status": "failed",

            "error": str(error)

        }


    # 3. Firecrawl still processing

    if firecrawl_result.get("status") != "completed":

        job.firecrawl_status = "processing"

        db.commit()


        return {

            "job_id": job.id,

            "status": "processing",

            "firecrawl_status": "processing",

            "firecrawl": firecrawl_result

        }


    # 4. Get companies

    companies = firecrawl_result.get(
        "data",
        {}
    ).get(
        "companies",
        []
    )


    # 5. Save companies

    saved_companies = []


    for company_data in companies:


        company = Company(

            job_id=job.id,

            enrichment_status="pending",

            company_name=company_data.get(
                "company_name"
            ),

            industry=company_data.get(
                "industry"
            ),

            website=company_data.get(
                "website"
            ),

            linkedin=company_data.get(
                "linkedin"
            ),

            facebook=company_data.get(
                "facebook"
            ),

            instagram=company_data.get(
                "instagram"
            ),

            owner=company_data.get(
                "owner"
            ),

            ceo=company_data.get(
                "ceo"
            ),

            email=company_data.get(
                "email"
            ),

            phone=company_data.get(
                "phone"
            ),

            headquarters=company_data.get(
                "headquarters"
            ),

            company_size=company_data.get(
                "company_size"
            ),

            contact_page=company_data.get(
                "contact_page"
            ),

            services=company_data.get(
                "services"
            )

        )


        db.add(company)

        saved_companies.append(company)


    # 6. Update Firecrawl status

    job.firecrawl_status = "completed"

    job.firecrawl_error = None

    job.status = "completed"


    db.commit()


    # 7. Start Python enrichment

    for company in saved_companies:

        enrich_company_socials.delay(
            company.id
        )


    return {

        "job_id": job.id,

        "status": "completed",

        "firecrawl_status": "completed",

        "companies_saved": len(
            saved_companies
        ),

        "companies": companies

    }

@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):

    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job