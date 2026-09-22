import re
from typing import Dict, Any, List, Tuple, Set, Optional
from resume_agent.models import JobModel
from resume_agent.matcher.select import _load_skills_vocab


def extract_jd_keywords(job_text: str) -> Set[str]:
    """Extract recognized technical keywords present in the target Job Description."""
    if not job_text:
        return set()

    skills_vocab = _load_skills_vocab()
    job_lower = job_text.lower()
    matched = set()

    for skill in skills_vocab:
        # Match word boundary
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, job_lower):
            matched.add(skill.lower())

    return matched


def verify_keyword_coverage(
    pdf_text: str,
    job: Optional[JobModel] = None,
    min_coverage_pct: float = 80.0
) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Gate 6: Keyword Coverage Verification.
    Calculates the proportion of relevant technical keywords requested in the target JD
    that are explicitly present in the generated resume PDF.
    
    Returns:
        (is_pass: bool, details: Dict[str, Any], violations: List[str])
    """
    violations = []
    resume_lower = pdf_text.lower()

    if not job or not job.description_md:
        # If no target job provided, return neutral pass with baseline stats
        return True, {
            "jd_keyword_count": 0,
            "found_terms": [],
            "missing_terms": [],
            "coverage_score": 100.0,
            "threshold_pct": min_coverage_pct,
        }, []

    jd_keywords = extract_jd_keywords(job.description_md)

    if not jd_keywords:
        # No recognized technical keywords in JD snippet
        return True, {
            "jd_keyword_count": 0,
            "found_terms": [],
            "missing_terms": [],
            "coverage_score": 100.0,
            "threshold_pct": min_coverage_pct,
        }, []

    # Alias synonyms to allow standard technical equivalents
    synonyms = {
        "go": ["go", "golang"],
        "golang": ["go", "golang"],
        "javascript": ["javascript", "js"],
        "typescript": ["typescript", "ts"],
        "postgres": ["postgresql", "postgres"],
        "postgresql": ["postgresql", "postgres"],
        "rest": ["rest", "restful", "rest api", "restful apis", "apis", "api"],
        "rest api": ["rest", "restful", "rest api", "restful apis", "apis", "api"],
        "k8s": ["k8s", "kubernetes"],
        "kubernetes": ["k8s", "kubernetes"],
        "aws": ["aws", "amazon web services", "cloud"],
        "gcp": ["gcp", "google cloud"],
        "ci/cd": ["ci/cd", "github actions", "ci", "cd"],
        "sql": ["sql", "postgresql", "postgres", "sqlite", "mysql"],
        "c": ["c", "c++"],
        "c++": ["c++", "cpp"],
    }

    found = []
    missing = []

    for term in sorted(jd_keywords):
        term_patterns = synonyms.get(term, [term])
        is_found = False
        for alt in term_patterns:
            pattern = r"\b" + re.escape(alt) + r"\b"
            if re.search(pattern, resume_lower):
                is_found = True
                break

        if is_found:
            found.append(term)
        else:
            missing.append(term)

    coverage_score = (len(found) / len(jd_keywords)) * 100.0

    # For small keyword sets (<= 3 keywords, often Boolean OR options like Java/Go/JS),
    # matching at least 1 or 2 core options is compliant (threshold 50.0%)
    effective_threshold = 50.0 if len(jd_keywords) <= 3 else min_coverage_pct
    is_pass = coverage_score >= effective_threshold
    if not is_pass:
        violations.append(
            f"Gate 6: Keyword coverage {coverage_score:.1f}% is below threshold {effective_threshold:.1f}%. "
            f"Missing keywords: {', '.join(missing[:5])}"
        )

    details = {
        "jd_keyword_count": len(jd_keywords),
        "found_terms_count": len(found),
        "missing_terms_count": len(missing),
        "coverage_score": round(coverage_score, 1),
        "threshold_pct": effective_threshold,
        "found_terms": sorted(found),
        "missing_terms": sorted(missing),
    }

    return is_pass, details, violations
