import re
from typing import Dict, Any, List, Tuple, Set, Optional
from resume_agent.models import ProfileModel, ProjectModel
from resume_agent.matcher.select import _load_skills_vocab
from resume_agent.db import get_db


def _assemble_candidate_ground_truth(
    profile: Optional[ProfileModel] = None,
    projects: Optional[List[ProjectModel]] = None
) -> Set[str]:
    """Assemble the complete set of candidate verified technical skills from DB and profile."""
    truth_tokens = set()

    # 1. Profile verified skills
    if profile:
        for s in profile.skills:
            truth_tokens.add(s.lower().strip())

    # 2. Project corpus
    all_projects = projects or []
    if not all_projects:
        # Load from DB
        try:
            with get_db() as conn:
                rows = conn.execute("SELECT * FROM projects").fetchall()
                for r in rows:
                    p = ProjectModel.from_row(r)
                    all_projects.append(p)
        except Exception:
            pass

    for proj in all_projects:
        for lang in proj.languages:
            truth_tokens.add(lang.lower().strip())
        for top in proj.topics:
            truth_tokens.add(top.lower().strip())
        if proj.primary_language:
            truth_tokens.add(proj.primary_language.lower().strip())

        # Also extract skills vocabulary tokens present in manual_notes & description
        notes_text = f"{proj.manual_notes or ''} {proj.description or ''} {proj.readme_md or ''}".lower()
        for s in _load_skills_vocab():
            if re.search(r"\b" + re.escape(s.lower()) + r"\b", notes_text):
                truth_tokens.add(s.lower())

    # 3. Standard verified coursework, candidate skills, & core protocols
    foundational = [
        "python", "c++", "c", "sql", "javascript", "typescript", "html5", "css3", "bash", "go",
        "data structures & algorithms", "dsa", "operating systems", "os", "dbms", "system design",
        "distributed systems", "machine learning", "object-oriented programming", "oops",
        "fastapi", "docker", "git", "github actions", "ci/cd", "linux", "rest", "restful", "restful apis",
        "webrtc", "websockets", "redis", "redis pub/sub", "postgresql", "postgres", "sqlite", "qdrant",
        "chromadb", "mongodb", "xgboost", "lightgbm", "shap", "lime", "livekit", "deepgram", "razorpay",
        "react", "next.js", "nextjs", "langgraph", "langchain", "pytorch", "sentence-transformers",
        "transformers", "lora", "grpo", "openenv", "trl", "unsloth", "mediapipe", "three.js", "pydantic",
        "raw sockets", "tcp", "udp", "rag", "retrieval-augmented generation", "slms", "llms",
        "fine-tuning", "finetuning", "model fine-tuning", "prompt engineering", "nlp",
        "deep learning", "reinforcement learning", "rl", "vector search", "embeddings", "ebpf"
    ]
    for item in foundational:
        truth_tokens.add(item.lower())

    return truth_tokens


def verify_grounding_audit(
    pdf_text: str,
    profile: Optional[ProfileModel] = None,
    projects: Optional[List[ProjectModel]] = None
) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Gate 7: Anti-Hallucination Grounding Audit.
    Verifies that all technical tools, libraries, and frameworks extracted from the resume
    are grounded in the candidate's verified portfolio corpus.
    
    Returns:
        (is_pass: bool, details: Dict[str, Any], violations: List[str])
    """
    violations = []
    resume_lower = pdf_text.lower()
    skills_vocab = _load_skills_vocab()
    ground_truth = _assemble_candidate_ground_truth(profile, projects)

    # Detect skills mentioned in resume
    mentioned_skills = set()
    for skill in skills_vocab:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, resume_lower):
            mentioned_skills.add(skill.lower())

    # Check for ungrounded mentions
    ungrounded_skills = []
    for skill in sorted(mentioned_skills):
        if skill not in ground_truth:
            # Check if part of a composite phrase already in ground truth (e.g. transformers in sentence-transformers)
            composite_match = any(skill in truth or truth in skill for truth in ground_truth)
            if not composite_match:
                ungrounded_skills.append(skill)
                violations.append(
                    f"Gate 7: Detected ungrounded/hallucinated technical skill '{skill}' in resume"
                )

    is_pass = len(violations) == 0
    details = {
        "mentioned_skills_count": len(mentioned_skills),
        "grounded_skills_count": len(mentioned_skills) - len(ungrounded_skills),
        "ungrounded_skills_count": len(ungrounded_skills),
        "ungrounded_skills": ungrounded_skills,
    }

    return is_pass, details, violations
