from backend.app.core.celery_app import celery_app

from backend.app.database import SessionLocal
from backend.app.models.job import Job
from backend.app.models.company import Company

from backend.app.services.firecrawl import (
    generate_leads,
    get_agent_status
)

from backend.app.services.social_finder import find_social_links


@celery_app.task(
    bind=True,
    name="process_lead_generation_job"
)
def process_lead_generation_job(
    self,
    job_id: int
):

    db = SessionLocal()

    try:

        # 1. Find our job
        job = db.query(Job).filter(
            Job.id == job_id
        ).first()

        if not job:

            print(
                f"Job {job_id} not found"
            )

            return


        # 2. Update job status
        job.status = "processing"

        db.commit()


        print(
            f"Starting lead generation for Job {job_id}"
        )


        # 3. Start Firecrawl
        result = generate_leads(

            country=job.country,

            province=job.province,

            industries=job.industries,

            lead_count=job.lead_count

        )


        # 4. Save Firecrawl job ID
        job.firecrawl_job_id = result.get(
            "id"
        )

        db.commit()


        print(
            f"Firecrawl Job ID: {job.firecrawl_job_id}"
        )


        # 5. Poll Firecrawl
        while True:

            firecrawl_result = get_agent_status(

                job.firecrawl_job_id

            )


            status = firecrawl_result.get(
                "status"
            )


            print(
                f"Firecrawl status: {status}"
            )


            if status == "completed":

                break


            if status == "failed":

                job.status = "failed"

                db.commit()

                return


            import time

            time.sleep(10)


        # 6. Extract companies
        companies = firecrawl_result.get(
            "data",
            {}
        ).get(
            "companies",
            []
        )


        # 7. Save companies
        for company_data in companies:


            # Firecrawl result
            website = company_data.get(
                "website"
            )


            # Python fallback social finder
            social_links = {}

            if website:

                social_links = find_social_links(
                    website
                )


            # Firecrawl first
            # Python fallback if missing
            facebook = (

                company_data.get(
                    "facebook"
                )

                or social_links.get(
                    "facebook"
                )

            )


            instagram = (

                company_data.get(
                    "instagram"
                )

                or social_links.get(
                    "instagram"
                )

            )


            linkedin = (

                company_data.get(
                    "linkedin"
                )

                or social_links.get(
                    "linkedin"
                )

            )


            company = Company(

                job_id=job.id,

                company_name=company_data.get(
                    "company_name"
                ),

                industry=company_data.get(
                    "industry"
                ),

                website=website,

                linkedin=linkedin,

                facebook=facebook,

                instagram=instagram,

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


        # 8. Mark job completed
        job.status = "completed"


        db.commit()


        print(

            f"Job {job_id} completed successfully"

        )


    except Exception as error:


        print(

            f"Job {job_id} failed: {error}"

        )


        job.status = "failed"

        db.commit()


        raise


    finally:

        db.close()