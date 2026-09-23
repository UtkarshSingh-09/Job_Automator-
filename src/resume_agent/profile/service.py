import json
from datetime import datetime
from typing import Optional, Any
from resume_agent.db import get_db
from resume_agent.models import ProfileModel
from resume_agent.logging import logger


def save_profile(profile: ProfileModel) -> None:
    """Upsert profile into SQLite as singleton row id=1."""
    data = profile.to_db_row()
    sql = """
    INSERT INTO profile (
        id, full_name, email, phone, github_url, linkedin_url, portfolio_url,
        college, degree, branch, grad_year, cgpa, location,
        skills_json, coursework_json, achievements_json, certifications_json,
        raw_text, confirmed_at, updated_at
    ) VALUES (
        :id, :full_name, :email, :phone, :github_url, :linkedin_url, :portfolio_url,
        :college, :degree, :branch, :grad_year, :cgpa, :location,
        :skills_json, :coursework_json, :achievements_json, :certifications_json,
        :raw_text, :confirmed_at, CURRENT_TIMESTAMP
    )
    ON CONFLICT(id) DO UPDATE SET
        full_name = excluded.full_name,
        email = excluded.email,
        phone = excluded.phone,
        github_url = excluded.github_url,
        linkedin_url = excluded.linkedin_url,
        portfolio_url = excluded.portfolio_url,
        college = excluded.college,
        degree = excluded.degree,
        branch = excluded.branch,
        grad_year = excluded.grad_year,
        cgpa = excluded.cgpa,
        location = excluded.location,
        skills_json = excluded.skills_json,
        coursework_json = excluded.coursework_json,
        achievements_json = excluded.achievements_json,
        certifications_json = excluded.certifications_json,
        raw_text = excluded.raw_text,
        confirmed_at = excluded.confirmed_at,
        updated_at = CURRENT_TIMESTAMP;
    """
    with get_db() as conn:
        conn.execute(sql, data)
        logger.info(f"Saved profile for candidate '{profile.full_name}' (ID=1)")


def get_profile() -> Optional[ProfileModel]:
    """Retrieve profile from SQLite database."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM profile WHERE id = 1;").fetchone()
        if not row:
            return None

        return ProfileModel(
            id=row["id"],
            full_name=row["full_name"],
            email=row["email"],
            phone=row["phone"],
            github_url=row["github_url"],
            linkedin_url=row["linkedin_url"],
            portfolio_url=row["portfolio_url"],
            college=row["college"],
            degree=row["degree"],
            branch=row["branch"],
            grad_year=row["grad_year"],
            cgpa=row["cgpa"],
            location=row["location"],
            skills=json.loads(row["skills_json"] or "[]"),
            coursework=json.loads(row["coursework_json"] or "[]"),
            achievements=json.loads(row["achievements_json"] or "[]"),
            certifications=json.loads(row["certifications_json"] or "[]"),
            raw_text=row["raw_text"],
            confirmed_at=datetime.fromisoformat(row["confirmed_at"]) if row["confirmed_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
        )


def confirm_profile() -> None:
    """Set confirmed_at timestamp to now."""
    with get_db() as conn:
        conn.execute(
            "UPDATE profile SET confirmed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = 1;"
        )
        logger.info("Profile confirmation timestamp updated.")


def update_profile_field(field_name: str, value: Any) -> None:
    """Update a specific field on profile record."""
    allowed_fields = {
        "full_name", "email", "phone", "github_url", "linkedin_url",
        "portfolio_url", "college", "degree", "branch", "grad_year", "cgpa", "location"
    }
    if field_name not in allowed_fields:
        raise ValueError(f"Field '{field_name}' cannot be modified directly via CLI.")

    with get_db() as conn:
        conn.execute(
            f"UPDATE profile SET {field_name} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1;",
            (value,)
        )


def is_profile_confirmed() -> bool:
    """Check if candidate profile exists and has been confirmed by human gate."""
    with get_db() as conn:
        row = conn.execute("SELECT confirmed_at FROM profile WHERE id = 1;").fetchone()
        return bool(row and row["confirmed_at"])


def ensure_candidate_profile() -> Optional[ProfileModel]:
    """Ensure candidate profile exists in SQLite database, initializing from seed JSON if missing."""
    p = get_profile()
    if p is not None:
        return p

    from pathlib import Path
    from resume_agent.config import get_settings
    settings = get_settings()

    candidate_paths = [
        settings.data_dir / "config" / "candidate_profile.json",
        settings.project_root / "data" / "config" / "candidate_profile.json",
        Path("/app/seed_config/candidate_profile.json"),
        Path("/app/data/config/candidate_profile.json"),
        Path(__file__).resolve().parent.parent.parent.parent / "data" / "config" / "candidate_profile.json",
    ]

    for cpath in candidate_paths:
        if cpath.exists():
            try:
                with open(cpath, "r", encoding="utf-8") as f:
                    pdata = json.load(f)
                # Convert timestamps if present as strings
                if "confirmed_at" in pdata and pdata["confirmed_at"]:
                    pdata["confirmed_at"] = datetime.fromisoformat(str(pdata["confirmed_at"]))
                if "updated_at" in pdata and pdata["updated_at"]:
                    pdata["updated_at"] = datetime.fromisoformat(str(pdata["updated_at"]))
                profile = ProfileModel(**pdata)
                save_profile(profile)
                confirm_profile()
                logger.info(f"Initialized verified candidate profile for '{profile.full_name}' from {cpath}")
                return profile
            except Exception as e:
                logger.warning(f"Could not load seed profile from {cpath}: {e}")

    logger.warning("No candidate profile found or seed JSON available.")
    return None
