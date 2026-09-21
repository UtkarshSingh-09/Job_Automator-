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

    # 2. Check title or preview inclusions
    include_match = INCLUDE_REGEX.search(title_lower)
    if not include_match:
        # Also check first 500 chars of description if title is ambiguous (e.g. "Software Engineer - Campus 2028")
        include_match = INCLUDE_REGEX.search(desc_preview[:500])
        if not include_match:
            return False, "Title does not match internship/entry-level patterns"

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
