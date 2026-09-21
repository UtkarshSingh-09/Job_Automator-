from typing import List, Tuple, Dict
import numpy as np

from resume_agent.models import ProjectModel, JobModel
from resume_agent.github.sync import get_all_projects
from resume_agent.matcher.embed import (
    build_job_embedding_text,
    embed_text,
    get_or_compute_project_embeddings,
)
from resume_agent.logging import logger


def retrieve_top_candidates(
    job: JobModel,
    top_k: int = 8,
    p1_bonus: float = 0.15
) -> List[Tuple[ProjectModel, float]]:
    """
    Retrieve Top-K candidate projects for a target job posting using vectorized cosine similarity.
    Applies priority tier weighting to ensure candidate's flagship verified projects (P1)
    are present in the consideration pool when technically relevant.
    
    Returns:
        List of tuples: (ProjectModel, cosine_similarity) sorted by match score descending.
    """
    # 1. Encode job description
    job_text = build_job_embedding_text(job)
    job_vec = embed_text(job_text)
    job_norm = np.linalg.norm(job_vec)
    if job_norm > 0:
        job_vec = job_vec / job_norm

    # 2. Get project embeddings map and project objects
    embeddings_map = get_or_compute_project_embeddings()
    projects = get_all_projects()
    projects_by_id: Dict[int, ProjectModel] = {p.id: p for p in projects if p.id is not None}

    scored_candidates = []

    for proj_id, proj_vec in embeddings_map.items():
        project = projects_by_id.get(proj_id)
        if not project:
            continue

        p_norm = np.linalg.norm(proj_vec)
        if p_norm > 0:
            proj_vec = proj_vec / p_norm

        # Raw cosine similarity [-1.0, 1.0]
        raw_sim = float(np.dot(job_vec, proj_vec))

        # Adjusted ranking score with candidate priority boost
        adjusted_score = raw_sim
        if project.priority == 1:
            adjusted_score += p1_bonus
        elif project.quality_score >= 80:
            adjusted_score += 0.05

        scored_candidates.append((project, raw_sim, adjusted_score))

    # 3. Sort by adjusted score descending
    scored_candidates.sort(key=lambda x: x[2], reverse=True)

    # 4. Take top K
    top_results = [(proj, raw_sim) for proj, raw_sim, _ in scored_candidates[:top_k]]
    logger.debug(f"Retrieved top {len(top_results)} candidate projects for Job '{job.title}' ({job.company_name})")

    return top_results
