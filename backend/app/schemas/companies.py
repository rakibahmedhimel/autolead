from pydantic import BaseModel


class CompanyResponse(BaseModel):

    id: int

    company_name: str | None

    industry: str | None

    website: str | None

    linkedin: str | None

    facebook: str | None

    instagram: str | None

    owner: str | None

    ceo: str | None

    email: str | None

    phone: str | None

    headquarters: str | None

    company_size: str | None

    contact_page: str | None

    services: str | None

    class Config:
        from_attributes = True


class PaginatedCompanies(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    companies: list[CompanyResponse]