from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from resume_agent.models import ProfileModel


class ApplyResult(BaseModel):
    """Result of an automated or simulated application submission attempt."""
    success: bool
    status: str  # submitted | dry_run | needs_login | captcha_blocked | form_error | failed | daily_limit_reached | cooldown_active
    method: str  # direct_api | playwright_form
    screenshot_path: Optional[Path] = None
    notes: str = ""
    error: Optional[str] = None
    response_data: Dict[str, Any] = Field(default_factory=dict)


class CandidateSubmissionPayload(BaseModel):
    """Normalized structured profile payload ready for ATS form injection or API upload."""
    first_name: str
    last_name: str
    full_name: str
    email: str
    phone: str
    linkedin_url: str
    github_url: str
    portfolio_url: str
    college: str
    degree: str
    branch: str
    grad_year: int
    cgpa: float
    location: str

    @classmethod
    def from_profile_model(cls, profile: ProfileModel) -> "CandidateSubmissionPayload":
        """Build normalized submission payload from candidate profile."""
        full_name = profile.full_name.strip()
        parts = full_name.split()
        first_name = parts[0] if parts else "Utkarsh"
        last_name = " ".join(parts[1:]) if len(parts) > 1 else "Singh"

        return cls(
            first_name=first_name,
            last_name=last_name,
            full_name=full_name,
            email=profile.email,
            phone=profile.phone or "+91-7565960168",
            linkedin_url=profile.linkedin_url or "https://linkedin.com/in/utkarshsingh09",
            github_url=profile.github_url or "https://github.com/UtkarshSingh-09",
            portfolio_url=profile.portfolio_url or "https://github.com/UtkarshSingh-09",
            college=profile.college or "SRM University Amaravati",
            degree=profile.degree or "B.Tech in Computer Science",
            branch=profile.branch or "Computer Science",
            grad_year=profile.grad_year or 2028,
            cgpa=profile.cgpa or 8.78,
            location=profile.location or "Ayodhya, UP, India",
        )
