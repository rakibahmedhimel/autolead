from celery.exceptions import (
    MaxRetriesExceededError,
    Retry
)

from backend.app.core.celery_app import celery_app
from backend.app.database import SessionLocal

from backend.app.models.job import Job
from backend.app.models.company import Company

from backend.app.services.firecrawl import get_agent_status

from backend.app.tasks.enrichment_tasks import (
    enrich_company_socials
)


@celery_app.task(
    bind=True,
    max_retries=60
)
def process_firecrawl_job(
    self,
    job_id: int
):

    db = SessionLocal()

    try:

        # 1. Find the job

        job = (
            db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

        if not job:

            print(
                f"Job {job_id} not found."
            )

            return {
                "status": "failed",
                "job_id": job_id,
                "error": "Job not found"
            }


        # 2. Get Firecrawl status

        try:

            firecrawl_result = get_agent_status(
                job.firecrawl_job_id
            )

        except Exception as error:

            job.firecrawl_status = "failed"

            job.firecrawl_error = str(error)

            job.status = "failed"

            db.commit()

            print(
                f"Firecrawl failed for job {job_id}: {error}"
            )

            return {

                "status": "failed",

                "job_id": job_id,

                "error": str(error)

            }


        firecrawl_status = firecrawl_result.get(
            "status"
        )


        # 3. Firecrawl is still processing

        if firecrawl_status != "completed":

            print(
                f"Firecrawl job {job_id} still processing..."
            )

            job.firecrawl_status = "processing"

            db.commit()


            # IMPORTANT:
            # This must not be caught by the broad
            # Exception handler below.

            raise self.retry(
                countdown=10
            )


        # 4. Get companies

        companies = (
            firecrawl_result
            .get("data", {})
            .get("companies", [])
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

            saved_companies.append(
                company
            )


        # 6. Update Job status

        job.firecrawl_status = "completed"

        job.firecrawl_error = None

        job.status = "completed"

        db.commit()


        # 7. Start social enrichment

        for company in saved_companies:

            enrich_company_socials.delay(
                company.id
            )


        print(
            f"Firecrawl completed for job {job_id}. "
            f"Saved {len(saved_companies)} companies."
        )


        return {

            "status": "completed",

            "job_id": job_id,

            "companies_saved": len(
                saved_companies
            )

        }


    except MaxRetriesExceededError:

        job.firecrawl_status = "failed"

        job.firecrawl_error = (
            "Firecrawl processing timed out."
        )

        job.status = "failed"

        db.commit()

        return {

            "status": "failed",

            "job_id": job_id,

            "error": "Firecrawl processing timed out."

        }
    
    except Retry:

        raise

    except Exception as error:

        db.rollback()

        print(
            f"Unexpected Firecrawl task error: {error}"
        )

        return {

            "status": "failed",

            "job_id": job_id,

            "error": str(error)

        }


    finally:

        db.close()