"""
Applicant Tracking System (ATS) detection, signature parsing, and endpoint validation.
"""

from resume_agent.jobs.discovery.patterns import ATS_SIGNATURES
from resume_agent.jobs.discovery.validator import validate_ats_slug
from resume_agent.jobs.discovery.detector import detect_ats

__all__ = [
    "ATS_SIGNATURES",
    "validate_ats_slug",
    "detect_ats",
]
