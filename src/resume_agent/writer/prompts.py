from typing import Dict, Any
from resume_agent.models import ProjectModel, JobModel


SYSTEM_PROMPT = """You are an elite technical resume writer for Utkarsh Singh, a B.Tech Computer Science undergraduate at SRM University Amaravati (CGPA 8.78/10.0, Grad 2028).
Your job is to rewrite 3 resume bullets for ONE specific project to best match a target Job Description (JD).

GROUNDING CONTRACT (STRICT RULES — VIOLATING ANY IS AN AUTOMATIC FAILURE):
1. ZERO HALLUCINATIONS: Every technology, tool, database, framework, library, protocol, and numeric metric (speedup, reduction percentage, latency, throughput, scale) MUST appear verbatim or directly in the SOURCE OF TRUTH below. NEVER introduce or invent any technology or metric not present in the project truth.
2. MISSING TECH: If the target JD requests a technology that this project did NOT use (e.g. Kubernetes, AWS Redshift, Spark), do NOT add it to the bullets. Report it in the "unmet" list instead.
3. ALIGNMENT & VOCABULARY: You MAY reorder, rephrase, and highlight project aspects using the target JD's terminology (e.g., if JD emphasizes 'financial infrastructure reliability' and project is a payment engine, highlight idempotency and transaction consistency).
4. ACTION ORIENTATION: Use past-tense, strong active verbs (Engineered, Architected, Implemented, Benchmarked, Streamlined, Optimized). Never use first-person pronouns ("I", "my", "we"). Omit droppable articles ("the", "a", "an") where natural.
5. BULLET CONSTRAINTS: Produce EXACTLY 3 bullets. Each bullet MUST be between 14 and 26 words in length.
6. JSON ONLY: Output valid JSON only matching the schema below, without markdown formatting or commentary.

SCHEMA:
{
  "bullets": [
    "<Action verb> <what was built/optimized> utilizing <verifiable tech>, achieving <verifiable metric/outcome>.",
    "<Action verb> <architecture/system mechanism> with <verifiable tech>, handling <verifiable feature>.",
    "<Action verb> <component/integration> using <verifiable tech>, ensuring <verifiable reliability/compliance>."
  ],
  "tech_used": ["<tech1>", "<tech2>", "<tech3>"],
  "unmet": ["<jd_requirement_not_in_project>"]
}
"""


def build_bullet_prompt(project: ProjectModel, job: JobModel) -> str:
    """Construct structured user prompt containing target JD and project ground truth."""
    name = project.display_name or project.repo_name

    source_of_truth = [
        f"PROJECT NAME: {name} (Repository: {project.repo_name})",
        f"PRIMARY LANGUAGE: {project.primary_language or 'N/A'}",
        f"KNOWN TECHNOLOGIES: {', '.join(project.languages)}",
        f"TOPICS: {', '.join(project.topics)}",
    ]

    if project.manual_notes:
        source_of_truth.append(f"VERIFIED MANUAL HIGHLIGHTS & METRICS:\n{project.manual_notes}")

    if project.description:
        source_of_truth.append(f"DESCRIPTION:\n{project.description}")

    if project.readme_md:
        source_of_truth.append(f"README EXCERPT:\n{project.readme_md[:1500]}")

    jd_snippet = [
        f"TARGET COMPANY: {job.company_name}",
        f"TARGET ROLE: {job.title}",
        f"LOCATION: {job.location or 'N/A'} (Remote: {job.remote_type or 'onsite'})",
        f"JOB DESCRIPTION SNIPPET:\n{job.description_md[:2000]}",
    ]

    return (
        f"TARGET JOB DESCRIPTION:\n"
        f"{chr(10).join(jd_snippet)}\n\n"
        f"==================================================\n"
        f"SOURCE OF TRUTH (ONLY FACTS YOU MAY USE):\n"
        f"{chr(10).join(source_of_truth)}\n\n"
        f"==================================================\n"
        f"Generate exactly 3 grounded bullets (14-26 words each) for {name}. Output JSON only."
    )
