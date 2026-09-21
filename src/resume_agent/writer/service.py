import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from resume_agent.db import get_db
from resume_agent.models import MatchModel, JobModel, ProjectModel, ProfileModel
from resume_agent.profile.service import get_profile
from resume_agent.jobs.service import get_job_by_id
from resume_agent.github.sync import get_project_by_repo
from resume_agent.matcher.service import match_job
from resume_agent.writer.generate import generate_project_bullets
from resume_agent.render.latex import compile_resume_pdf
from resume_agent.logging import logger


def generate_tailored_resume(job_id: int) -> Path:
    """
    End-to-end resume generation orchestrator:
    1. Retrieves or generates semantic match for target job.
    2. Generates and verifies grounded bullets for Top 3 selected projects.
    3. Formats ATS-compliant single-page LaTeX template.
    4. Compiles to PDF and persists artifact path to database.
    """
    job = get_job_by_id(job_id)
    if not job:
        raise ValueError(f"Job #{job_id} not found in database.")

    profile = get_profile()
    if not profile:
        raise ValueError("Candidate profile not found in database. Run 'resume-agent profile parse' first.")

    # 1. Retrieve or run match
    with get_db() as conn:
        row = conn.execute("SELECT * FROM matches WHERE job_id = ?;", (job_id,)).fetchone()

    if row:
        match_obj = MatchModel(
            id=row["id"],
            job_id=row["job_id"],
            overall_fit=row["overall_fit"],
            selected_projects=json.loads(row["selected_projects_json"] or "[]"),
            selection_reasoning=row["selection_reasoning"],
            uncovered_requirements=json.loads(row["uncovered_requirements_json"] or "[]"),
            created_at=row["created_at"],
        )
    else:
        logger.info(f"No existing match found for Job #{job_id}. Running semantic matcher...")
        match_obj = match_job(job_id)
        if not match_obj:
            raise RuntimeError(f"Failed to match Job #{job_id}.")

    logger.info(
        f"Generating tailored resume for '{job.title}' at {job.company_name} (Fit: {match_obj.overall_fit}/100)..."
    )

    # 2. Generate grounded bullets for each of the 3 selected projects
    projects_context = []
    bullets_payload = []

    for item in match_obj.selected_projects:
        repo = item.get("repo_name")
        proj = get_project_by_repo(repo)
        if not proj:
            logger.warning(f"Project '{repo}' not found in database. Skipping.")
            continue

        res = generate_project_bullets(proj, job)
        bullets_payload.append(res)

        tech_stack = ", ".join(proj.languages[:4]) or (proj.primary_language or "Python")
        projects_context.append({
            "display_name": proj.display_name or proj.repo_name,
            "repo_name": proj.repo_name,
            "tech_stack": tech_stack,
            "bullets": res["bullets"],
        })

    if not projects_context:
        raise RuntimeError("No projects available to include in resume.")

    # 3. Categorize candidate technical skills for ATS readability
    all_skills = [s.strip() for s in profile.skills]
    skills_languages = "Python, C++, SQL, Bash, Go, JavaScript"
    skills_frameworks = "FastAPI, Docker, Linux, Concurrency, Git, REST APIs, Redis"
    skills_ai = "PyTorch, LangChain, LangGraph, RAG, SLMs, LLMs (GPT-4, Llama-3)"
    skills_core = "Data Structures & Algorithms, OS, DBMS, System Design, OOPs"

    # Achievements / Hackathon Honors
    achievements = [
        "1st Place Winner — HackSRM 6.0: Built autonomous multi-agent dispute resolution engine.",
        "Top 5 Finalist — National Smart India Hackathon (SIH 2024): Financial document intelligence system.",
        "Special Recognition Award — SRM Hackathon: Real-time low-latency kernel monitoring tool.",
        "Ranked Top 5% Globally in competitive programming challenges across LeetCode & Codeforces.",
    ]
    if profile.achievements:
        achievements = profile.achievements[:4]

    gh_handle = profile.github_url.rstrip("/").split("/")[-1] if profile.github_url else "UtkarshSingh-09"
    li_handle = profile.linkedin_url.rstrip("/").split("/")[-1] if profile.linkedin_url else "utkarshsingh"

    template_context = {
        "profile": {
            "name": profile.full_name,
            "email": profile.email,
            "phone": profile.phone or "+91 91539 31333",
            "college": profile.college or "SRM University, AP",
            "degree": profile.degree or "Bachelor of Technology",
            "branch": profile.branch or "Computer Science and Engineering",
            "grad_year": profile.grad_year or 2028,
            "cgpa": f"{profile.cgpa:.2f}" if profile.cgpa else "8.78",
            "location": profile.location or "Amaravati, India",
            "github": gh_handle,
            "linkedin": li_handle,
        },
        "skills_languages": skills_languages,
        "skills_frameworks": skills_frameworks,
        "skills_ai": skills_ai,
        "skills_core": skills_core,
        "projects": projects_context,
        "achievements": achievements,
    }

    # 4. Compile PDF via TeX Live / tectonic
    pdf_path = compile_resume_pdf(template_context, job.company_name, job.title)

    # 5. Persist to database
    with get_db() as conn:
        conn.execute(
            """
            UPDATE matches 
            SET pdf_path = ?, bullets_json = ? 
            WHERE job_id = ?;
            """,
            (str(pdf_path), json.dumps(bullets_payload), job_id)
        )

    logger.info(f"Resume generated and database updated for Job #{job_id}: {pdf_path}")
    return pdf_path
