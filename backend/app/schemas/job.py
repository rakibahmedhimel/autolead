from datetime import datetime
from pydantic import BaseModel

from backend.app.schemas.companies import CompanyResponse


class JobResponse(BaseModel):

    id: int

    country: str

    province: str | None

    industries: list[str]

    lead_count: int

    status: str

    firecrawl_status: str

    firecrawl_error: str | None

    created_at: datetime

    companies: list[CompanyResponse] = []

    class Config:
        from_attributes = True