import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


SOCIAL_PLATFORMS = {
    "facebook": "facebook.com",
    "instagram": "instagram.com",
    "linkedin": "linkedin.com",
}


def find_social_links(website: str) -> dict:

    result = {
        "facebook": None,
        "instagram": None,
        "linkedin": None,
    }

    if not website:
        return result

    try:

        response = requests.get(
            website,
            timeout=15,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "Chrome/120 Safari/537.36"
                )
            }
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        links = soup.find_all("a", href=True)

        for link in links:

            href = link["href"].strip()

            href = urljoin(
                website,
                href
            )

            href_lower = href.lower()

            if (
                "facebook.com" in href_lower
                and not result["facebook"]
            ):
                result["facebook"] = href

            elif (
                "instagram.com" in href_lower
                and not result["instagram"]
            ):
                result["instagram"] = href

            elif (
                "linkedin.com" in href_lower
                and not result["linkedin"]
            ):
                result["linkedin"] = href

        return result

    except requests.RequestException as error:

        print(
            f"Social link extraction failed: {error}"
        )

        return result