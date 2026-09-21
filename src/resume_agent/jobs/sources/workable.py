from typing import List, Dict, Any
import httpx
from resume_agent.models import CompanyModel, JobModel
from resume_agent.jobs.sources.base import JobSourceAdapter
from resume_agent.logging import logger


class WorkableAdapter(JobSourceAdapter):
    """Ingests job postings from Workable public accounts API."""

    BASE_URL = "https://apply.workable.com/api/v1/accounts/{slug}"

    def fetch_jobs(self, company: CompanyModel) -> List[Dict[str, Any]]:
        if not company.ats_slug:
            return []

        url = self.BASE_URL.format(slug=company.ats_slug)
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json",
        }

        try:
            with httpx.Client(headers=headers, timeout=15.0, follow_redirects=True) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("results", [])
                logger.warning(f"Workable fetch returned status {resp.status_code} for '{company.name}'")
                return []
        except Exception as e:
            logger.warning(f"Failed to fetch Workable jobs for '{company.name}': {e}")
            return []

    def normalize_job(self, raw: Dict[str, Any], company: CompanyModel) -> JobModel:
        title = raw.get("title", "")
        city = raw.get("city", "")
        country = raw.get("country", "")
        location = f"{city}, {country}".strip(", ")
        description = raw.get("description", "") or title
        shortcode = raw.get("shortcode", "")
        apply_url = raw.get("url") or f"https://apply.workable.com/{company.ats_slug}/j/{shortcode}/"

        return self.build_job_model(
            company=company,
            title=title,
            location=location,
            description_raw=description,
            apply_url=apply_url,
            source="workable",
            source_job_id=str(shortcode or raw.get("id", "")),
        )
