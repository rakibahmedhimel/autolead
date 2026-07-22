from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.lead_request import LeadRequest
from backend.app.services.firecrawl import (
    generate_leads,
    get_agent_status
)
from backend.app.models.job import Job
from backend.app.models.company import Company
from backend.app.schemas.job import JobResponse
from backend.app.services.social_finder import find_social_links


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


@router.post("/generate")
def generate_job(
    data: LeadRequest,
    db: Session = Depends(get_db)
):

    # 1. Create our Job
    job = Job(
        project_id=data.project_id,
        country=data.country,
        province=data.province,
        industries=data.industries,
        lead_count=data.lead_count,
        status="processing"
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

    # Save Firecrawl ID
    job.firecrawl_job_id = result.get("id")

    db.commit()

    return {
        "job_id": job.id,
        "firecrawl_job_id": result.get("id"),
        "status": "processing"
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
        return {
            "error": "Job not found"
        }

    # 2. Check Firecrawl
    firecrawl_result = get_agent_status(
        job.firecrawl_job_id
    )

    # 3. If still processing
    if firecrawl_result.get("status") != "completed":

        return firecrawl_result

    # 4. Get companies from Firecrawl
    companies = firecrawl_result.get(
        "data",
        {}
    ).get(
        "companies",
        []
    )

    # 5. Save every company
    saved_companies = []

    for company_data in companies:

        # --------------------------------
        # Python Enrichment
        # --------------------------------

        website = company_data.get("website")

        if website:

            social_links = find_social_links(
                website
            )

            # Only fill missing fields
            if not company_data.get("facebook"):

                company_data["facebook"] = (
                    social_links.get("facebook")
                )

            if not company_data.get("instagram"):

                company_data["instagram"] = (
                    social_links.get("instagram")
                )

            if not company_data.get("linkedin"):

                company_data["linkedin"] = (
                    social_links.get("linkedin")
                )

        # --------------------------------
        # Save Company
        # --------------------------------

        company = Company(

            job_id=job.id,

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

        saved_companies.append(
            company
        )

    # 6. Update Job status
    job.status = "completed"

    db.commit()

    return {
        "job_id": job.id,
        "status": "completed",
        "companies_saved": len(saved_companies),
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