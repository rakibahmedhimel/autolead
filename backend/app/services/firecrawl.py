import os
import requests
from dotenv import load_dotenv

load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

BASE_URL = "https://api.firecrawl.dev/v2"


def _headers(api_key: str | None = None):
    key = api_key or FIRECRAWL_API_KEY
    if not key:
        raise RuntimeError("FIRECRAWL_API_KEY is not configured")
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def generate_leads(country: str, province: str | None, industries: list[str], lead_count: int, api_key: str | None = None):

    industry_text = ", ".join(industries)

    location = country

    if province:
        location = f"{province}, {country}"    

    prompt = f"""
        You are a B2B lead generation researcher.

        Find up to {lead_count} qualified businesses in {location}
        operating across these industries:

        {industry_text}

        Search across all the target industries listed above and select businesses from those industries.

        Prioritize established small and mid-sized businesses that could realistically need custom software, AI automation, CRM, ERP, booking systems, websites, mobile apps, customer support automation, or other digital transformation services.

        IMPORTANT:

        - Focus only on real, currently operating businesses physically located in {location}.
        - Every company must belong to at least one of the requested target industries.
        - Do not return software development companies, IT consulting companies, digital marketing agencies, or technology service companies unless they primarily operate as a business in one of the requested target industries.
        - Prioritize potential B2B clients rather than large multinational corporations whenever possible.
        - Use the company's official website and publicly available LinkedIn, Facebook, and Instagram pages when available.
        - Extract ONLY publicly available information.
        - Do not guess, infer, or fabricate information.
        - If a field cannot be verified, return null.
        - Avoid duplicate companies.
        - Ensure every company is actually located in {location}.
        - Classify each company using the most appropriate industry from the requested target industries.
        - Continue researching until the requested number of qualified businesses is reached or no more relevant businesses can be reliably found.

        Return the following fields:

        - company_name
        - industry
        - official_website
        - linkedin
        - facebook
        - instagram
        - owner
        - ceo
        - email
        - phone
        - headquarters
        - company_size
        - contact_page
        - services

        Return ONLY valid JSON matching the provided schema.
    """

    schema = {
        "type": "object",
        "properties": {
            "companies": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "company_name": {"type": "string"},
                        "industry": {"type": "string"},
                        "website": {"type": "string"},
                        "linkedin": {"type": "string"},
                        "facebook": {"type": "string"},
                        "instagram": {"type": "string"},
                        "owner": {"type": "string"},
                        "ceo": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"},
                        "headquarters": {"type": "string"},
                        "company_size": {"type": "string"},
                        "contact_page": {"type": "string"},
                        "services": {"type": "string"}
                    }
                }
            }
        }
    }

    response = requests.post(
        f"{BASE_URL}/agent",
        headers=_headers(api_key),
        json={
            "prompt": prompt,
            "schema": schema
        },
        timeout=60
    )

    response.raise_for_status()

    return response.json()



def get_agent_status(job_id: str, api_key: str | None = None):

    response = requests.get(
        f"{BASE_URL}/agent/{job_id}",
        headers=_headers(api_key),
        timeout=60
    )

    response.raise_for_status()

    return response.json()
