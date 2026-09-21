from datetime import datetime, timezone
from typing import Dict, Any, Optional


def compute_quality_score(project_data: Dict[str, Any]) -> float:
    """
    Compute deterministic project quality score (0–100) per §4 (FR-02).
    
    Formula:
      Score = 25(README) + 20(commits) + 15(tests) + 10(CI) + 5(Docker) + 
              10(diversity) + 10(recency) + 5(stars)
    """
    score = 0.0

    # 1. README presence & substance (max 25 pts)
    readme = project_data.get("readme_md") or ""
    words = len(readme.split())
    if words > 500:
        score += 25.0
    elif words > 250:
        score += 20.0
    elif words > 100:
        score += 15.0
    elif words > 20:
        score += 5.0

    # 2. Commit count / depth of work (max 20 pts)
    commits = project_data.get("commit_count", 0)
    if commits >= 40:
        score += 20.0
    elif commits >= 25:
        score += 16.0
    elif commits >= 15:
        score += 12.0
    elif commits >= 5:
        score += 6.0

    # 3. Automated tests present (max 15 pts)
    if project_data.get("has_tests", False):
        score += 15.0

    # 4. CI/CD workflow configured (max 10 pts)
    if project_data.get("has_ci", False):
        score += 10.0

    # 5. Docker containerization (max 5 pts)
    if project_data.get("has_docker", False):
        score += 5.0

    # 6. Primary language & technical diversity (max 10 pts)
    langs = project_data.get("languages", [])
    if len(langs) >= 2 or project_data.get("primary_language"):
        score += 10.0

    # 7. Recency of code pushed (max 10 pts)
    pushed_at = project_data.get("pushed_at")
    if pushed_at:
        if isinstance(pushed_at, str):
            try:
                pushed_dt = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            except Exception:
                pushed_dt = None
        elif isinstance(pushed_dt, datetime):
            pushed_dt = pushed_at
        else:
            pushed_dt = None

        if pushed_dt:
            days_ago = (datetime.now(timezone.utc) - pushed_dt).days
            if days_ago <= 30:
                score += 10.0
            elif days_ago <= 90:
                score += 7.0
            elif days_ago <= 180:
                score += 4.0
    else:
        # Default recency bonus for newly curated portfolio projects
        score += 8.0

    # 8. GitHub stars / community validation (max 5 pts)
    stars = project_data.get("stars", 0)
    score += min(stars * 0.5, 5.0)

    # Clamp score to [0.0, 100.0]
    return round(max(0.0, min(100.0, score)), 1)
