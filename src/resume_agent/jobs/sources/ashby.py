from typing import List, Dict, Any
import httpx
from resume_agent.models import CompanyModel, JobModel
from resume_agent.jobs.sources.base import JobSourceAdapter
from resume_agent.logging import logger


class AshbyAdapter(JobSourceAdapter):
    """Ingests job postings from Ashby public job-board API."""

    BASE_URL = "https://api.ashbyhq.com/posting-api/job-board/{slug}"

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
                logger.warning(f"Ashby fetch returned status {resp.status_code} for '{company.name}'")
                return []
        except Exception as e:
            logger.warning(f"Failed to fetch Ashby jobs for '{company.name}': {e}")
            return []

    def normalize_job(self, raw: Dict[str, Any], company: CompanyModel) -> JobModel:
        title = raw.get("title", "")
        location = raw.get("locationName", "")
        description = raw.get("descriptionHtml") or raw.get("descriptionPlain") or ""
        apply_url = raw.get("jobUrl") or f"https://jobs.ashbyhq.com/{company.ats_slug}/{raw.get('id')}"

        return self.build_job_model(
            company=company,
            title=title,
            location=location,
            description_raw=description,
            apply_url=apply_url,
            source="ashby",
            source_job_id=str(raw.get("id", "")),
        )
