"""
Test Suite for Telegram Delivery & Automation Pipeline (Phase 9).
Validates:
- TelegramClient dry-run message, document, and alert formatting
- Daily pipeline orchestration loop in dry-run mode
- n8n visual workflow JSON schema and topology
"""
import json
import pytest
from pathlib import Path
from resume_agent.models import JobModel, MatchModel
from resume_agent.deliver.telegram import TelegramClient
from resume_agent.orchestrate.daily import run_daily_pipeline


@pytest.fixture
def sample_job():
    return JobModel(
        id=2648,
        company_id=1,
        company_name="Stripe",
        title="Software Engineer, Intern",
        location="Bengaluru, India",
        remote_type="Hybrid",
        description_md="Software engineering internship building financial infrastructure.",
        apply_url="https://stripe.com/jobs/2648",
        source="greenhouse",
        content_hash="stripehash123",
    )


@pytest.fixture
def sample_match():
    return MatchModel(
        id=1,
        job_id=2648,
        overall_fit=85.0,
        selected_projects=[
            {"repo_name": "trinetra", "relevance": "Financial document pipeline and credit risk scoring"},
            {"repo_name": "merchantmind", "relevance": "2PC transaction saga and checkout engine"},
            {"repo_name": "aegis-forge", "relevance": "Real-time low-latency multi-agent platform"},
        ],
        selection_reasoning="Strong alignment with financial systems, APIs, and low-latency infrastructure.",
    )


def test_telegram_client_dry_run_send_message():
    """TelegramClient in dry-run mode records simulated message without throwing errors."""
    client = TelegramClient(dry_run=True)
    res = client.send_message("<b>Test Notification</b>\nPipeline operational.")
    assert res is True


def test_telegram_client_dry_run_send_document(tmp_path):
    """TelegramClient in dry-run mode simulates document upload."""
    sample_pdf = tmp_path / "test.pdf"
    sample_pdf.write_bytes(b"%PDF-1.4 simulated pdf bytes")

    client = TelegramClient(dry_run=True)
    res = client.send_document(
        document_path=sample_pdf,
        caption="<b>Test ATS Resume</b>",
        reply_markup={"inline_keyboard": [[{"text": "Apply", "url": "https://stripe.com"}]]}
    )
    assert res is True


def test_telegram_client_send_match_alert(sample_job, sample_match, tmp_path):
    """TelegramClient formats rich match card with inline buttons and attaches PDF."""
    sample_pdf = tmp_path / "resume.pdf"
    sample_pdf.write_bytes(b"%PDF-1.4 test")

    client = TelegramClient(dry_run=True)
    res = client.send_match_alert(sample_job, sample_match, sample_pdf)
    assert res is True


def test_telegram_client_send_daily_digest():
    """TelegramClient formats 09:00 IST executive morning briefing."""
    client = TelegramClient(dry_run=True)
    stats = {
        "date": "2026-09-22",
        "boards_monitored": 41,
        "jobs_ingested": 12,
        "matches_found": 3,
        "resumes_generated": 3,
        "resumes_validated": 3,
        "applied_count": 0,
        "matches": [
            {"company": "Stripe", "title": "Software Engineer Intern", "score": 85.0},
            {"company": "Coinbase", "title": "Backend Intern", "score": 82.0},
        ]
    }
    res = client.send_daily_digest(stats)
    assert res is True


def test_telegram_client_send_error_alert():
    """TelegramClient formats error alerts cleanly."""
    client = TelegramClient(dry_run=True)
    res = client.send_error_alert("Database connection timeout during job fetch", stage="Job Ingestion")
    assert res is True


def test_n8n_workflow_json_structure():
    """Validates n8n workflow definition JSON schema, trigger node, and CLI execution node."""
    workflow_path = Path("n8n/workflows/daily_pipeline.json")
    assert workflow_path.exists(), "n8n/workflows/daily_pipeline.json must exist"

    with open(workflow_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "nodes" in data
    assert "connections" in data
    node_names = [n["name"] for n in data["nodes"]]
    assert "Schedule Trigger (09:00 PM IST Night Digest)" in node_names
    assert "Execute Daily Pipeline CLI" in node_names
    assert "Matches Found?" in node_names
    assert "Telegram: Matches Digest" in node_names


def test_daily_pipeline_dry_run():
    """Validates end-to-end execution of daily pipeline in dry-run mode."""
    stats = run_daily_pipeline(dry_run=True, skip_fetch=True, limit=1, send_telegram=True)
    assert isinstance(stats, dict)
    assert stats["success"] is True
    assert stats["boards_monitored"] > 0
    assert "matches" in stats


def test_telegram_client_send_apply_confirmation_with_tap_to_copy(sample_job, tmp_path):
    """Validates Telegram alert packaging for manual/OTP intervention with tap-to-copy Q&A blocks."""
    client = TelegramClient(dry_run=True)
    sample_pdf = tmp_path / "resume.pdf"
    sample_pdf.write_bytes(b"%PDF-1.4 test")
    sample_img = tmp_path / "captcha.png"
    sample_img.write_bytes(b"PNG mock")

    answers = {
        "Why do you want to work at Stripe?": "Strong alignment with financial infrastructure.",
        "Expected Graduation": "May 2028"
    }

    res = client.send_apply_confirmation(
        job=sample_job,
        status="manual_required",
        method="browser_automation",
        pdf_path=sample_pdf,
        screenshot_path=sample_img,
        notes="Bot Protection: OTP verification required.",
        ai_answers=answers
    )
    assert res is True
