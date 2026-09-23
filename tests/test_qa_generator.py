import pytest
from unittest.mock import patch, MagicMock
from resume_agent.models import JobModel
from resume_agent.apply.qa_generator import QAGenerator


@pytest.fixture
def sample_job():
    return JobModel(
        id=611,
        company_id=1,
        company_name="Figma",
        title="Software Engineer Intern (Winter 2027)",
        location="San Francisco, CA (onsite)",
        remote_type="Onsite",
        description_md="Building real-time collaborative canvas infrastructure.",
        apply_url="https://boards.greenhouse.io/figma/jobs/6131089004",
        source="greenhouse",
        source_job_id="6131089004",
        content_hash="figmahash123",
    )


def test_deterministic_work_authorization_us(sample_job):
    qa = QAGenerator()
    res = qa.resolve_question(
        "Are you authorized to work in the country for which you applied?",
        field_type="select",
        job=sample_job,
        options=["Yes", "No"]
    )
    assert res["answer"] == "No"
    assert res["is_ai_generated"] is False
    assert res["category"] == "work_authorization_eligibility"


def test_deterministic_visa_sponsorship(sample_job):
    qa = QAGenerator()
    res = qa.resolve_question(
        "Will you now or in the future require visa sponsorship for employment?",
        field_type="select",
        job=sample_job,
        options=["Yes", "No"]
    )
    assert res["answer"] == "Yes"
    assert res["is_ai_generated"] is False
    assert res["category"] == "work_authorization_sponsorship"


def test_deterministic_graduation_date(sample_job):
    qa = QAGenerator()
    res = qa.resolve_question(
        "If you are currently enrolled in university or a program, what is your expected graduation date?",
        field_type="text",
        job=sample_job
    )
    assert "May 2028" in res["answer"] or "2028" in res["answer"]
    assert res["is_ai_generated"] is False


def test_deterministic_eeo_demographics(sample_job):
    qa = QAGenerator()
    g_res = qa.resolve_question("What is your gender?", field_type="select", job=sample_job, options=["Male", "Female", "Decline"])
    assert g_res["answer"] == "Male"

    v_res = qa.resolve_question("Veteran Status", field_type="select", job=sample_job, options=["I am not a protected veteran", "I am a veteran", "Decline"])
    assert "not a protected veteran" in v_res["answer"]


def test_options_heuristic_engineering_track(sample_job):
    qa = QAGenerator()
    options = [
        "Select your choice",
        "Frontend Engineering",
        "Infrastructure / Systems Engineering",
        "Data Analytics"
    ]
    res = qa.resolve_question(
        "Which type of engineering work are you most excited to do at Figma? Select your first choice.",
        field_type="select",
        job=sample_job,
        options=options
    )
    assert res["answer"] == "Infrastructure / Systems Engineering"
    assert res["category"] == "engineering_track_choice"


def test_llm_subjective_generation_mocked(sample_job):
    qa = QAGenerator()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "I built RudraKernel for multi-agent reinforcement learning safety, aligning directly with Figma's mission."
                }
            }
        ]
    }

    with patch("httpx.Client.post", return_value=mock_resp):
        res = qa.resolve_question(
            "Why do you want to join Figma?",
            field_type="textarea",
            job=sample_job
        )
        assert res["is_ai_generated"] is True
        assert "RudraKernel" in res["answer"]
        assert res["confidence"] >= 0.9
