from typing import List, Dict, Any
import httpx
from resume_agent.models import CompanyModel, JobModel
from resume_agent.jobs.sources.base import JobSourceAdapter
from resume_agent.logging import logger


class LeverAdapter(JobSourceAdapter):
    """Ingests job postings from Lever public postings API."""

    BASE_URL = "https://api.lever.co/v0/postings/{slug}?mode=json"

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
                    return data if isinstance(data, list) else []
                logger.warning(f"Lever fetch returned status {resp.status_code} for '{company.name}'")
                return []
        except Exception as e:
            logger.warning(f"Failed to fetch Lever jobs for '{company.name}': {e}")
            return []

    def normalize_job(self, raw: Dict[str, Any], company: CompanyModel) -> JobModel:
        title = raw.get("text", "")
        cats = raw.get("categories") or {}
        location = cats.get("location", "") if isinstance(cats, dict) else ""
        description = raw.get("description", "")
        apply_url = raw.get("hostedUrl") or raw.get("applyUrl") or f"https://jobs.lever.co/{company.ats_slug}/{raw.get('id')}"

        return self.build_job_model(
            company=company,
            title=title,
            location=location,
            description_raw=description,
            apply_url=apply_url,
            source="lever",
            source_job_id=str(raw.get("id", "")),
        )
