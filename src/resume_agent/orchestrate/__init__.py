"""
Orchestration package for automated end-to-end pipeline workflows.
Coordinates ingestion, matching, resume generation, ATS validation, and delivery.
"""
from resume_agent.orchestrate.daily import run_daily_pipeline

__all__ = ["run_daily_pipeline"]
