"""
Validation package for Applicant Tracking System (ATS) verification suite.
Exposes 7 mechanical verification gates and pipeline runner.
"""
from resume_agent.validate.runner import validate_resume_pdf, ValidationReport, GateResult

__all__ = ["validate_resume_pdf", "ValidationReport", "GateResult"]
