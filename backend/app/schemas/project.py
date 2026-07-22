from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime



class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: str | None = None

class CompanyResponse(BaseModel):
    id: int
    company_name: str | None = None
    industry: str | None = None
    website: str | None = None
    linkedin: str | None = None
    facebook: str | None = None
    instagram: str | None = None
    owner: str | None = None
    ceo: str | None = None
    email: str | None = None
    phone: str | None = None
    headquarters: str | None = None
    company_size: str | None = None
    contact_page: str | None = None
    services: str | None = None

    model_config = ConfigDict(from_attributes=True)


class JobResponse(BaseModel):
    id: int
    country: str
    province: str | None = None
    industries: list[str]
    lead_count: int
    status: str
    created_at: datetime
    companies: list[CompanyResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    created_at: datetime
    jobs: list[JobResponse] = []

    model_config = ConfigDict(from_attributes=True)