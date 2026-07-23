from backend.app.core.celery_app import celery_app
from backend.app.database import SessionLocal
from backend.app.models.company import Company
from backend.app.services.social_finder import find_social_links


@celery_app.task
def enrich_company_socials(company_id: int):

    db = SessionLocal()

    try:

        company = db.query(Company).filter(
            Company.id == company_id
        ).first()

        if not company:

            return {
                "status": "failed",
                "message": "Company not found"
            }

        company.enrichment_status = "processing"

        db.commit()


        if not company.website:

            company.enrichment_status = "skipped"

            db.commit()

            return {
                "status": "skipped",
                "message": "Company has no website"
            }


        social_links = find_social_links(
            company.website
        )


        if not company.facebook and social_links["facebook"]:

            company.facebook = social_links["facebook"]


        if not company.instagram and social_links["instagram"]:

            company.instagram = social_links["instagram"]


        if not company.linkedin and social_links["linkedin"]:

            company.linkedin = social_links["linkedin"]


        company.enrichment_status = "completed"

        db.commit()


        return {
            "status": "completed",
            "company_id": company.id
        }


    except Exception as error:

        db.rollback()

        company = db.query(Company).filter(
            Company.id == company_id
        ).first()

        if company:

            company.enrichment_status = "failed"

            db.commit()


        return {
            "status": "failed",
            "company_id": company_id,
            "error": str(error)
        }


    finally:

        db.close()