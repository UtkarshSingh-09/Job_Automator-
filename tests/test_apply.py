"""
Test Suite for Auto-Apply Engine (Phase 10).
Validates:
- Profile payload normalization
- ATS provider detection (Greenhouse, Lever)
- Direct API submission dry-run formatting
- Safety guardrails (daily circuit breaker, cooldown rate limiting)
- Safety interceptors (CAPTCHA & Login Wall detection)
- ApplyManager orchestration and persistence
"""
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

from resume_agent.models import ProfileModel, JobModel, CompanyModel, MatchModel
from resume_agent.apply.models import CandidateSubmissionPayload, ApplyResult
from resume_agent.apply.api_submit import (
    detect_api_provider,
    submit_via_greenhouse_api,
    submit_via_lever_api,
    submit_via_api,
)
from resume_agent.apply.browser_submit import (
    check_captcha_present,
    check_login_wall_present,
    _clean_slug,
)
from resume_agent.apply.manager import ApplyManager
from resume_agent.db import get_db


@pytest.fixture
def sample_profile():
    return ProfileModel(
        id=1,
        full_name="Utkarsh Singh",
        email="thakurutkarsh2212@gmail.com",
        phone="+91-7565960168",
        github_url="https://github.com/UtkarshSingh-09",
        linkedin_url="https://linkedin.com/in/utkarshsingh09",
        portfolio_url="https://github.com/UtkarshSingh-09",
        college="SRM University Amaravati",
        degree="B.Tech in Computer Science",
        branch="Computer Science",
        grad_year=2028,
        cgpa=8.78,
        location="Ayodhya, UP, India",
    )


@pytest.fixture
def sample_greenhouse_job():
    return JobModel(
        id=2648,
        company_id=1,
        company_name="Stripe",
        title="Software Engineer, Intern",
        location="Bengaluru, India",
        remote_type="Hybrid",
        description_md="Backend engineering internship.",
        apply_url="https://stripe.com/jobs/search?gh_jid=8031833",
        source="greenhouse",
        source_job_id="8031833",
        content_hash="stripehash1",
    )


@pytest.fixture
def sample_lever_job():
    return JobModel(
        id=9999,
        company_id=2,
        company_name="Palantir",
        title="Software Engineer Intern",
        location="London, UK",
        remote_type="Onsite",
        description_md="Distributed systems internship.",
        apply_url="https://jobs.lever.co/palantir/51d6be3f-08e1-45a7-bd3c-abc123456789",
        source="lever",
        source_job_id="51d6be3f-08e1-45a7-bd3c-abc123456789",
        content_hash="palantirhash1",
    )


def test_candidate_payload_normalization(sample_profile):
    """Payload correctly normalizes first name, last name, phone, and URLs."""
    payload = CandidateSubmissionPayload.from_profile_model(sample_profile)
    assert payload.first_name == "Utkarsh"
    assert payload.last_name == "Singh"
    assert payload.email == "thakurutkarsh2212@gmail.com"
    assert payload.phone == "+91-7565960168"
    assert "UtkarshSingh-09" in payload.github_url
    assert "utkarshsingh09" in payload.linkedin_url


def test_detect_api_provider_greenhouse(sample_greenhouse_job):
    """Greenhouse job detection correctly extracts board slug and job ID."""
    company = CompanyModel(name="Stripe", domain="stripe.com", ats_provider="greenhouse", ats_slug="stripe")
    can_submit, provider, slug, jid = detect_api_provider(sample_greenhouse_job, company)
    assert can_submit is True
    assert provider == "greenhouse"
    assert slug == "stripe"
    assert jid == "8031833"


def test_detect_api_provider_lever(sample_lever_job):
    """Lever job detection correctly parses URL slug and posting ID."""
    can_submit, provider, slug, jid = detect_api_provider(sample_lever_job)
    assert can_submit is True
    assert provider == "lever"
    assert slug == "palantir"
    assert jid == "51d6be3f-08e1-45a7-bd3c-abc123456789"


def test_greenhouse_api_dry_run(sample_profile, tmp_path):
    """Greenhouse API dry-run verifies payload without network call."""
    dummy_pdf = tmp_path / "resume.pdf"
    dummy_pdf.write_bytes(b"%PDF-1.4 dummy")

    payload = CandidateSubmissionPayload.from_profile_model(sample_profile)
    res = submit_via_greenhouse_api(
        board_slug="stripe",
        job_id="8031833",
        candidate=payload,
        resume_pdf_path=dummy_pdf,
        dry_run=True,
    )
    assert res.success is True
    assert res.status == "dry_run"
    assert res.method == "direct_api"
    assert "simulated" in res.response_data


def test_lever_api_dry_run(sample_profile, tmp_path):
    """Lever API dry-run validates payload without making live HTTP requests."""
    dummy_pdf = tmp_path / "resume.pdf"
    dummy_pdf.write_bytes(b"%PDF-1.4 dummy")

    payload = CandidateSubmissionPayload.from_profile_model(sample_profile)
    res = submit_via_lever_api(
        company_slug="palantir",
        posting_id="51d6be3f-08e1-45a7-bd3c-abc123456789",
        candidate=payload,
        resume_pdf_path=dummy_pdf,
        dry_run=True,
    )
    assert res.success is True
    assert res.status == "dry_run"
    assert res.method == "direct_api"


def test_clean_slug_sanitization():
    """Sanitizes strings for file and folder naming."""
    assert _clean_slug("Software Engineer, Intern (2026)") == "Software_Engineer_Intern_2026"
    assert _clean_slug("Coinbase / Risk & Finance") == "Coinbase_Risk_Finance"


def test_daily_limit_circuit_breaker(sample_greenhouse_job):
    """ApplyManager enforces daily quota circuit breaker when limit is reached."""
    mgr = ApplyManager(dry_run=False)

    # Mock get_daily_applied_count to exceed threshold
    with patch.object(mgr, "get_daily_applied_count", return_value=10):
        res = mgr.apply_for_job(sample_greenhouse_job.id, dry_run=False, force=False)
        assert res.success is False
        assert res.status == "daily_limit_reached"
        assert "Daily limit reached" in res.notes


def test_domain_cooldown(sample_greenhouse_job):
    """ApplyManager blocks rapid consecutive applications to the same domain."""
    mgr = ApplyManager(dry_run=False)

    # Mock cooldown check returning 120s remaining
    with patch.object(mgr, "check_domain_cooldown", return_value=120):
        res = mgr.apply_for_job(sample_greenhouse_job.id, dry_run=False, force=False)
        assert res.success is False
        assert res.status == "cooldown_active"
        assert "Cooldown active: 120s remaining" in res.notes


def test_captcha_detection_logic():
    """check_captcha_present detects CAPTCHA locators."""
    mock_page = MagicMock()
    # Mock locator count > 0 for turnstile
    mock_locator = MagicMock()
    mock_locator.count.return_value = 1
    mock_page.locator.return_value = mock_locator

    assert check_captcha_present(mock_page) is True


def test_login_wall_detection_logic():
    """check_login_wall_present detects workday login URLs."""
    mock_page = MagicMock()
    assert check_login_wall_present(mock_page, "https://company.myworkdayjobs.com/en-US/careers/login") is True
