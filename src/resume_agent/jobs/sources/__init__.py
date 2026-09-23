"""
ATS Source Adapters for job ingestion.
"""

from typing import Dict, Type
from resume_agent.jobs.sources.base import JobSourceAdapter
from resume_agent.jobs.sources.greenhouse import GreenhouseAdapter
from resume_agent.jobs.sources.lever import LeverAdapter
from resume_agent.jobs.sources.ashby import AshbyAdapter
from resume_agent.jobs.sources.workable import WorkableAdapter
from resume_agent.jobs.sources.workday import WorkdayAdapter

ADAPTER_REGISTRY: Dict[str, Type[JobSourceAdapter]] = {
    "greenhouse": GreenhouseAdapter,
    "lever": LeverAdapter,
    "ashby": AshbyAdapter,
    "workable": WorkableAdapter,
    "workday": WorkdayAdapter,
}

def get_adapter(provider: str) -> JobSourceAdapter | None:
    """Retrieve adapter instance for a given ATS provider."""
    cls = ADAPTER_REGISTRY.get(provider.lower())
    return cls() if cls else None
