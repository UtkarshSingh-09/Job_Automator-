import json
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import yaml

from resume_agent.config import get_settings
from resume_agent.db import get_db
from resume_agent.models import ProjectModel, JobModel, MatchModel
from resume_agent.matcher.client import LLMClient
from resume_agent.logging import logger


def select_projects_and_score(
    job: JobModel,
    candidates: List[Tuple[ProjectModel, float]]
) -> MatchModel:
    """
    Stage B selection & fit scoring:
    Evaluates Top-8 retrieved projects against target job description.
    Uses OpenRouter (DeepSeek V3 / Llama / Claude) if configured,
    or falls back to an intelligent deterministic ranker.
    Saves and returns MatchModel.
    """
    client = LLMClient()
    match_data: Optional[Dict[str, Any]] = None

    if client.is_configured:
        logger.info(f"Running LLM evaluation for Job #{job.id} '{job.title}' via {client.settings.llm_model}...")
        match_data = _evaluate_with_llm(client, job, candidates)

    if not match_data:
        logger.info(f"Using deterministic ranker for Job #{job.id} '{job.title}'")
        match_data = _evaluate_deterministically(job, candidates)

    # Persist match result to SQLite
    match_model = _save_match_to_db(job.id, match_data)
    return match_model


def _evaluate_with_llm(
    client: LLMClient,
    job: JobModel,
    candidates: List[Tuple[ProjectModel, float]]
) -> Optional[Dict[str, Any]]:
    """Stage B evaluation via OpenRouter LLM."""
    system_prompt = (
        "You are an expert technical recruiter and resume strategist for Utkarsh Singh, "
        "a B.Tech Computer Science undergraduate at SRM University Amaravati (CGPA 8.78/10.0, Grad 2028). "
        "Your task is to analyze a target job description and select the EXACTLY 3 BEST projects "
        "from the candidate's 8 retrieved technical projects.\n\n"
        "SELECTION CRITERIA:\n"
        "- Rank 1: Primary flagship technical match (strongest overlap with core JD requirements).\n"
        "- Rank 2: Strong supporting systems or backend match demonstrating production engineering depth.\n"
        "- Rank 3: Breadth or complementary engineering match.\n"
        "- Priority 1 projects (MerchantMind, Trinetra, RudraKernel, Aegis Forge) have verified real-world metrics.\n\n"
        "RESPONSE FORMAT: Return valid JSON ONLY matching this exact schema:\n"
        "{\n"
        '  "overall_fit": <integer 0-100>,\n'
        '  "recommend_apply": <boolean, true if overall_fit >= 55>,\n'
        '  "reasoning": "<concise 2-sentence explanation of candidate fit for this role>",\n'
        '  "selected": [\n'
        "    {\n"
        '      "project_id": <int>,\n'
        '      "repo_name": "<string>",\n'
        '      "display_name": "<string>",\n'
        '      "rank": <1, 2, or 3>,\n'
        '      "why": "<specific rationale linking this project to JD requirements>",\n'
        '      "jd_requirements_covered": ["<skill1>", "<skill2>"]\n'
        "    }\n"
        "  ],\n"
        '  "uncovered_requirements": ["<requirement1 not met by candidate>", ...]\n'
        "}"
    )

    candidates_text = []
    for idx, (p, sim) in enumerate(candidates, 1):
        name = p.display_name or p.repo_name
        p_info = (
            f"Candidate #{idx} [ID: {p.id}]: {name} (P{p.priority}, Sim: {sim:.2f})\n"
            f"- Tech: {', '.join(p.languages[:6])} | Quality: {p.quality_score}/100\n"
            f"- Summary: {(p.manual_notes or p.description or 'N/A')[:180]}\n"
        )
        candidates_text.append(p_info)

    user_prompt = (
        f"TARGET JOB POSTING:\n"
        f"Company: {job.company_name} | Role: {job.title}\n"
        f"Location: {job.location} | Remote: {job.remote_type}\n\n"
        f"Job Description:\n{job.description_md[:1000]}\n\n"
        f"CANDIDATE'S RETRIEVED PROJECTS:\n"
        f"{''.join(candidates_text)}\n"
        f"Select the Top 3 projects and compute overall_fit (0-100). Return JSON only."
    )

    result = client.generate_json(system_prompt, user_prompt)
    if not result or "selected" not in result or len(result["selected"]) != 3:
        logger.warning(f"LLM output invalid or did not contain 3 selected projects: {result}")
        return None

    return result


def _evaluate_deterministically(
    job: JobModel,
    candidates: List[Tuple[ProjectModel, float]]
) -> Dict[str, Any]:
    """Deterministic fallback ranker when LLM API is offline or unconfigured."""
    skills_vocab = _load_skills_vocab()
    jd_lower = f"{job.title} {job.description_md}".lower()

    # Extract tech terms present in JD
    jd_skills = set()
    for skill in skills_vocab:
        if re.search(r"\b" + re.escape(skill) + r"\b", jd_lower):
            jd_skills.add(skill)

    # Score each candidate project on skill overlap + cosine sim
    project_scores = []
    for p, sim in candidates:
        proj_tech = set(l.lower() for l in p.languages)
        for t in p.topics:
            t_clean = t.lower()
            proj_tech.add(t_clean)
            proj_tech.add(t_clean.replace("-", " "))
            for sub in t_clean.split("-"):
                if len(sub) > 2:
                    proj_tech.add(sub)
        if p.primary_language:
            proj_tech.add(p.primary_language.lower())
        overlap = list(proj_tech.intersection(jd_skills))

        # Composite score
        score = sim * 50.0 + len(overlap) * 5.0
        if p.priority == 1:
            score += 15.0
        if p.quality_score >= 80:
            score += 5.0

        project_scores.append((p, sim, overlap, score))

    project_scores.sort(key=lambda x: x[3], reverse=True)
    top_3 = project_scores[:3]

    # Calculate overall fit (0-100)
    avg_sim = sum(sim for _, sim, _, _ in top_3) / max(1, len(top_3))
    covered_all = set()
    for _, _, overlap, _ in top_3:
        covered_all.update(overlap)

    # Scale fit score into 0-100
    sim_component = min(75.0, avg_sim * 85.0)
    tech_component = min(15.0, len(covered_all) * 3.0)
    flagship_bonus = 10.0 if any(p.priority == 1 for p, _, _, _ in top_3) else 0.0
    base_fit = min(96.0, max(50.0, sim_component + tech_component + flagship_bonus))
    overall_fit = round(base_fit, 1)
    uncovered = [s for s in list(jd_skills)[:5] if s not in covered_all]

    selected_list = []
    for rank, (p, sim, overlap, _) in enumerate(top_3, 1):
        name = p.display_name or p.repo_name
        covered_display = [o.capitalize() for o in overlap[:4]] or [p.primary_language or "Engineering"]
        selected_list.append({
            "project_id": p.id,
            "repo_name": p.repo_name,
            "display_name": name,
            "rank": rank,
            "why": f"Rank {rank} match for {job.company_name} with {round(sim, 2)} cosine similarity and verified technical depth.",
            "jd_requirements_covered": covered_display,
        })

    reasoning = (
        f"Candidate exhibits strong alignment ({overall_fit}/100) with {job.company_name} "
        f"across core skills: {', '.join(list(covered_all)[:4]) or 'Computer Science Fundamentals'}."
    )

    return {
        "overall_fit": overall_fit,
        "recommend_apply": overall_fit >= 55.0,
        "reasoning": reasoning,
        "selected": selected_list,
        "uncovered_requirements": uncovered,
    }


def _save_match_to_db(job_id: int, match_data: Dict[str, Any]) -> MatchModel:
    """Upsert match record into SQLite matches table."""
    overall_fit = float(match_data.get("overall_fit", 0.0))
    selected_json = json.dumps(match_data.get("selected", []))
    reasoning = match_data.get("reasoning", "")
    uncovered_json = json.dumps(match_data.get("uncovered_requirements", []))

    sql = """
    INSERT INTO matches (
        job_id, overall_fit, selected_projects_json, selection_reasoning,
        uncovered_requirements_json, created_at
    ) VALUES (
        :job_id, :overall_fit, :selected_projects_json, :selection_reasoning,
        :uncovered_requirements_json, CURRENT_TIMESTAMP
    )
    ON CONFLICT(job_id) DO UPDATE SET
        overall_fit = excluded.overall_fit,
        selected_projects_json = excluded.selected_projects_json,
        selection_reasoning = excluded.selection_reasoning,
        uncovered_requirements_json = excluded.uncovered_requirements_json,
        created_at = CURRENT_TIMESTAMP;
    """

    with get_db() as conn:
        conn.execute(sql, {
            "job_id": job_id,
            "overall_fit": overall_fit,
            "selected_projects_json": selected_json,
            "selection_reasoning": reasoning,
            "uncovered_requirements_json": uncovered_json,
        })
        row = conn.execute("SELECT * FROM matches WHERE job_id = ?;", (job_id,)).fetchone()

        return MatchModel(
            id=row["id"],
            job_id=row["job_id"],
            overall_fit=row["overall_fit"],
            selected_projects=json.loads(row["selected_projects_json"] or "[]"),
            selection_reasoning=row["selection_reasoning"],
            uncovered_requirements=json.loads(row["uncovered_requirements_json"] or "[]"),
            created_at=row["created_at"],
        )


def _load_skills_vocab() -> List[str]:
    """Load flat list of technical skill keywords from data/gazetteer/skills.yaml."""
    settings = get_settings()
    candidate_paths = [
        settings.data_dir / "gazetteer" / "skills.yaml",
        settings.project_root / "data" / "gazetteer" / "skills.yaml",
        Path("/app/data/gazetteer/skills.yaml"),
        Path("/app/seed_gazetteer/skills.yaml"),
        Path(__file__).resolve().parent.parent.parent.parent / "data" / "gazetteer" / "skills.yaml",
    ]

    skills_path = None
    for p in candidate_paths:
        if p.exists():
            skills_path = p
            break

    if not skills_path:
        return ["python", "c++", "fastapi", "docker", "sql", "linux", "git", "rest api", "quantitative", "trading"]

    try:
        with open(skills_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            flat = []
            if isinstance(data, dict):
                for cat, items in data.items():
                    if isinstance(items, list):
                        flat.extend([str(i).lower() for i in items])
            return flat
    except Exception:
        return ["python", "c++", "fastapi", "docker", "sql", "linux", "git", "quantitative", "trading"]
