import re
from typing import List, Tuple, Set, Optional
from resume_agent.models import ProjectModel
from resume_agent.matcher.select import _load_skills_vocab


def _strip_markdown(text: str) -> str:
    """Strip markdown bolding and inline code formatting for clean lexical validation."""
    t = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    t = re.sub(r"`(.*?)`", r"\1", text)
    return t


def verify_bullets(
    bullets: List[str],
    project: ProjectModel,
    min_words: int = 14,
    max_words: int = 26
) -> Tuple[bool, List[str]]:
    """
    Programmatic anti-hallucination and formatting verification suite.
    Enforces that:
    1. Exactly 3 bullets are provided.
    2. Word counts are within [14, 26] words (excluding markdown asterisks).
    3. First 4 Words Rule: Starts with strong technical active verb; rejects weak starters.
    4. No first-person pronouns ('I', 'me', 'my', 'we', 'our').
    5. Numeric figures, percentages, and latency metrics appear in project truth.
    6. Technical framework/tool terms are grounded in the project corpus.
    
    Returns:
        (is_valid: bool, violations: List[str])
    """
    violations = []

    # 1. Check bullet count
    if not isinstance(bullets, list) or len(bullets) != 3:
        violations.append(f"Expected exactly 3 bullets, got {len(bullets) if isinstance(bullets, list) else 0}")
        return False, violations

    # Assemble ground truth text (lowercased)
    truth_parts = [
        project.display_name or "",
        project.repo_name or "",
        project.description or "",
        project.manual_notes or "",
        project.readme_md or "",
        " ".join(project.languages),
        " ".join(project.topics),
    ]
    ground_truth_lower = " ".join(truth_parts).lower()
    norm_truth = ground_truth_lower.replace(" ", "").replace(",", "").replace("$", "").replace("~", "")

    skills_vocab = set(s.lower() for s in _load_skills_vocab())

    first_person_pattern = re.compile(r"\b(i|me|my|we|our|us)\b", re.IGNORECASE)
    weak_starters = [
        "assisted", "helped", "worked on", "responsible for", "participated in",
        "collaborated", "supported", "contributed to", "involved in"
    ]
    metric_pattern = re.compile(
        r"(~?\d+(?:\.\d+)?%|\b\d+x\b|~?\d+\s*(?:ms|s|µs|fps|rpm|qps|rps|tps)|\$\d+(?:,\d+)?|\b\d+\s*(?:days|weeks|months|seconds)\b)",
        re.IGNORECASE
    )

    # Acronym synonyms allowed if primary is grounded
    synonym_aliases = {
        "postgres": "postgresql",
        "rest": "restful",
        "k8s": "kubernetes",
        "ci/cd": "github actions",
    }

    for idx, raw_bullet in enumerate(bullets, 1):
        clean_bullet = _strip_markdown(raw_bullet.strip()).rstrip(".").strip()
        words = clean_bullet.split()
        word_count = len(words)

        # 2. Check word count
        if word_count < min_words or word_count > max_words:
            violations.append(
                f"Bullet #{idx} has {word_count} words (must be between {min_words} and {max_words}): '{clean_bullet[:40]}...'"
            )

        # 3. Check First 4 Words Rule (anti-weak starter)
        bullet_start = clean_bullet.lower()
        for ws in weak_starters:
            if bullet_start.startswith(ws):
                violations.append(
                    f"Bullet #{idx} starts with weak phrasing '{ws}'. Enforce Google X-Y-Z formula with strong active verb."
                )

        # 4. Check first-person pronouns
        fp_match = first_person_pattern.search(clean_bullet)
        if fp_match:
            violations.append(f"Bullet #{idx} contains first-person pronoun '{fp_match.group(0)}'")

        # 5. Check metrics (percentages, speedups, latencies, prizes)
        for metric_m in metric_pattern.finditer(clean_bullet):
            metric_raw = metric_m.group(0).lower()
            metric_norm = metric_raw.replace(" ", "").replace(",", "").replace("$", "").replace("~", "")
            if metric_norm not in norm_truth:
                violations.append(
                    f"Bullet #{idx} contains ungrounded metric '{metric_m.group(0)}' not found in project truth"
                )

        # 6. Check technical skill terms (anti-hallucination)
        bullet_lower = clean_bullet.lower()
        for skill in skills_vocab:
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, bullet_lower):
                # Check if skill or its known alias is in truth
                grounded = bool(re.search(pattern, ground_truth_lower))
                if not grounded and skill in synonym_aliases:
                    alias = synonym_aliases[skill]
                    grounded = bool(re.search(r"\b" + re.escape(alias) + r"\b", ground_truth_lower))

                if not grounded:
                    violations.append(
                        f"Bullet #{idx} introduces hallucinated technology '{skill}' not in project truth"
                    )

    is_valid = len(violations) == 0
    return is_valid, violations
