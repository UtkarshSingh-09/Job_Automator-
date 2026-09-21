import re
from typing import List, Tuple, Set, Optional
from resume_agent.models import ProjectModel
from resume_agent.matcher.select import _load_skills_vocab


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
    2. Word counts are within [14, 26] words.
    3. No first-person pronouns ('I', 'me', 'my', 'we', 'our').
    4. Numeric figures, percentages, and latency metrics appear verbatim in project truth.
    5. Technical framework/tool terms are grounded in the project corpus.
    
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
    ground_truth_raw = " ".join(truth_parts)

    skills_vocab = set(s.lower() for s in _load_skills_vocab())

    first_person_pattern = re.compile(r"\b(i|me|my|we|our|us)\b", re.IGNORECASE)
    metric_pattern = re.compile(r"\b(\d+(\.\d+)?%|\d+x|\d+\s*(?:ms|s|µs|fps|rpm|qps|rps|tps))\b", re.IGNORECASE)
    large_number_pattern = re.compile(r"\b\d{2,}\b")

    for idx, bullet in enumerate(bullets, 1):
        clean_bullet = bullet.strip().rstrip(".").strip()
        words = clean_bullet.split()
        word_count = len(words)

        # 2. Check word count
        if word_count < min_words or word_count > max_words:
            violations.append(
                f"Bullet #{idx} has {word_count} words (must be between {min_words} and {max_words}): '{clean_bullet[:40]}...'"
            )

        # 3. Check first-person pronouns
        fp_match = first_person_pattern.search(clean_bullet)
        if fp_match:
            violations.append(f"Bullet #{idx} contains first-person pronoun '{fp_match.group(0)}'")

        # 4. Check metrics (percentages, speedups, latencies)
        for metric_m in metric_pattern.finditer(clean_bullet):
            metric_str = metric_m.group(0).lower().replace(" ", "")
            # Verify metric appears in ground truth
            norm_truth = ground_truth_lower.replace(" ", "")
            if metric_str not in norm_truth:
                violations.append(
                    f"Bullet #{idx} contains ungrounded metric '{metric_m.group(0)}' not found in project truth"
                )

        # 5. Check technical skill terms (anti-hallucination)
        bullet_lower = clean_bullet.lower()
        for skill in skills_vocab:
            # Check if this skill keyword is mentioned in the bullet
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, bullet_lower):
                # Check if it was in the project ground truth
                if not re.search(pattern, ground_truth_lower):
                    violations.append(
                        f"Bullet #{idx} introduces hallucinated technology '{skill}' not in project truth"
                    )

    is_valid = len(violations) == 0
    return is_valid, violations
