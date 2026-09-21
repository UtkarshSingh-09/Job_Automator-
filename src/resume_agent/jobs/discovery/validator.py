from typing import Optional
import httpx
from resume_agent.logging import logger

VALIDATION_URLS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
    "lever": "https://api.lever.co/v0/postings/{slug}?mode=json",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{slug}",
    "workable": "https://apply.workable.com/api/v1/accounts/{slug}",
    "recruitee": "https://{slug}.recruitee.com/api/offers/",
    "smartrecruiters": "https://api.smartrecruiters.com/v1/companies/{slug}/postings",
}


def validate_ats_slug(provider: str, slug: str, timeout: float = 10.0) -> bool:
    """
    Ping the discovered public ATS API endpoint to verify the slug exists and returns active listings.
    """
    provider_lower = provider.lower()
    template = VALIDATION_URLS.get(provider_lower)
    if not template:
        logger.warning(f"No validation endpoint configured for provider: {provider}")
        return True  # Assume valid if unknown provider

    target_url = template.format(slug=slug)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    try:
        with httpx.Client(headers=headers, timeout=timeout, follow_redirects=True) as client:
            resp = client.get(target_url)
            if resp.status_code == 200:
                logger.info(f"Verified {provider} endpoint for '{slug}': HTTP 200 OK")
                return True
            else:
                logger.warning(f"Endpoint verification returned status {resp.status_code} for {provider} slug '{slug}'")
                return False
    except Exception as e:
        logger.warning(f"Network error verifying {provider} slug '{slug}': {e}")
        return False
