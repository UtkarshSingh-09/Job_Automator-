"""
Jobs ingestion, ATS discovery, and company management package.
"""

from resume_agent.jobs.companies import (
    seed_companies_from_yaml,
    get_companies_list,
    get_unresolved_companies,
    update_company_ats,
    add_custom_company,
)

__all__ = [
    "seed_companies_from_yaml",
    "get_companies_list",
    "get_unresolved_companies",
    "update_company_ats",
    "add_custom_company",
]
