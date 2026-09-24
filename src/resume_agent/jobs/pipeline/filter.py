import re
from typing import Tuple

INCLUDE_REGEX = re.compile(
    r"\b(intern|internship|trainee|graduate|campus|entry.?level|fresher|new.?grad|"
    r"sde.?[01]|associate (software )?engineer|junior|apprentice|fellow|fellowship|student)\b",
    re.IGNORECASE
)

EXCLUDE_REGEX = re.compile(
    r"\b(senior|sr\b|staff|principal|lead|manager|director|architect|head of|"
    r"[3-9]\+?\s*years?|1[0-9]\+?\s*years?)\b",
    re.IGNORECASE
)

NON_TECH_EXCLUSIONS = re.compile(
    r"\b(accounting|accountant|recruitment|recruiter|talent acquisition|hr\b|human resources|"
    r"legal|paralegal|tax|brokerage|underwriting|real estate|nurse|medical|clinical|"
    r"video editor|youtube|social media|content creator|copywriter|sales|business development|"
    r"marketing|growth marketing|finance|financial|investment|fraud|prediction market|"
    r"business operations|bizops|operations associate|workplace experience|facilities|office manager|executive assistant)\b",
    re.IGNORECASE
)

TECH_ROLE_KEYWORDS = re.compile(
    r"\b(software|engineer|developer|data|ml\b|machine learning|ai\b|artificial intelligence|"
    r"systems|infra|backend|frontend|full.?stack|devops|security|quant|quantitative|algorithm|"
    r"computer science|research|deep learning|nlp|robotics|computational|sde|coding|programmer|"
    r"platform|cloud|distributed systems|embedded|firmware|qa|test|automation|sre|web|android|ios|mobile)\b",
    re.IGNORECASE
)

INDIA_LOCATIONS = {
    "india", "bangalore", "bengaluru", "hyderabad", "gurugram", "gurgaon",
    "mumbai", "delhi", "noida", "pune", "chennai", "kolkata", "ahmedabad", "remote"
}

NON_INDIA_RESTRICTIONS = re.compile(
    r"\b(us only|usa only|united states only|uk only|canada only|emea only|apac only|latin america)\b",
    re.IGNORECASE
)


def evaluate_job_filter(title: str, location: str, description: str) -> Tuple[bool, str]:
    """
    Evaluate whether a job listing is suitable for an internship / entry-level candidate in India.
    Returns (passed: bool, reason: str).
    """
    title_lower = title.lower()
    loc_lower = location.lower()
    desc_preview = description[:1500].lower()

    # 1. Check strict title exclusions
    exclude_match = EXCLUDE_REGEX.search(title_lower)
    if exclude_match:
        return False, f"Title contains excluded term: '{exclude_match.group(0)}'"

    # Check non-technical exclusions (accounting, recruiter, hr, etc.) unless tech role keyword present
    if NON_TECH_EXCLUSIONS.search(title_lower) and not TECH_ROLE_KEYWORDS.search(title_lower):
        return False, "Title matches non-technical role exclusion pattern"

    # 2. Check title or preview inclusions
    include_match = INCLUDE_REGEX.search(title_lower)
    if not include_match:
        # Also check first 500 chars of description if title is ambiguous (e.g. "Software Engineer - Campus 2028")
        include_match = INCLUDE_REGEX.search(desc_preview[:500])
        if not include_match:
            return False, "Title does not match internship/entry-level patterns"

    # 2.5 Must be a technical role (software, engineering, data, AI, systems, devops, quant)
    is_tech_role = bool(TECH_ROLE_KEYWORDS.search(title_lower) or TECH_ROLE_KEYWORDS.search(desc_preview[:500]))
    if not is_tech_role:
        return False, "Role is not technical (software/engineering/data/AI/systems)"

    # 3. Location filtering: check if in India or open Remote
    if NON_INDIA_RESTRICTIONS.search(loc_lower) or NON_INDIA_RESTRICTIONS.search(desc_preview[:500]):
        return False, "Location has geographic restriction outside India"

    is_india_or_remote = any(loc_token in loc_lower for loc_token in INDIA_LOCATIONS)
    # If location field is empty, default to passing if title matched
    if not is_india_or_remote and location.strip():
        # Check if country explicitly mentions non-India locations
        foreign_countries = ["united states", "usa", "germany", "japan", "france", "australia", "singapore", "brazil"]
        if any(fc in loc_lower for fc in foreign_countries):
            return False, f"Non-India physical location: {location}"

    return True, f"Matched pattern '{include_match.group(0)}'"
