"""
Auto-Apply Engine (Phase 10).
Supports Tier 1 Direct ATS API submissions (Greenhouse, Lever)
and Tier 2 Headless Browser Automation (Playwright Chromium)
with non-negotiable safety guardrails (cooldown, daily circuit breaker, zero CAPTCHA solving).
"""
from resume_agent.apply.models import ApplyResult, CandidateSubmissionPayload
from resume_agent.apply.api_submit import submit_via_api, detect_api_provider
from resume_agent.apply.browser_submit import submit_via_browser
from resume_agent.apply.manager import ApplyManager

__all__ = [
    "ApplyResult",
    "CandidateSubmissionPayload",
    "submit_via_api",
    "detect_api_provider",
    "submit_via_browser",
    "ApplyManager",
]
