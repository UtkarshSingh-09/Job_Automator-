"""
Anti-Hallucination Grounding Test Suite
Validates that verify_bullets accurately passes grounded bullets and strictly
detects & rejects fabricated technologies, hallucinated metrics, pronoun violations, and length bounds.
"""
import pytest
from resume_agent.models import ProjectModel
from resume_agent.writer.verify import verify_bullets


@pytest.fixture
def sample_merchantmind():
    return ProjectModel(
        id=1,
        repo_name="merchantmind",
        display_name="MerchantMind",
        description="Autonomous Conversational-Commerce & Dispute Resolution Engine",
        primary_language="Python",
        languages=["Python", "JavaScript", "SQL", "HTML"],
        topics=["fastapi", "redis", "postgresql", "razorpay", "multi-agent"],
        manual_notes="Engineered multi-agent conversational-commerce platform using Python and FastAPI, processing 5,000+ products with sub-650ms cached catalog retrieval via Redis. Architected atomic 3-phase checkout saga with PostgreSQL row-level locks and Razorpay Payment Links, ensuring idempotency and preventing duplicate charges via HMAC-SHA256 webhooks. Validated by 151-test security suite.",
    )


@pytest.fixture
def sample_trinetra():
    return ProjectModel(
        id=2,
        repo_name="trinetra",
        display_name="Trinetra",
        description="Automated Financial Document Intelligence & Credit Risk Pipeline",
        primary_language="Python",
        languages=["Python", "SQL"],
        topics=["fastapi", "langgraph", "xgboost", "rag", "shap"],
        manual_notes="Engineered financial document intelligence pipeline using Python and FastAPI, reducing credit risk analysis time from 2-3 weeks to under 90 seconds. Architected RESTful APIs coordinating 13 concurrent LangGraph agents with sub-second task scheduling for parallel multi-format document processing. Integrated XGBoost with SHAP/LIME explainability for transparent credit risk scoring.",
    )


def test_grounded_bullets_pass(sample_merchantmind):
    """Grounded bullets matching verified project metrics must pass verification."""
    valid_bullets = [
        "Engineered multi-agent conversational platform using Python and FastAPI, processing 5,000+ products with sub-650ms cached catalog retrieval via Redis.",
        "Architected atomic 3-phase checkout saga with PostgreSQL row-level locks and Razorpay Payment Links, ensuring idempotency and preventing duplicate charges.",
        "Implemented deterministic budget enforcement and Redis sliding-window rate limiting, validated by 151-test security suite for reliable transaction handling.",
    ]
    is_valid, violations = verify_bullets(valid_bullets, sample_merchantmind)
    assert is_valid is True
    assert len(violations) == 0


def test_reject_hallucinated_technology(sample_merchantmind):
    """Bullets introducing technologies not present in project truth must be rejected."""
    hallucinated_bullets = [
        "Architected enterprise distributed cloud data pipeline using Kubernetes and Apache Spark for petabyte-scale stream processing.",
        "Architected atomic 3-phase checkout saga with PostgreSQL row-level locks and Razorpay Payment Links, ensuring idempotency and preventing duplicate charges.",
        "Implemented deterministic budget enforcement and Redis sliding-window rate limiting, validated by 151-test security suite for reliable transaction handling.",
    ]
    is_valid, violations = verify_bullets(hallucinated_bullets, sample_merchantmind)
    assert is_valid is False
    assert any("kubernetes" in v.lower() or "spark" in v.lower() for v in violations)


def test_reject_hallucinated_metrics(sample_merchantmind):
    """Bullets fabricating metrics (e.g. 99.999% uptime or 10,000 rps) must be rejected."""
    fake_metric_bullets = [
        "Optimized checkout transaction throughput achieving 99.999% uptime and sub-10ms latency across global distributed multi-region server clusters.",
        "Architected atomic 3-phase checkout saga with PostgreSQL row-level locks and Razorpay Payment Links, ensuring idempotency and preventing duplicate charges.",
        "Implemented deterministic budget enforcement and Redis sliding-window rate limiting, validated by 151-test security suite for reliable transaction handling.",
    ]
    is_valid, violations = verify_bullets(fake_metric_bullets, sample_merchantmind)
    assert is_valid is False
    assert any("ungrounded metric" in v.lower() for v in violations)


def test_reject_first_person_pronouns(sample_merchantmind):
    """Bullets using first-person pronouns must be rejected."""
    fp_bullets = [
        "I engineered the conversational commerce backend platform using Python and FastAPI, processing 5,000+ products with sub-650ms cached retrieval.",
        "Architected atomic 3-phase checkout saga with PostgreSQL row-level locks and Razorpay Payment Links, ensuring idempotency and preventing duplicate charges.",
        "Implemented deterministic budget enforcement and Redis sliding-window rate limiting, validated by 151-test security suite for reliable transaction handling.",
    ]
    is_valid, violations = verify_bullets(fp_bullets, sample_merchantmind)
    assert is_valid is False
    assert any("first-person" in v.lower() for v in violations)


def test_reject_too_short_bullets(sample_merchantmind):
    """Bullets under 14 words must be rejected."""
    short_bullets = [
        "Engineered Python FastAPI backend with Redis caching for rapid catalog retrieval.",  # 10 words
        "Architected atomic 3-phase checkout saga with PostgreSQL row-level locks and Razorpay Payment Links, ensuring idempotency and preventing duplicate charges.",
        "Implemented deterministic budget enforcement and Redis sliding-window rate limiting, validated by 151-test security suite for reliable transaction handling.",
    ]
    is_valid, violations = verify_bullets(short_bullets, sample_merchantmind)
    assert is_valid is False
    assert any("words" in v.lower() for v in violations)


def test_reject_too_long_bullets(sample_merchantmind):
    """Bullets over 26 words must be rejected to fit single-page budget."""
    long_bullets = [
        "Engineered multi-agent conversational-commerce platform using Python and FastAPI, processing 5,000+ products with sub-650ms cached catalog retrieval via Redis, and integrated external third-party microservices across multiple distributed environments worldwide.",  # 30 words
        "Architected atomic 3-phase checkout saga with PostgreSQL row-level locks and Razorpay Payment Links, ensuring idempotency and preventing duplicate charges.",
        "Implemented deterministic budget enforcement and Redis sliding-window rate limiting, validated by 151-test security suite for reliable transaction handling.",
    ]
    is_valid, violations = verify_bullets(long_bullets, sample_merchantmind)
    assert is_valid is False
    assert any("words" in v.lower() for v in violations)


def test_trinetra_grounded_bullets_pass(sample_trinetra):
    """Grounded bullets for Trinetra must pass verification."""
    trinetra_bullets = [
        "Engineered financial document intelligence pipeline using Python and FastAPI, reducing credit risk analysis time from 2-3 weeks to under 90 seconds.",
        "Architected RESTful APIs coordinating 13 concurrent LangGraph agents with sub-second task scheduling for parallel multi-format document processing.",
        "Integrated XGBoost with SHAP/LIME explainability for transparent credit risk scoring, ensuring regulatory compliance and auditability.",
    ]
    is_valid, violations = verify_bullets(trinetra_bullets, sample_trinetra)
    assert is_valid is True
    assert len(violations) == 0


def test_trinetra_reject_hallucinated_blockchain(sample_trinetra):
    """Injecting blockchain or smart contract claims into Trinetra must be rejected."""
    poisoned_bullets = [
        "Engineered decentralized credit risk audit ledger deploying Solidity smart contracts on Ethereum mainnet with zero-knowledge proof verification.",
        "Architected RESTful APIs coordinating 13 concurrent LangGraph agents with sub-second task scheduling for parallel multi-format document processing.",
        "Integrated XGBoost with SHAP/LIME explainability for transparent credit risk scoring, ensuring regulatory compliance and auditability.",
    ]
    is_valid, violations = verify_bullets(poisoned_bullets, sample_trinetra)
    assert is_valid is False
    assert any("solidity" in v.lower() or "ethereum" in v.lower() for v in violations)


def test_markdown_bolded_metrics_pass(sample_merchantmind):
    """Bullets featuring markdown bold highlights for metrics and tools must pass verification cleanly."""
    bold_bullets = [
        "Engineered multi-agent conversational platform using **Python** and **FastAPI**, processing 5,000+ products with **sub-650ms** cached catalog retrieval via Redis.",
        "Architected atomic 3-phase checkout saga with **PostgreSQL** row-level locks and Razorpay Payment Links, ensuring idempotency and preventing duplicate charges.",
        "Implemented deterministic budget enforcement and Redis sliding-window rate limiting, validated by **151-test** security suite for reliable transaction handling.",
    ]
    is_valid, violations = verify_bullets(bold_bullets, sample_merchantmind)
    assert is_valid is True
    assert len(violations) == 0


def test_reject_weak_action_starters(sample_merchantmind):
    """Bullets starting with passive or weak verbs ('Worked on', 'Assisted in') must fail First 4 Words Rule."""
    weak_bullets = [
        "Worked on multi-agent conversational platform using Python and FastAPI, processing 5,000+ products with sub-650ms cached catalog retrieval via Redis.",
        "Architected atomic 3-phase checkout saga with PostgreSQL row-level locks and Razorpay Payment Links, ensuring idempotency and preventing duplicate charges.",
        "Implemented deterministic budget enforcement and Redis sliding-window rate limiting, validated by 151-test security suite for reliable transaction handling.",
    ]
    is_valid, violations = verify_bullets(weak_bullets, sample_merchantmind)
    assert is_valid is False
    assert any("weak phrasing" in v.lower() for v in violations)

