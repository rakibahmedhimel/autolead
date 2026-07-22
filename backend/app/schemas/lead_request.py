from pydantic import BaseModel, Field


class LeadRequest(BaseModel):

    project_id: int = Field(
        ...,
        example=1
    )

    country: str = Field(
        ...,
        example="Canada"
    )

    province: str | None = Field(
        default=None,
        example="British Columbia"
    )

    industries: list[str] = Field(
        ...,
        min_length=1,
        example=[
            "Construction",
            "Retail",
            "Real Estate"
        ]
    )

    lead_count: int = Field(
        ...,
        ge=1,
        le=100,
        example=20
    )