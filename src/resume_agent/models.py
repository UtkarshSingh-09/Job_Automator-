import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr


class ProfileModel(BaseModel):
    """User candidate profile (singleton row in DB)."""
    id: int = 1
    full_name: str
    email: str
    phone: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    grad_year: Optional[int] = None
    cgpa: Optional[float] = None
    location: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    coursework: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    raw_text: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_db_row(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "github_url": self.github_url,
            "linkedin_url": self.linkedin_url,
            "portfolio_url": self.portfolio_url,
            "college": self.college,
            "degree": self.degree,
            "branch": self.branch,
            "grad_year": self.grad_year,
            "cgpa": self.cgpa,
            "location": self.location,
            "skills_json": json.dumps(self.skills),
            "coursework_json": json.dumps(self.coursework),
            "achievements_json": json.dumps(self.achievements),
            "certifications_json": json.dumps(self.certifications),
            "raw_text": self.raw_text,
            "confirmed_at": self.confirmed_at.isoformat() if self.confirmed_at else None,
        }


class ProjectModel(BaseModel):
    """Candidate project ground truth corpus."""
    id: Optional[int] = None
    repo_name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    readme_md: Optional[str] = None
    manual_notes: Optional[str] = None
    languages: List[str] = Field(default_factory=list)
    primary_language: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    stars: int = 0
    commit_count: int = 0
    has_tests: bool = False
    has_ci: bool = False
    has_docker: bool = False
    line_count: int = 0
    quality_score: float = 0.0
    include_override: bool = False
    priority: int = 10
    embedding: Optional[bytes] = None
    embedding_source_hash: Optional[str] = None
    created_at: Optional[datetime] = None
    pushed_at: Optional[datetime] = None
    synced_at: Optional[datetime] = None


class CompanyModel(BaseModel):
    """Company target with ATS detection metadata."""
    id: Optional[int] = None
    name: str
    domain: str
    tier: int = 2
    ats_provider: Optional[str] = None
    ats_slug: Optional[str] = None
    detection_status: str = "unknown"
    etag: Optional[str] = None
    last_polled_at: Optional[datetime] = None
    consecutive_failures: int = 0


class JobModel(BaseModel):
    """Normalized job opportunity."""
    id: Optional[int] = None
    company_id: Optional[int] = None
    company_name: str
    title: str
    location: Optional[str] = None
    remote_type: Optional[str] = None
    description_md: str
    apply_url: str
    posted_at: Optional[datetime] = None
    source: str
    source_job_id: Optional[str] = None
    content_hash: str
    passed_filter: bool = False
    first_seen_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None


class MatchModel(BaseModel):
    """Semantic match result with generated resume artifacts."""
    id: Optional[int] = None
    job_id: int
    overall_fit: Optional[float] = None
    selected_projects: List[str] = Field(default_factory=list)
    selection_reasoning: Optional[str] = None
    uncovered_requirements: List[str] = Field(default_factory=list)
    bullets: List[Dict[str, Any]] = Field(default_factory=list)
    pdf_path: Optional[str] = None
    parse_ok: bool = False
    coverage_score: float = 0.0
    missing_terms: List[str] = Field(default_factory=list)
    attempts: int = 0
    needs_review: bool = False
    llm_cost_usd: float = 0.0
    created_at: Optional[datetime] = None


class ApplicationModel(BaseModel):
    """Application submission attempt and status."""
    id: Optional[int] = None
    match_id: int
    status: str = "generated"
    auto_apply_status: str = "pending"
    confirmation_screenshot: Optional[str] = None
    submit_attempted_at: Optional[datetime] = None
    applied_at: Optional[datetime] = None
    notes: Optional[str] = None


class RunLogModel(BaseModel):
    """Execution heartbeat log entry."""
    id: Optional[int] = None
    run_type: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: str
    stats: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
