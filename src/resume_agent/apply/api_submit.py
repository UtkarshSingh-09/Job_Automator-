import re
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import httpx

from resume_agent.models import JobModel, CompanyModel
from resume_agent.apply.models import ApplyResult, CandidateSubmissionPayload
from resume_agent.logging import logger


def detect_api_provider(job: JobModel, company: Optional[CompanyModel] = None) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
    """
    Detect if a job can be submitted directly via ATS API.
    Returns: (can_submit, provider, board_slug, posting_id)
    """
    apply_url = job.apply_url or ""
    source = (job.source or "").lower()

    # 1. Greenhouse Detection
    # Formats:
    # https://boards.greenhouse.io/{board_slug}/jobs/{id}
    # https://boards.greenhouse.io/embed/job_app?for={board_slug}&token={id}
    # https://boards-api.greenhouse.io/v1/boards/{board_slug}/jobs/{id}
    # https://company.com/careers?gh_jid={id}
    if "greenhouse" in source or "greenhouse.io" in apply_url or "gh_jid=" in apply_url:
        board_slug = None
        posting_id = job.source_job_id

        # Check URL patterns
        gh_match = re.search(r"boards\.greenhouse\.io/(?:embed/job_app\?for=)?([^/&\?]+)(?:/jobs/|&token=)?(\d+)?", apply_url)
        if gh_match:
            board_slug = gh_match.group(1)
            if gh_match.group(2):
                posting_id = gh_match.group(2)

        # Fallback to query param gh_jid
        if not posting_id:
            jid_match = re.search(r"gh_jid=(\d+)", apply_url)
            if jid_match:
                posting_id = jid_match.group(1)

        # Fallback board slug from company record
        if not board_slug and company and company.ats_provider == "greenhouse" and company.ats_slug:
            board_slug = company.ats_slug

        if board_slug and posting_id:
            return True, "greenhouse", board_slug, str(posting_id)

    # 2. Lever Detection
    # Formats:
    # https://jobs.lever.co/{company_slug}/{posting_id}
    if "lever" in source or "lever.co" in apply_url:
        lever_match = re.search(r"jobs\.lever\.co/([^/]+)/([a-f0-9\-]+)", apply_url)
        if lever_match:
            board_slug = lever_match.group(1)
            posting_id = lever_match.group(2)
            return True, "lever", board_slug, posting_id
        
        # Fallback from company
        if company and company.ats_provider == "lever" and company.ats_slug and job.source_job_id:
            return True, "lever", company.ats_slug, str(job.source_job_id)

    return False, None, None, None


def submit_via_greenhouse_api(
    board_slug: str,
    job_id: str,
    candidate: CandidateSubmissionPayload,
    resume_pdf_path: Path,
    dry_run: bool = False,
    timeout: float = 30.0
) -> ApplyResult:
    """
    Direct multipart form POST to Greenhouse Boards API.
    Endpoint: POST https://boards-api.greenhouse.io/v1/boards/{board_slug}/jobs/{job_id}
    """
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_slug}/jobs/{job_id}"
    logger.info(f"Greenhouse API Submission target: {url} (Dry Run: {dry_run})")

    if not resume_pdf_path.exists():
        return ApplyResult(
            success=False,
            status="failed",
            method="direct_api",
            error=f"Resume PDF not found: {resume_pdf_path}"
        )

    form_data = {
        "first_name": candidate.first_name,
        "last_name": candidate.last_name,
        "email": candidate.email,
        "phone": candidate.phone,
        "urls[0][value]": candidate.linkedin_url,
        "urls[1][value]": candidate.github_url,
    }

    if dry_run:
        logger.info(f"[DRY-RUN] Greenhouse API submission simulated successfully for {board_slug} Job #{job_id}")
        return ApplyResult(
            success=True,
            status="dry_run",
            method="direct_api",
            notes=f"Simulated Greenhouse API POST to {url}",
            response_data={"simulated": True, "target_url": url, "payload": form_data}
        )

    try:
        with open(resume_pdf_path, "rb") as f:
            pdf_bytes = f.read()

        files = {
            "resume": (resume_pdf_path.name, pdf_bytes, "application/pdf")
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json",
        }

        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, data=form_data, files=files, headers=headers)

        if resp.status_code in (200, 201):
            logger.info(f"Greenhouse application submitted successfully! (HTTP {resp.status_code})")
            return ApplyResult(
                success=True,
                status="submitted",
                method="direct_api",
                notes=f"Greenhouse HTTP {resp.status_code}",
                response_data=resp.json() if "application/json" in resp.headers.get("content-type", "") else {"status": resp.status_code}
            )
        else:
            err_msg = f"Greenhouse API returned HTTP {resp.status_code}: {resp.text[:300]}"
            logger.warning(err_msg)
            return ApplyResult(
                success=False,
                status="failed",
                method="direct_api",
                error=err_msg,
                response_data={"status_code": resp.status_code, "body": resp.text[:500]}
            )

    except Exception as e:
        logger.error(f"Exception during Greenhouse API submission: {e}")
        return ApplyResult(
            success=False,
            status="failed",
            method="direct_api",
            error=str(e)
        )


def submit_via_lever_api(
    company_slug: str,
    posting_id: str,
    candidate: CandidateSubmissionPayload,
    resume_pdf_path: Path,
    dry_run: bool = False,
    timeout: float = 30.0
) -> ApplyResult:
    """
    Direct multipart form POST to Lever Postings API.
    Endpoint: POST https://api.lever.co/v0/postings/{company_slug}/{posting_id}/apply
    """
    url = f"https://api.lever.co/v0/postings/{company_slug}/{posting_id}/apply"
    logger.info(f"Lever API Submission target: {url} (Dry Run: {dry_run})")

    if not resume_pdf_path.exists():
        return ApplyResult(
            success=False,
            status="failed",
            method="direct_api",
            error=f"Resume PDF not found: {resume_pdf_path}"
        )

    form_data = {
        "name": candidate.full_name,
        "email": candidate.email,
        "phone": candidate.phone,
        "urls[LinkedIn]": candidate.linkedin_url,
        "urls[GitHub]": candidate.github_url,
    }

    if dry_run:
        logger.info(f"[DRY-RUN] Lever API submission simulated successfully for {company_slug} Job #{posting_id}")
        return ApplyResult(
            success=True,
            status="dry_run",
            method="direct_api",
            notes=f"Simulated Lever API POST to {url}",
            response_data={"simulated": True, "target_url": url, "payload": form_data}
        )

    try:
        with open(resume_pdf_path, "rb") as f:
            pdf_bytes = f.read()

        files = {
            "resume": (resume_pdf_path.name, pdf_bytes, "application/pdf")
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json",
        }

        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, data=form_data, files=files, headers=headers)

        if resp.status_code in (200, 201):
            logger.info(f"Lever application submitted successfully! (HTTP {resp.status_code})")
            return ApplyResult(
                success=True,
                status="submitted",
                method="direct_api",
                notes=f"Lever HTTP {resp.status_code}",
                response_data=resp.json() if "application/json" in resp.headers.get("content-type", "") else {"status": resp.status_code}
            )
        else:
            err_msg = f"Lever API returned HTTP {resp.status_code}: {resp.text[:300]}"
            logger.warning(err_msg)
            return ApplyResult(
                success=False,
                status="failed",
                method="direct_api",
                error=err_msg,
                response_data={"status_code": resp.status_code, "body": resp.text[:500]}
            )

    except Exception as e:
        logger.error(f"Exception during Lever API submission: {e}")
        return ApplyResult(
            success=False,
            status="failed",
            method="direct_api",
            error=str(e)
        )


def submit_via_api(
    job: JobModel,
    candidate: CandidateSubmissionPayload,
    resume_pdf_path: Path,
    company: Optional[CompanyModel] = None,
    dry_run: bool = False
) -> ApplyResult:
    """
    Tier 1 Dispatcher: Routes to appropriate Direct ATS API.
    """
    can_submit, provider, slug, posting_id = detect_api_provider(job, company)
    if not can_submit or not slug or not posting_id:
        return ApplyResult(
            success=False,
            status="unsupported_provider",
            method="direct_api",
            error=f"No Direct API endpoint detected for job {job.id} ({job.apply_url})"
        )

    if provider == "greenhouse":
        return submit_via_greenhouse_api(slug, posting_id, candidate, resume_pdf_path, dry_run=dry_run)
    elif provider == "lever":
        return submit_via_lever_api(slug, posting_id, candidate, resume_pdf_path, dry_run=dry_run)
    else:
        return ApplyResult(
            success=False,
            status="unsupported_provider",
            method="direct_api",
            error=f"Unsupported API provider: {provider}"
        )
