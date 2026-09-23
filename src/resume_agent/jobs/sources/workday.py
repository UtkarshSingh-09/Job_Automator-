from typing import List, Dict, Any
import httpx
from resume_agent.models import CompanyModel, JobModel
from resume_agent.jobs.sources.base import JobSourceAdapter
from resume_agent.logging import logger


class WorkdayAdapter(JobSourceAdapter):
    """Ingests job postings from Workday CXS public API."""

    def fetch_jobs(self, company: CompanyModel) -> List[Dict[str, Any]]:
        if not company.ats_slug:
            return []

        parts = company.ats_slug.split("/")
        tenant = parts[0]
        portal = parts[1] if len(parts) > 1 else "careers"

        candidate_urls = [
            f"https://{tenant}.wd1.myworkdayjobs.com/wday/cxs/{tenant}/{portal}/jobs",
            f"https://{tenant}.wd3.myworkdayjobs.com/wday/cxs/{tenant}/{portal}/jobs",
            f"https://{tenant}.wd5.myworkdayjobs.com/wday/cxs/{tenant}/{portal}/jobs",
        ]

        payload = {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": ""}
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        for url in candidate_urls:
            try:
                with httpx.Client(headers=headers, timeout=15.0, follow_redirects=True) as client:
                    resp = client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data.get("jobPostings", [])
            except Exception:
                continue

        logger.warning(f"Workday fetch failed for '{company.name}' across candidate endpoints.")
        return []

    def normalize_job(self, raw: Dict[str, Any], company: CompanyModel) -> JobModel:
        title = raw.get("title", "")
        location = raw.get("locationsText", "") or ""
        external_path = raw.get("externalPath", "")
        bullet_fields = raw.get("bulletFields", [])
        description = " ".join(bullet_fields) if bullet_fields else title

        parts = (company.ats_slug or "").split("/")
        tenant = parts[0] if parts else company.name.lower()
        apply_url = f"https://{tenant}.wd1.myworkdayjobs.com/careers{external_path}" if external_path else f"https://{tenant}.wd1.myworkdayjobs.com/careers"

        return self.build_job_model(
            company=company,
            title=title,
            location=location,
            description_raw=description,
            apply_url=apply_url,
            source="workday",
            source_job_id=str(external_path or raw.get("id", "")),
        )
