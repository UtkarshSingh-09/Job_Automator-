"""
Test Suite for 7-Gate Mechanical ATS Verification Suite (Phase 8).
Validates deterministic execution of all gates:
Gate 1: Parse-Back Fidelity
Gate 2: Section Boundary Sequence
Gate 3: Unicode & Ligature Integrity
Gate 4: Zero Trailing Hyphenation
Gate 5: Single-Page Physical Geometry
Gate 6: JD Keyword Coverage
Gate 7: Anti-Hallucination Grounding Audit
"""
import pytest
from pathlib import Path
from resume_agent.models import ProfileModel, JobModel
from resume_agent.validate.parseback import verify_parseback_fidelity
from resume_agent.validate.hygiene import (
    verify_section_order,
    verify_unicode_integrity,
    verify_zero_hyphenation,
    verify_page_geometry,
)
from resume_agent.validate.keywords import verify_keyword_coverage, extract_jd_keywords
from resume_agent.validate.audit import verify_grounding_audit


@pytest.fixture
def sample_profile():
    return ProfileModel(
        id=1,
        full_name="Utkarsh Singh",
        email="thakurutkarsh2212@gmail.com",
        phone="+91-7565960168",
        college="SRM University Amaravati",
        degree="Bachelor of Technology in Computer Science",
        branch="Computer Science",
        grad_year=2028,
        cgpa=8.78,
        skills=["Python", "C++", "SQL", "Go", "FastAPI", "Docker"],
        achievements=["Zenith Hackathon Runner-Up"],
    )


@pytest.fixture
def valid_resume_text():
    return """
Utkarsh Singh
Ayodhya, UP, India | +91-7565960168 | thakurutkarsh2212@gmail.com | github.com/UtkarshSingh-09 | linkedin.com/in/utkarshsingh09

Education
SRM University Amaravati Amaravati, India
Bachelor of Technology in Computer Science Aug 2024 – May 2028
CGPA: 8.78 / 10.00 | Coursework: Data Structures & Algorithms, DBMS, Operating Systems, Machine Learning

Technical Skills
Languages: Python, C++, SQL, Go, TypeScript, JavaScript, HTML5, CSS3
Frameworks & Libraries: FastAPI, Next.js 16, React 19, LangGraph, LiveKit WebRTC, Deepgram SDK, Razorpay SDK, Pydantic v2
Databases & Vector Stores: Qdrant Vector DB (14 Collections), PostgreSQL 16, Redis 7, SQLite, ChromaDB
ML, RL & AI Safety: Sentence-Transformers (bge-small, MiniLM), XGBoost, LightGBM, SHAP, LIME, OpenEnv, LoRA
Developer Tools & Protocols: Docker, Git, GitHub Actions CI/CD, WebSockets, Redis Pub/Sub, Raw Sockets (TCP/UDP), Linux, RESTful APIs

Technical Projects
Trinetra | Agentic Commercial Credit Intelligence OS GitHub | Patent Filed
Python, FastAPI, Qdrant Vector DB, Redis Pub/Sub, XGBoost, SHAP/LIME Dec 2025 – Jan 2026
• Engineered a financial document intelligence pipeline achieving 90-second CAM generation by coordinating 13 LangGraph agents with RESTful APIs.
• Automated credit risk analysis reducing manual workflow from 2–3 weeks to 60 seconds using XGBoost with SHAP/LIME explainability.
• Designed a multi-agent architecture ensuring sub-second task scheduling by integrating FastAPI with structured logging.

MerchantMind | Autonomous Conversational Commerce Engine GitHub | Demo Video | Live
Python 3.12, FastAPI, PostgreSQL 16, Redis 7, Razorpay SDK Jan 2026 – Feb 2026
• Engineered a multi-agent conversational-commerce platform supporting 200+ stores and 5,000+ products by orchestrating FastAPI with PostgreSQL.
• Optimized catalog retrieval to sub-650ms latency by implementing Redis multi-tier caching and efficient query routing.
• Secured atomic 3-phase checkout using PostgreSQL row-level locks and Razorpay Payment Links, preventing duplicate charges.

Honors & Achievements
• 1st Runner-Up ($1,500 Prize): Zenith National Hackathon (Built Aegis Forge distributed multi-agent system).
• Top Finalist: Meta OpenEnv x PyTorch Hackathon 2026 (Built RudraKernel multi-agent RL environment).
• Top 25 Finalist: Logithon ’25 @ IIT Bombay and HackFor Green Bharat @ Microsoft Gurugram.
• Competitive Programming: Solved 150+ DSA problems on LeetCode covering dynamic programming, graph theory.
"""


def test_gate_1_parseback_passes(valid_resume_text, sample_profile):
    """Gate 1: Assert all candidate core identity fields are recovered."""
    is_pass, details, violations = verify_parseback_fidelity(valid_resume_text, sample_profile)
    assert is_pass is True
    assert len(violations) == 0
    assert details["recovered_fields_count"] == details["total_fields_count"]


def test_gate_1_parseback_detects_missing_identity(sample_profile):
    """Gate 1: Detects missing name or email in corrupted text stream."""
    corrupted_text = "Some Unknown Candidate | +91-7565960168 | Education SRM University 8.78 2028"
    is_pass, details, violations = verify_parseback_fidelity(corrupted_text, sample_profile)
    assert is_pass is False
    assert any("candidate_name" in v for v in violations)
    assert any("email_address" in v for v in violations)


def test_gate_2_section_order_passes(valid_resume_text):
    """Gate 2: Assert standard reading sequence passes."""
    is_pass, details, violations = verify_section_order(valid_resume_text)
    assert is_pass is True
    assert len(violations) == 0


def test_gate_2_section_order_detects_scrambled():
    """Gate 2: Detects sections placed out of order (e.g. Projects before Education)."""
    scrambled_text = """
    Utkarsh Singh
    Technical Projects
    Aegis Forge
    Education
    SRM University
    Technical Skills
    Python
    Honors & Achievements
    Zenith Hackathon
    """
    is_pass, details, violations = verify_section_order(scrambled_text)
    assert is_pass is False
    assert any("Section order violation" in v for v in violations)


def test_gate_3_unicode_detects_ufffd(valid_resume_text):
    """Gate 3: Detects unmapped glyph '\ufffd'."""
    corrupted_text = valid_resume_text.replace("FastAPI", "FastAP\ufffd")
    is_pass, details, violations = verify_unicode_integrity(corrupted_text)
    assert is_pass is False
    assert any("unmapped glyph" in v for v in violations)


def test_gate_3_unicode_detects_pua_icons(valid_resume_text):
    """Gate 3: Detects FontAwesome PUA characters."""
    icon_text = valid_resume_text + "\n\uE001 Phone \uE002 Email"
    is_pass, details, violations = verify_unicode_integrity(icon_text)
    assert is_pass is False
    assert any("Private Use Area" in v for v in violations)


def test_gate_4_zero_hyphenation_detects_severed_token():
    """Gate 4: Detects keyword severed with trailing hyphen across lines."""
    mutilated_text = "Engineered enterprise cloud microservices using Kuber-\nnetes and deployed containers."
    is_pass, details, violations = verify_zero_hyphenation(mutilated_text)
    assert is_pass is False
    assert any("Word severed across line break" in v for v in violations)


def test_gate_5_page_geometry(tmp_path):
    """Gate 5: Checks page count == 1."""
    import fitz
    # Create single-page PDF
    single_pdf = tmp_path / "single.pdf"
    doc1 = fitz.open()
    doc1.new_page()
    doc1.save(single_pdf)
    doc1.close()

    is_pass, details, violations = verify_page_geometry(single_pdf)
    assert is_pass is True
    assert details["page_count"] == 1

    # Create 2-page PDF
    multi_pdf = tmp_path / "multi.pdf"
    doc2 = fitz.open()
    doc2.new_page()
    doc2.new_page()
    doc2.save(multi_pdf)
    doc2.close()

    is_pass2, details2, violations2 = verify_page_geometry(multi_pdf)
    assert is_pass2 is False
    assert details2["page_count"] == 2


def test_gate_6_keyword_coverage(valid_resume_text):
    """Gate 6: Calculates keyword coverage against target job."""
    sample_job = JobModel(
        id=1,
        company_id=1,
        company_name="Acme Corp",
        title="Software Engineer Intern",
        description_md="We are seeking an intern skilled in Python, SQL, FastAPI, Docker, and Redis.",
        apply_url="https://acme.com/jobs/1",
        source="greenhouse",
        content_hash="abc123hash",
    )
    is_pass, details, violations = verify_keyword_coverage(valid_resume_text, sample_job, min_coverage_pct=80.0)
    assert is_pass is True
    assert details["coverage_score"] == 100.0
    assert len(details["missing_terms"]) == 0


def test_gate_7_grounding_audit_passes(valid_resume_text, sample_profile):
    """Gate 7: Verified portfolio tools pass grounding audit."""
    is_pass, details, violations = verify_grounding_audit(valid_resume_text, sample_profile)
    assert is_pass is True
    assert len(violations) == 0


def test_gate_7_grounding_audit_detects_fabrication(valid_resume_text, sample_profile):
    """Gate 7: Detects ungrounded tools (e.g. Solidity, Ethereum, Hadoop)."""
    fabricated_text = valid_resume_text + "\nEngineered smart contracts using Solidity on Ethereum with Hadoop cluster."
    is_pass, details, violations = verify_grounding_audit(fabricated_text, sample_profile)
    assert is_pass is False
    assert any("solidity" in v.lower() or "ethereum" in v.lower() for v in violations)
