from abc import ABC, abstractmethod
from typing import List, Dict, Any
from resume_agent.models import CompanyModel, JobModel
from resume_agent.jobs.pipeline.normalize import html_to_markdown, detect_remote_type
from resume_agent.jobs.pipeline.dedupe import generate_content_hash
from resume_agent.jobs.pipeline.filter import evaluate_job_filter


class JobSourceAdapter(ABC):
    """Abstract interface for Applicant Tracking System (ATS) data ingestion adapters."""

    @abstractmethod
    def fetch_jobs(self, company: CompanyModel) -> List[Dict[str, Any]]:
        """Fetch raw listings from the ATS API."""
        pass

    @abstractmethod
    def normalize_job(self, raw: Dict[str, Any], company: CompanyModel) -> JobModel:
        """Normalize raw ATS JSON item into strongly typed JobModel."""
        pass

    def build_job_model(
        self,
        company: CompanyModel,
        title: str,
        location: str,
        description_raw: str,
        apply_url: str,
        source: str,
        source_job_id: str,
    ) -> JobModel:
        """Helper to assemble normalized JobModel with markdown description, dedup hash, and filter eval."""
        description_md = html_to_markdown(description_raw)
        remote_type = detect_remote_type(title, location, description_md)
        content_hash = generate_content_hash(company.name, title, location)
        passed, _ = evaluate_job_filter(title, location, description_md)

        return JobModel(
            company_id=company.id,
            company_name=company.name,
            title=title.strip(),
            location=location.strip(),
            remote_type=remote_type,
            description_md=description_md,
            apply_url=apply_url.strip(),
            source=source,
            source_job_id=str(source_job_id),
            content_hash=content_hash,
            passed_filter=passed,
        )
