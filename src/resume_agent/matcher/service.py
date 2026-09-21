import json
from typing import List, Optional, Dict, Any
from resume_agent.db import get_db
from resume_agent.models import MatchModel, JobModel
from resume_agent.jobs.service import get_job_by_id
from resume_agent.matcher.retrieve import retrieve_top_candidates
from resume_agent.matcher.select import select_projects_and_score
from resume_agent.logging import logger


def match_job(job_id: int) -> Optional[MatchModel]:
    """
    Execute full two-stage semantic matching pipeline for a target job listing.
    Stage A: Local BGE-small dense vector cosine similarity (Top 8 candidates).
    Stage B: LLM / deterministic project selection (Top 3 projects + fit score 0-100).
    """
    job = get_job_by_id(job_id)
    if not job:
        logger.warning(f"Job with ID {job_id} not found in database.")
        return None

    logger.info(f"Starting semantic match for Job #{job.id} at {job.company_name}: '{job.title}'...")

    # Stage A: Vector retrieval
    candidates = retrieve_top_candidates(job, top_k=8)
    if not candidates:
        logger.warning(f"No candidate projects retrieved for Job #{job_id}")
        return None

    # Stage B: Selection & scoring
    match_result = select_projects_and_score(job, candidates)
    logger.info(
        f"Match complete for Job #{job.id} - Overall Fit: {match_result.overall_fit}/100"
    )
    return match_result


def match_all_jobs(min_fit: float = 55.0, limit: int = 20) -> List[MatchModel]:
    """
    Batch match active listings that passed the internship filter and do not yet have a match record.
    """
    query = """
    SELECT id FROM jobs 
    WHERE passed_filter = 1 
      AND id NOT IN (SELECT job_id FROM matches)
    ORDER BY id DESC
    LIMIT ?;
    """
    with get_db() as conn:
        rows = conn.execute(query, (limit,)).fetchall()
        job_ids = [r["id"] for r in rows]

    logger.info(f"Found {len(job_ids)} unmatched passed jobs to process (limit={limit}).")

    matches = []
    for jid in job_ids:
        try:
            m = match_job(jid)
            if m:
                matches.append(m)
        except Exception as e:
            logger.error(f"Error matching job #{jid}: {e}")

    return matches


def get_matches(min_fit: float = 0.0, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Retrieve stored match records joined with company and job details.
    """
    query = """
    SELECT 
        m.id AS match_id,
        m.job_id,
        m.overall_fit,
        m.selected_projects_json,
        m.selection_reasoning,
        m.uncovered_requirements_json,
        m.created_at,
        j.company_name,
        j.title AS job_title,
        j.location,
        j.apply_url
    FROM matches m
    JOIN jobs j ON m.job_id = j.id
    WHERE m.overall_fit >= ?
    ORDER BY m.overall_fit DESC, m.created_at DESC
    LIMIT ?;
    """
    with get_db() as conn:
        rows = conn.execute(query, (min_fit, limit)).fetchall()
        results = []
        for r in rows:
            results.append({
                "match_id": r["match_id"],
                "job_id": r["job_id"],
                "company_name": r["company_name"],
                "job_title": r["job_title"],
                "location": r["location"],
                "apply_url": r["apply_url"],
                "overall_fit": r["overall_fit"],
                "selected_projects": json.loads(r["selected_projects_json"] or "[]"),
                "selection_reasoning": r["selection_reasoning"],
                "uncovered_requirements": json.loads(r["uncovered_requirements_json"] or "[]"),
                "created_at": r["created_at"],
            })
        return results
