from typing import List, Dict, Any
import httpx
from resume_agent.models import CompanyModel, JobModel
from resume_agent.jobs.sources.base import JobSourceAdapter
from resume_agent.logging import logger


class GreenhouseAdapter(JobSourceAdapter):
    """Ingests job postings from Greenhouse public job board API."""

    BASE_URL = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"

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
                    return data.get("jobs", [])
                logger.warning(f"Greenhouse fetch returned status {resp.status_code} for '{company.name}'")
                return []
        except Exception as e:
            logger.warning(f"Failed to fetch Greenhouse jobs for '{company.name}': {e}")
            return []

    def normalize_job(self, raw: Dict[str, Any], company: CompanyModel) -> JobModel:
        title = raw.get("title", "")
        loc_obj = raw.get("location") or {}
        location = loc_obj.get("name", "") if isinstance(loc_obj, dict) else str(loc_obj)
        content_html = raw.get("content", "")
        apply_url = raw.get("absolute_url", f"https://boards.greenhouse.io/{company.ats_slug}/jobs/{raw.get('id')}")

        return self.build_job_model(
            company=company,
            title=title,
            location=location,
            description_raw=content_html,
            apply_url=apply_url,
            source="greenhouse",
            source_job_id=str(raw.get("id", "")),
        )
