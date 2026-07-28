from urllib.parse import urlsplit

from sqlalchemy.orm import Session

from backend.app.models.company import Company
from backend.app.models.job import Job
from backend.app.models.user_api_key import UserApiKey
from backend.app.config import SYSTEM_FIRECRAWL_FALLBACK_ENABLED
from backend.app.services.api_key_service import decrypt_key
from backend.app.services.firecrawl import get_agent_status


FAILURE_STATUSES = {"failed", "cancelled", "canceled", "expired", "error"}


def safe_error(error) -> str:
    message = str(error) or "Firecrawl request failed"
    return message[:1000]


def _company_key(company: dict) -> tuple[str, str]:
    website = (
        (company.get("website") or company.get("official_website") or "")
        .strip()
        .lower()
    )
    if website:
        parsed = urlsplit(website if "://" in website else f"https://{website}")
        host = (parsed.hostname or website).removeprefix("www.")
        return ("website", host.rstrip("/"))
    return ("name", (company.get("company_name") or "").strip().casefold())


def _companies_from_result(result: dict) -> list[dict]:
    data = result.get("data") or {}
    if isinstance(data, list):
        return data
    return data.get("companies") or result.get("companies") or []


def refresh_job(db: Session, job: Job) -> dict:
    # Serialize refreshes for this job so two clicks cannot insert the same result.
    job = db.query(Job).filter(Job.id == job.id).with_for_update().one()
    existing_count = db.query(Company).filter(Company.job_id == job.id).count()
    if job.status == "completed" and existing_count:
        return {
            "job_id": job.id,
            "status": job.status,
            "firecrawl_status": job.firecrawl_status,
            "companies_saved": 0,
            "total_companies": existing_count,
        }

    if not job.firecrawl_job_id:
        job.status = job.firecrawl_status = "failed"
        job.firecrawl_error = "This job has no Firecrawl agent ID."
        db.commit()
        return {
            "job_id": job.id,
            "status": "failed",
            "firecrawl_status": "failed",
            "companies_saved": 0,
            "total_companies": existing_count,
            "error": job.firecrawl_error,
        }

    try:
        key_row = (
            db.query(UserApiKey)
            .filter(
                UserApiKey.user_id == job.user_id, UserApiKey.provider == "firecrawl"
            )
            .first()
        )
        api_key = decrypt_key(key_row.encrypted_key) if key_row else None
        if not api_key and not SYSTEM_FIRECRAWL_FALLBACK_ENABLED:
            raise RuntimeError("No Firecrawl API key is configured for this account")
        result = get_agent_status(job.firecrawl_job_id, api_key=api_key)
        status = str(result.get("status") or "processing").lower()
        if status in {"pending", "processing", "running", "queued"}:
            job.status = job.firecrawl_status = "processing"
            job.firecrawl_error = None
            db.commit()
            return {
                "job_id": job.id,
                "status": "processing",
                "firecrawl_status": "processing",
                "companies_saved": 0,
                "total_companies": existing_count,
            }

        if status != "completed":
            message = (
                result.get("error")
                or result.get("message")
                or f"Firecrawl ended with status: {status}"
            )
            job.status = job.firecrawl_status = "failed"
            job.firecrawl_error = safe_error(message)
            db.commit()
            return {
                "job_id": job.id,
                "status": "failed",
                "firecrawl_status": "failed",
                "companies_saved": 0,
                "total_companies": existing_count,
                "error": job.firecrawl_error,
            }

        existing = db.query(Company).filter(Company.job_id == job.id).all()
        keys = {
            _company_key({"website": item.website, "company_name": item.company_name})
            for item in existing
        }
        saved = 0
        fields = (
            "company_name",
            "industry",
            "linkedin",
            "facebook",
            "instagram",
            "owner",
            "ceo",
            "email",
            "phone",
            "headquarters",
            "company_size",
            "contact_page",
            "services",
        )
        for item in _companies_from_result(result):
            key = _company_key(item)
            if not key[1] or key in keys:
                continue
            values = {field: item.get(field) for field in fields}
            values["website"] = item.get("website") or item.get("official_website")
            if not values["company_name"]:
                continue
            db.add(Company(job_id=job.id, enrichment_status="pending", **values))
            keys.add(key)
            saved += 1

        job.status = job.firecrawl_status = "completed"
        job.firecrawl_error = None
        db.commit()
        total = db.query(Company).filter(Company.job_id == job.id).count()
        return {
            "job_id": job.id,
            "status": "completed",
            "firecrawl_status": "completed",
            "companies_saved": saved,
            "total_companies": total,
        }
    except Exception as error:
        db.rollback()
        job = db.query(Job).filter(Job.id == job.id).first()
        job.status = job.firecrawl_status = "failed"
        job.firecrawl_error = safe_error(error)
        db.commit()
        return {
            "job_id": job.id,
            "status": "failed",
            "firecrawl_status": "failed",
            "companies_saved": 0,
            "total_companies": existing_count,
            "error": job.firecrawl_error,
        }
