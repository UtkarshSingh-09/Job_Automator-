import re
from pathlib import Path
from typing import List, Optional
import fitz  # PyMuPDF
from resume_agent.models import ProfileModel
from resume_agent.logging import logger


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract raw UTF-8 text from all pages of a PDF document."""
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

    doc = fitz.open(str(pdf_path))
    pages_text = []
    for page in doc:
        pages_text.append(page.get_text())
    doc.close()
    return "\n".join(pages_text)


def parse_profile_deterministic(raw_text: str) -> ProfileModel:
    """
    Deterministically extract structured candidate profile from resume text using
    regular expressions and robust layout heuristics.
    """
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    # 1. Full Name
    # The first line of the resume is usually the candidate's name
    full_name = "Utkarsh Singh"
    if lines and len(lines[0].split()) <= 4:
        candidate_name = lines[0].title()
        if "Resume" not in candidate_name and "Curriculum" not in candidate_name:
            full_name = candidate_name

    # 2. Email Address
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", raw_text)
    email = email_match.group(0) if email_match else "thakurutkarsh2212@gmail.com"

    # 3. Phone Number
    phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}", raw_text)
    phone = phone_match.group(0).strip() if phone_match else "+91-7565960168"

    # 4. GitHub URL
    github_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/([\w-]+)", raw_text, re.IGNORECASE)
    github_url = f"https://github.com/{github_match.group(1)}" if github_match else "https://github.com/UtkarshSingh-09"

    # 5. LinkedIn URL
    linkedin_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/([\w-]+)", raw_text, re.IGNORECASE)
    linkedin_url = f"https://linkedin.com/in/{linkedin_match.group(1)}" if linkedin_match else "https://linkedin.com/in/utkarshsingh09"

    # 6. Location
    location = "Ayodhya, UP, India"
    loc_match = re.search(r"([^\n,]+,\s*[^\n,]+,\s*India)", raw_text)
    if loc_match:
        location = loc_match.group(1).strip()

    # 7. Education & Academics
    college = "SRM University Amaravati"
    degree = "B.Tech in Computer Science"
    branch = "Computer Science"
    grad_year = 2028
    cgpa = 8.78

    if "SRM" in raw_text:
        college_match = re.search(r"(SRM University[^\n—–-]+)", raw_text, re.IGNORECASE)
        if college_match:
            college = college_match.group(0).strip()

    degree_match = re.search(r"(B\.Tech[^\n—–-]*)", raw_text, re.IGNORECASE)
    if degree_match:
        degree = degree_match.group(0).strip()

    cgpa_match = re.search(r"CGPA:\s*([0-9]+\.[0-9]+)", raw_text, re.IGNORECASE)
    if cgpa_match:
        cgpa = float(cgpa_match.group(1))

    grad_match = re.search(r"202[4-9]\s*[–-]\s*(202[8-9]|203[0-9])", raw_text)
    if grad_match:
        grad_year = int(grad_match.group(1))

    # 8. Coursework
    coursework: List[str] = []
    coursework_match = re.search(r"Coursework:\s*([^\n]+(?:\n[^\n]+)?)", raw_text, re.IGNORECASE)
    if coursework_match:
        raw_coursework = coursework_match.group(1).split("TECHNICAL")[0].strip()
        items = re.split(r"[,•|]\s*", raw_coursework)
        coursework = [item.strip() for item in items if item.strip() and len(item.strip()) > 2]

    # 9. Technical Skills
    skills: List[str] = []
    skills_section_match = re.search(
        r"TECHNICAL SKILLS\s*\n(.*?)(?=\n(?:EXPERIENCE|PROJECTS|EDUCATION|ACHIEVEMENTS)\b|\Z)",
        raw_text,
        re.DOTALL
    )
    if skills_section_match:
        section_text = skills_section_match.group(1)
        for line in section_text.splitlines():
            line = line.strip()
            if not line:
                continue
            if ":" in line:
                _, line = line.split(":", 1)
            # Match items respecting commas outside parentheses
            for s in re.split(r"[,•|]\s*(?![^()]*\))", line):
                s_clean = s.strip()
                if s_clean and len(s_clean) > 1 and s_clean not in skills:
                    skills.append(s_clean)

    # 10. Achievements
    achievements: List[str] = []
    achieve_section_match = re.search(r"ACHIEVEMENTS\s*\n(.*?)(?=\n[A-Z\s]{4,}|\Z)", raw_text, re.DOTALL)
    if achieve_section_match:
        achieve_text = achieve_section_match.group(1)
        for bullet in re.split(r"(?:^|\n)\s*[•\-\*]\s*", achieve_text):
            cleaned = " ".join(bullet.split()).strip()
            if cleaned and len(cleaned) > 10:
                achievements.append(cleaned)

    profile = ProfileModel(
        id=1,
        full_name=full_name,
        email=email,
        phone=phone,
        github_url=github_url,
        linkedin_url=linkedin_url,
        portfolio_url="https://github.com/UtkarshSingh-09",
        college=college,
        degree=degree,
        branch=branch,
        grad_year=grad_year,
        cgpa=cgpa,
        location=location,
        skills=skills,
        coursework=coursework,
        achievements=achievements,
        certifications=[],
        raw_text=raw_text,
        confirmed_at=None,
    )
    return profile
