import re
import json
import httpx
from typing import Dict, Any, List, Optional, Tuple
from resume_agent.models import JobModel
from resume_agent.apply.models import CandidateSubmissionPayload
from resume_agent.profile.service import get_compliance_profile
from resume_agent.config import get_settings
from resume_agent.logging import logger


class QAGenerator:
    """
    Intelligent Form Question-Answering Engine.
    Resolves application form fields using:
    1. Static deterministic compliance configuration (Visa, work authorization, graduation date, EEO).
    2. DeepSeek LLM generation for behavioral/subjective essay prompts grounded in candidate's verified projects.
    """

    def __init__(self):
        self.settings = get_settings()
        self.compliance = get_compliance_profile()
        self._cache: Dict[str, str] = {}

    def resolve_question(
        self,
        question_text: str,
        field_type: str = "text",
        job: Optional[JobModel] = None,
        candidate: Optional[CandidateSubmissionPayload] = None,
        options: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Main entrypoint: analyzes question text and returns the appropriate grounded answer.
        """
        q_norm = self._normalize_text(question_text)
        options = options or []

        # 1. Deterministic / Compliance Checks
        det_res = self._match_deterministic(q_norm, question_text, options, job)
        if det_res:
            return det_res

        # 2. Options selection without LLM (heuristics for dropdowns)
        if options and field_type in ("select", "radio"):
            opt_res = self._match_options_heuristic(q_norm, options)
            if opt_res:
                return opt_res

        # 3. Subjective / Essay generation via LLM
        return self._generate_llm_answer(question_text, job, candidate, options, field_type)

    def _normalize_text(self, text: str) -> str:
        return re.sub(r"[^\w\s]", " ", text.lower()).strip()

    def _match_deterministic(
        self,
        q_norm: str,
        raw_q: str,
        options: List[str],
        job: Optional[JobModel] = None
    ) -> Optional[Dict[str, Any]]:
        """Match deterministic legal, immigration, education, identity, and EEO fields."""
        work_auth = self.compliance.get("work_authorization", {})
        edu = self.compliance.get("education_and_availability", {})
        eeo = self.compliance.get("eeo_demographics", {})
        identity = self.compliance.get("legal_identity", {})
        relations = self.compliance.get("company_relations", {})

        # --- A. Work Authorization & Visa Sponsorship ---
        is_sponsorship = any(kw in q_norm for kw in [
            "require sponsorship", "need sponsorship", "visa sponsorship",
            "future sponsorship", "require visa", "immigration sponsorship"
        ])
        if is_sponsorship:
            ans = "Yes" if work_auth.get("requires_us_sponsorship", True) else "No"
            return self._format_result(ans, "work_authorization_sponsorship", options)

        is_auth = any(kw in q_norm for kw in [
            "authorized to work", "legally authorized", "legal right to work",
            "work authorization", "eligible to work", "work permit"
        ])
        if is_auth:
            job_loc = (job.location or "").lower() if job else ""
            if "india" in q_norm or "india" in job_loc:
                ans = "Yes"
            elif any(c in q_norm or c in job_loc for c in ["united states", "us", "u s", "usa", "san francisco", "new york"]):
                ans = "No"  # Requires US visa/sponsorship
            elif any(c in q_norm or c in job_loc for c in ["uk", "london", "europe", "canada"]):
                ans = "No"  # Requires international visa
            else:
                ans = "No" if work_auth.get("requires_general_sponsorship", True) else "Yes"
            return self._format_result(ans, "work_authorization_eligibility", options)

        # --- B. Education & Graduation ---
        if any(kw in q_norm for kw in ["graduation date", "expected graduation", "grad date", "completion date"]):
            ans = edu.get("expected_graduation", "May 2028")
            return self._format_result(ans, "graduation_date", options)

        if any(kw in q_norm for kw in ["graduation year", "year of graduation"]):
            ans = edu.get("expected_graduation_year", "2028")
            return self._format_result(ans, "graduation_year", options)

        if any(kw in q_norm for kw in ["university", "college", "school name", "institution"]):
            ans = edu.get("current_university", "SRM University Amaravati")
            return self._format_result(ans, "university", options)

        if any(kw in q_norm for kw in ["degree", "degree type"]):
            ans = edu.get("degree", "B.Tech in Computer Science")
            return self._format_result(ans, "degree", options)

        if any(kw in q_norm for kw in ["cgpa", "gpa", "cumulative gpa"]):
            ans = edu.get("cgpa", "8.78")
            return self._format_result(ans, "cgpa", options)

        # --- C. Legal Identity & Names ---
        if any(kw in q_norm for kw in ["full legal name", "legal name"]):
            ans = identity.get("full_legal_name", "Utkarsh Singh")
            return self._format_result(ans, "full_legal_name", options)

        if any(kw in q_norm for kw in ["preferred first name", "preferred name"]):
            ans = identity.get("preferred_first_name", "Utkarsh")
            return self._format_result(ans, "preferred_name", options)

        if "pronoun" in q_norm:
            ans = identity.get("pronouns", "He/Him")
            return self._format_result(ans, "pronouns", options)

        # --- D. Prior Employment & Referral ---
        if any(kw in q_norm for kw in ["worked for", "previously employed", "former employee"]):
            ans = relations.get("previously_employed", "No")
            return self._format_result(ans, "previously_employed", options)

        if any(kw in q_norm for kw in ["relative", "family member"]):
            ans = relations.get("has_relatives_employed", "No")
            return self._format_result(ans, "relative_employed", options)

        if any(kw in q_norm for kw in ["how did you connect", "how did you hear", "source of referral", "referral source"]):
            ans = relations.get("how_did_you_hear", "LinkedIn / Company Careers Page")
            return self._format_result(ans, "referral_source", options)

        # --- E. EEO / Demographics ---
        if "gender" in q_norm:
            ans = eeo.get("gender", "Male")
            return self._format_result(ans, "eeo_gender", options)

        if any(kw in q_norm for kw in ["race", "ethnicity", "ethnic origin"]):
            ans = eeo.get("race_ethnicity", "Asian (Indian)")
            return self._format_result(ans, "eeo_race", options)

        if "veteran" in q_norm:
            ans = eeo.get("veteran_status", "I am not a protected veteran")
            return self._format_result(ans, "eeo_veteran", options)

        if "disability" in q_norm:
            ans = eeo.get("disability_status", "No, I do not have a disability")
            return self._format_result(ans, "eeo_disability", options)

        return None

    def _match_options_heuristic(self, q_norm: str, options: List[str]) -> Optional[Dict[str, Any]]:
        """Match engineering interest or standard categorical choice from dropdown."""
        # Engineering track preference
        if any(kw in q_norm for kw in ["type of engineering", "engineering work", "interest", "team", "track"]):
            keywords_priority = [
                ["backend", "server", "distributed"],
                ["infrastructure", "platform", "systems", "cloud"],
                ["full stack", "fullstack", "web"],
                ["machine learning", "ai", "data"],
                ["product engineering", "software engineer"]
            ]
            for kw_group in keywords_priority:
                for opt in options:
                    if any(kw in opt.lower() for kw in kw_group):
                        return {
                            "answer": opt,
                            "is_ai_generated": False,
                            "category": "engineering_track_choice",
                            "confidence": 0.95
                        }

        # Fallback to first non-empty option if available
        for opt in options:
            if opt.strip() and not any(placeholder in opt.lower() for placeholder in ["select", "choose", "--"]):
                return {
                    "answer": opt,
                    "is_ai_generated": False,
                    "category": "dropdown_default",
                    "confidence": 0.70
                }

        return None

    def _generate_llm_answer(
        self,
        question_text: str,
        job: Optional[JobModel],
        candidate: Optional[CandidateSubmissionPayload],
        options: List[str],
        field_type: str
    ) -> Dict[str, Any]:
        """Query DeepSeek via OpenRouter to craft a sharp, grounded 2-3 sentence answer."""
        cache_key = f"{job.company_name if job else 'generic'}::{question_text}"
        if cache_key in self._cache:
            return {
                "answer": self._cache[cache_key],
                "is_ai_generated": True,
                "category": "llm_subjective",
                "confidence": 0.95
            }

        company = job.company_name if job else "the company"
        role = job.title if job else "Software Engineer Intern"
        jd_snippet = (job.description_md or "")[:600] if job else ""

        system_prompt = (
            "You are Utkarsh Singh, a 3rd-year CS student at SRM University Amaravati (CGPA 8.78, graduating May 2028). "
            "You are applying for a software engineering internship. "
            "Your verified engineering portfolio consists of:\n"
            "1. RudraKernel: Multi-Agent Reinforcement Learning Environment for LLM Safety (Python, TRL, GRPO, FastAPI) — Meta OpenEnv Hackathon finalist.\n"
            "2. Trinetra: Autonomous Cross-Compliance Financial Intelligence Pipeline (Python, LangGraph, FastAPI, XGBoost, PostgreSQL) — patent-filed credit analysis system.\n"
            "3. MerchantMind: Autonomous AI Conversational Commerce Agent with 3-phase atomic checkout saga (FastAPI, Redis, PostgreSQL row-level locks, Next.js).\n"
            "4. Aegis Forge: Real-Time Voice AI Interview Platform (850ms latency, LiveKit WebRTC, FastAPI).\n\n"
            "Rules for answering employer questions:\n"
            "- Write in first person ('I built...', 'My experience with...').\n"
            "- Exactly 2 to 4 sentences. Concise, dense, high-impact.\n"
            "- Ground the answer strictly in your real technical projects above.\n"
            "- Zero corporate jargon, zero exaggerated fluff, no conversational greetings.\n"
            "- Answer the specific question directly."
        )

        user_prompt = (
            f"Employer: {company}\n"
            f"Role: {role}\n"
            f"Job Overview: {jd_snippet}\n"
            f"Question on Application Form: \"{question_text}\"\n\n"
            f"Please generate the exact text to enter into this application form field."
        )

        try:
            api_key = self.settings.openrouter_api_key
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY is missing.")

            payload = {
                "model": "deepseek/deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 200
            }

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            with httpx.Client(timeout=25.0) as client:
                resp = client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    json=payload,
                    headers=headers
                )
                resp.raise_for_status()
                data = resp.json()
                raw_ans = data["choices"][0]["message"]["content"].strip()
                # Clean enclosing quotes if LLM added them
                cleaned_ans = re.sub(r'^["\']|["\']$', '', raw_ans).strip()

            self._cache[cache_key] = cleaned_ans
            return {
                "answer": cleaned_ans,
                "is_ai_generated": True,
                "category": "llm_subjective",
                "confidence": 0.95
            }

        except Exception as e:
            logger.warning(f"LLM question answer generation failed ({e}), using safe fallback.")
            fallback = (
                f"I am excited to bring my experience building production multi-agent systems and "
                f"high-performance backend architectures like RudraKernel and Trinetra to the engineering team at {company}."
            )
            return {
                "answer": fallback,
                "is_ai_generated": False,
                "category": "fallback_subjective",
                "confidence": 0.70
            }

    def _format_result(self, raw_value: str, category: str, options: List[str]) -> Dict[str, Any]:
        """Helper to match raw answer against dropdown options if present."""
        if not options:
            return {
                "answer": raw_value,
                "is_ai_generated": False,
                "category": category,
                "confidence": 1.0
            }

        # Match closest option
        val_lower = raw_value.lower()
        for opt in options:
            if opt.lower() == val_lower or val_lower in opt.lower() or opt.lower() in val_lower:
                return {
                    "answer": opt,
                    "is_ai_generated": False,
                    "category": category,
                    "confidence": 1.0
                }

        # Fallback to raw value
        return {
            "answer": raw_value,
            "is_ai_generated": False,
            "category": category,
            "confidence": 0.90
        }
