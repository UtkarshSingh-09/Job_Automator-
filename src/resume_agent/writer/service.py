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


import re


def build_tailored_skills(job: JobModel, profile: ProfileModel) -> Dict[str, str]:
    """
    Dynamically tailor and prioritize candidate technical skills for target Job Description.
    Maintains 100% grounding to candidate profile and verified portfolio while prioritizing
    languages, frameworks, databases, AI/ML tools, and systems protocols mentioned in the target JD.
    """
    master_skills = {
        "languages": [
            "Python", "C++", "SQL", "TypeScript", "JavaScript", "Go", "C", "Bash", "Shell", "HTML5", "CSS3"
        ],
        "frameworks": [
            "FastAPI", "PyTorch", "Next.js 16", "React 19", "LangGraph", "LangChain", 
            "LiveKit WebRTC", "Pydantic v2", "Deepgram SDK", "Razorpay SDK", "XGBoost"
        ],
        "databases": [
            "PostgreSQL 16", "Redis 7", "Qdrant Vector DB", "SQLite", "ChromaDB"
        ],
        "ai_ml": [
            "LLMs (Fine-tuning, LoRA, GRPO, TRL)", "PyTorch", "RAG Pipelines", "Sentence-Transformers", 
            "Deep Learning", "NLP", "Multi-Agent RL", "OpenEnv", "SLMs", "Classical ML", "XGBoost", "SHAP", "LIME"
        ],
        "tools": [
            "Docker", "Git", "GitHub Actions CI/CD", "Concurrency", "WebSockets", 
            "Redis Pub/Sub", "Raw Sockets (TCP/UDP)", "Linux", "System Design", "RESTful APIs"
        ]
    }

    synonyms = {
        "python": ["python"],
        "c++": ["c++", "cpp"],
        "c": ["c"],
        "go": ["go", "golang"],
        "typescript": ["typescript", "ts"],
        "javascript": ["javascript", "js"],
        "sql": ["sql", "postgres", "postgresql"],
        "bash": ["bash", "shell"],
        "shell": ["shell", "bash"],
        "pytorch": ["pytorch", "torch"],
        "llms": ["llms", "llm", "large language models"],
        "fine-tuning": ["fine-tuning", "finetuning", "fine tuning"],
        "nlp": ["nlp", "natural language processing"],
        "deep learning": ["deep learning", "dl"],
        "rag": ["rag", "retrieval-augmented generation"],
        "concurrency": ["concurrency", "multithreading", "concurrent"],
        "linux": ["linux", "unix"],
        "fastapi": ["fastapi"],
        "next.js": ["next.js", "nextjs", "next"],
        "react": ["react", "reactjs"],
        "docker": ["docker", "container", "containers"],
        "git": ["git", "github", "gitlab"],
        "ci/cd": ["ci/cd", "continuous integration", "actions"],
        "kubernetes": ["kubernetes", "k8s"],
        "testing": ["testing", "unit test", "pytest"],
        "websockets": ["websockets", "websocket", "real-time"],
    }

    jd_text = f"{job.title} {job.description_md}".lower() if (job.title and job.description_md) else ""

    result = {}
    for cat, skills in master_skills.items():
        matched = []
        unmatched = []
        for s in skills:
            s_clean = s.split("(")[0].strip().lower()
            syns = [s_clean]
            for k, v in synonyms.items():
                if k in s_clean:
                    syns.extend(v)
            is_matched = any(re.search(r"\b" + re.escape(w) + r"\b", jd_text) for w in syns)
            if is_matched:
                matched.append(s)
            else:
                unmatched.append(s)

        # Keep matched first, and complement with remaining verified skills (up to 8)
        final_list = (matched + unmatched)[:8]
        result[cat] = ", ".join(final_list)

    return result


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

    # Metadata registry for flagship projects (temporal binding, dates, links)
    project_meta = {
        "merchantmind": {
            "subtitle": "Autonomous Conversational Commerce Engine",
            "date_range": "Jan 2026 -- Feb 2026",
            "tech_stack": "Python 3.12, FastAPI, PostgreSQL 16, Redis 7, Razorpay SDK",
            "demo_url": "https://youtu.be/hS77jr1y1z4",
            "live_url": "https://merchantmind-ai.netlify.app",
        },
        "trinetra": {
            "subtitle": "Agentic Commercial Credit Intelligence OS",
            "date_range": "Dec 2025 -- Jan 2026",
            "tech_stack": "Python, FastAPI, Qdrant Vector DB, Redis Pub/Sub, XGBoost, SHAP/LIME",
            "is_patent": True,
        },
        "aegis-forge": {
            "subtitle": "Real-Time Voice AI Interview Platform",
            "date_range": "Jan 2026 -- Feb 2026",
            "tech_stack": "Python, FastAPI, Next.js 16, LiveKit WebRTC, Deepgram Nova-3",
            "demo_url": "https://youtu.be/6XJ7HiaCKKQ",
        },
        "rudrakernel": {
            "subtitle": "Multi-Agent Reinforcement Learning Environment",
            "date_range": "Jan 2026 -- Feb 2026",
            "tech_stack": "Python, PyTorch, OpenEnv, Multi-Agent RL, GRPO, TRL, LoRA",
        },
    }

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

        meta = project_meta.get(repo.lower(), {})
        tech_stack = meta.get("tech_stack") or (", ".join(proj.languages[:4]) or (proj.primary_language or "Python"))
        subtitle = meta.get("subtitle") or (proj.description[:45] if proj.description else "")
        date_range = meta.get("date_range", "Oct 2025 -- Jan 2026")

        projects_context.append({
            "display_name": proj.display_name or proj.repo_name,
            "repo_name": proj.repo_name,
            "subtitle": subtitle,
            "tech_stack": tech_stack,
            "date_range": date_range,
            "demo_url": meta.get("demo_url"),
            "live_url": meta.get("live_url"),
            "is_patent": meta.get("is_patent", False),
            "bullets": res["bullets"],
        })

    if not projects_context:
        raise RuntimeError("No projects available to include in resume.")

    # 3. Categorize candidate technical skills dynamically tailored to target Job Description
    tailored_skills = build_tailored_skills(job, profile)
    skills_languages = tailored_skills["languages"]
    skills_frameworks = tailored_skills["frameworks"]
    skills_databases = tailored_skills["databases"]
    skills_ai = tailored_skills["ai_ml"]
    skills_tools = tailored_skills["tools"]

    coursework = "Data Structures & Algorithms, DBMS, Operating Systems, Machine Learning, System Design, Distributed Systems"

    # Achievements / Hackathon Honors with recruiter bolding
    achievements = [
        "**1st Runner-Up ($1,500 Prize):** Zenith National Hackathon (Built Aegis Forge distributed multi-agent system under competitive time constraints).",
        "**Top Finalist:** Meta OpenEnv x PyTorch Hackathon 2026 (Built RudraKernel multi-agent RL environment for LLM epistemic safety).",
        "**Top 25 Finalist:** Logithon '25 @ IIT Bombay and HackFor Green Bharat @ Microsoft Gurugram.",
        "**Competitive Programming:** Solved 150+ DSA problems on LeetCode covering dynamic programming, graph theory, and system optimization.",
    ]

    gh_handle = profile.github_url.rstrip("/").split("/")[-1] if profile.github_url else "UtkarshSingh-09"
    li_handle = profile.linkedin_url.rstrip("/").split("/")[-1] if profile.linkedin_url else "utkarshsingh09"

    degree_display = "Bachelor of Technology in Computer Science"
    if profile.degree and "bachelor" in profile.degree.lower():
        degree_display = profile.degree

    experience_context = [
        {
            "role": "Software Engineer — Freelance Consulting",
            "organization": "Client Deliveries & Applied AI Solutions",
            "location": "Ayodhya / Remote, India",
            "date_range": "Apr 2026 -- Present",
            "bullets": [
                "Shipped **Sanchay** (May 2026), a mobile inventory-management platform for real estate businesses serving **15+ active users**, featuring a voice-input RAG pipeline for natural-language queries that reduced manual tracking time by **~60%**.",
                "Engaged directly with SME clients to translate business requirements into production software; engineered backend APIs and managed Git pull request workflows.",
            ]
        }
    ]

    template_context = {
        "profile": {
            "name": profile.full_name,
            "email": profile.email,
            "phone": profile.phone or "+91-7565960168",
            "college": profile.college or "SRM University, AP",
            "degree": degree_display,
            "date_range": "Aug 2024 -- May 2028",
            "cgpa": f"{profile.cgpa:.2f}" if profile.cgpa else "8.78",
            "location": profile.location or "Ayodhya, UP, India",
            "github": gh_handle,
            "linkedin": li_handle,
        },
        "coursework": coursework,
        "skills_languages": skills_languages,
        "skills_frameworks": skills_frameworks,
        "skills_databases": skills_databases,
        "skills_ai": skills_ai,
        "skills_tools": skills_tools,
        "experience": experience_context,
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
