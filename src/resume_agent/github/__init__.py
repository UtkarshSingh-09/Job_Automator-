"""
GitHub synchronization, deterministic quality scoring, and project corpus management.
"""

from resume_agent.github.client import GitHubClient
from resume_agent.github.scorer import compute_quality_score
from resume_agent.github.sync import sync_projects, get_all_projects, get_project_by_repo

__all__ = [
    "GitHubClient",
    "compute_quality_score",
    "sync_projects",
    "get_all_projects",
    "get_project_by_repo",
]
