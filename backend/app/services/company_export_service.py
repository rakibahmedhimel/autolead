import re

from backend.app.models.company import Company

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


def company_export_headers() -> list[str]:
    return [header for header, _ in COMPANY_EXPORT_COLUMNS]


def company_export_row(company: Company) -> dict:
    return {
        header: getattr(company, field, None)
        for header, field in COMPANY_EXPORT_COLUMNS
    }


def safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())
    return cleaned.strip("_")[:80] or "results"
