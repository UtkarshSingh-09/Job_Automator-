from typing import Dict, Any
from resume_agent.models import ProjectModel, JobModel


SYSTEM_PROMPT = """You are an elite technical resume writer for Utkarsh Singh, a B.Tech Computer Science undergraduate at SRM University Amaravati (CGPA 8.78 / 10.00, Expected Graduation Aug 2024 -- May 2028).
Your job is to rewrite 3 high-impact resume bullets for ONE specific project to best match a target Job Description (JD).

ATS & RECRUITER PSYCHOLOGY CONTRACT:
1. GOOGLE X-Y-Z BULLET FORMULA (MANDATORY):
   Structure every bullet strictly following Google's formula:
   "Accomplished [X] as measured by [Y], by doing [Z]"
   - [X] Concrete Action / Deliverable: What was built, engineered, or optimized? Must start with a strong past-tense active verb (e.g., Architected, Engineered, Implemented, Automated, Built, Optimized).
   - [Y] Quantitative Measurement: How was success measured? Latency (e.g., ~850ms, sub-650ms), speedup (e.g., 3-5 days to 60s, under 90s), test count (e.g., 151-test suite), scale (e.g., 200+ stores, 5,000+ products), prizes ($1,500 prize). All metrics MUST be grounded in the project truth.
   - [Z] Technical Implementation: Exact tools, protocols, algorithms, or architectural patterns used (e.g., LiveKit WebRTC, Deepgram Nova-3, PostgreSQL row locks, HMAC-SHA256 webhooks, Qdrant vector collections, XGBoost with SHAP/LIME).

2. RECRUITER 7.4-SECOND F-PATTERN & FIRST 4 WORDS RULE:
   - Recruiters scan the first 3-4 words of each bullet point along the left margin.
   - The first 4 words MUST communicate the primary technical action verb + technical deliverable (e.g., "Architected 6-agent real-time...", "Automated commercial credit underwriting...", "Engineered atomic 3-phase...").
   - NEVER start with weak or passive phrases ("Assisted in", "Helped with", "Worked on", "Responsible for", "Collaborated with", "Supported", "Participated in").

3. BOLDFACE HIGHLIGHTING FOR VISUAL SCAN RETENTION:
   - Wrap 1 to 2 key verified metrics or core technologies per bullet in markdown bold (**metric** or **technology**).
   - Example: "Architected a 6-agent real-time technical interview simulator achieving **~850ms voice latency** by orchestrating **LiveKit WebRTC** and Deepgram Nova-3 with FastAPI."
   - Example: "Automated commercial credit underwriting from **3--5 days to 60 seconds** by engineering a 14-agent pipeline across **14 Qdrant vector collections**."

4. DUAL KEYWORDS & CONCEPT CO-OCCURRENCE:
   - For critical technologies, include both standard name and acronym if natural and grounded: e.g., "PostgreSQL (Postgres)", "RESTful APIs (REST)".
   - Highlight concept co-occurrence (e.g., PostgreSQL with row-level locks, Redis with caching/pubsub, LiveKit with WebRTC, XGBoost with SHAP/LIME).

5. STRICT ANTI-HALLUCINATION CONTRACT (ZERO TOLERANCE):
   - Every technology, tool, database, framework, library, protocol, and numeric metric MUST appear verbatim or directly in the SOURCE OF TRUTH below.
   - NEVER invent or import any technology or metric not present in the project truth, even if requested by the JD.
   - Report any unmet JD requirements in the "unmet" list.

6. BULLET CONSTRAINTS:
   - Produce EXACTLY 3 bullets.
   - Word count per bullet: Between 14 and 26 words (counting natural words; markdown asterisks do not count towards word length).
   - Never use first-person pronouns ("I", "me", "my", "we", "our").

7. JSON ONLY:
   - Return valid JSON matching the schema below without commentary or markdown code fences.

SCHEMA:
{
  "bullets": [
    "<Strong Verb> <Deliverable> achieving **<Metric>** by <Engineering Details> using **<Tech>**.",
    "<Strong Verb> <Deliverable/Mechanism> with **<Tech>**, handling <Feature/Scale> with **<Metric>**.",
    "<Strong Verb> <Deliverable/Integration> using **<Tech>**, ensuring <Outcome> validated by **<Metric>**."
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
        source_of_truth.append(f"VERIFIED MANUAL HIGHLIGHTS & GROUND TRUTH METRICS:\n{project.manual_notes}")

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
        f"INSTRUCTIONS:\n"
        f"1. Generate exactly 3 grounded bullets (14-26 words each) for {name}.\n"
        f"2. Follow Google X-Y-Z formula: Accomplished [X] as measured by [Y], by doing [Z].\n"
        f"3. First 4 Words Rule: Start immediately with a strong technical action verb + technical deliverable.\n"
        f"4. Wrap 1-2 key verified metrics or core tools in markdown bold (**metric** / **tech**).\n"
        f"5. Output JSON only matching the schema."
    )
