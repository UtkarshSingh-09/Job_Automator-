# 📋 Autonomous Resume Agent: System Requirements & Execution Blueprint

> **Project Name:** Autonomous Internship-Matching, Resume Generation & Auto-Apply System  
> **Target Candidate:** Utkarsh Singh (B.Tech CS @ SRM University Amaravati, Grad 2028, CGPA 8.78)  
> **Core Focus:** SDE / AI / ML / Systems Engineering Internships & Entry-Level Roles  
> **Status:** Requirements Defined — Ready for Phase 1 Implementation  

---

## 📑 Table of Contents

1. [System Objective & Scope](#1-system-objective--scope)
2. [Current Readiness & Asset Inventory](#2-current-readiness--asset-inventory)
3. [Required Credentials & Environment Prerequisites](#3-required-credentials--environment-prerequisites)
4. [Functional Requirements (FR-01 to FR-10)](#4-functional-requirements)
5. [Non-Functional Requirements & Guardrails (NFR-01 to NFR-06)](#5-non-functional-requirements--guardrails)
6. [Data Models & Schema Contracts](#6-data-models--schema-contracts)
7. [Phase-by-Phase Implementation Roadmap](#7-phase-by-phase-implementation-roadmap)
8. [Actionable Checklist: What to Build First](#8-actionable-checklist-what-to-build-first)

---

## 1. System Objective & Scope

The objective of this system is to eliminate the manual, repetitive grind of searching, tailoring resumes, and applying for software engineering internships.

The system autonomously executes a daily pipeline at **09:00 IST (03:30 UTC)**:
1. **Polls 300+ tech companies** across high-signal ATS APIs (Greenhouse, Lever, Ashby, Workable, etc.).
2. **Filters strictly for internships & fresh graduate roles** (excluding 3+ years experience, senior titles).
3. **Matches openings against the candidate's verified project portfolio** using local embeddings (`bge-small-en-v1.5`) and LLM semantic selection (`claude-sonnet-4-6`).
4. **Selects the top 3 most relevant projects** (prioritizing Aegis Forge, Trinetra, RudraKernel, MerchantMind).
5. **Rewrites project bullet points in the exact vocabulary of the Job Description**, enforced by a strict code-level anti-hallucination verifier (zero fabricated technologies or metrics).
6. **Compiles a single-page, ATS-proof PDF** via LaTeX (`tectonic`) using verified Unicode preambles and anti-hyphenation guards.
7. **Mechanically validates the generated PDF** (100% parse-back recovery, $\ge 90\%$ keyword coverage, 1-page guarantee).
8. **Submits the application where technically feasible** via direct ATS APIs or Playwright browser automation.
9. **Delivers real-time Telegram alerts** with the compiled PDF, confirmation screenshot, and direct apply link.

---

## 2. Current Readiness & Asset Inventory

All preparatory research, source resumes, project specifications, and architectural maps have been prepared:

| Asset | Location / File | Purpose & Status |
|---|---|---|
| **System Spec** | [`RESUME_AGENT_SPEC.md`](file:///Users/utkarshsingh/Desktop/Job_finder/RESUME_AGENT_SPEC.md) | Authoritative technical specification (v1.0) with resolved decisions. |
| **System Architecture** | [`PROJECT_ARCHITECTURE.md`](file:///Users/utkarshsingh/Desktop/Job_finder/PROJECT_ARCHITECTURE.md) | Complete ~59-file tree, module definitions, CLI commands, and CI/CD workflow. |
| **Project Knowledge Base** | [`PROJECTS_PORTFOLIO.md`](file:///Users/utkarshsingh/Desktop/Job_finder/PROJECTS_PORTFOLIO.md) | Verified grounding corpus for all 6 projects with metrics, hackathon awards, and links. |
| **ATS Deep Research** | [`ATS_RESUME_RESEARCH.md`](file:///Users/utkarshsingh/Desktop/Job_finder/ATS_RESUME_RESEARCH.md) | 556-line technical guide on Textkernel parsing, LaTeX anti-hyphenation, and eye-tracking. |
| **Candidate Source Resume** | `data/input/old_resume.pdf` | Extracted from `GDG_resume.pdf` (SRM Amaravati, CGPA 8.78, ShulinTech, top awards). |
| **6 Project READMEs** | `README (5).md` to `readme (10).md` | Source documentation for MerchantMind, Trinetra, Aegis Forge, RudraKernel, Madad AI, AstraGuard. |

---

## 3. Required Credentials & Environment Prerequisites

To run the pipeline locally and in GitHub Actions, the following environment variables and tools are required:

### 1. API Keys & Tokens (`.env`)

| Variable | Description | Where to Get | Status |
|---|---|---|:---:|
| `ANTHROPIC_API_KEY` | Powers project selection and bullet rewriting (`claude-sonnet-4-6`) | [console.anthropic.com](https://console.anthropic.com/) | 🔴 User to provide |
| `GITHUB_TOKEN` | Fine-grained PAT (Read-only `public_repo` scope) to sync repo metadata | [github.com/settings/tokens](https://github.com/settings/tokens?type=beta) | 🔴 User to provide |
| `GITHUB_USERNAME` | `UtkarshSingh-09` | Confirmed from profile | 🟢 Ready (`UtkarshSingh-09`) |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token for instant push notifications and PDF delivery | Create via [@BotFather](https://t.me/BotFather) | 🔴 User to create |
| `TELEGRAM_CHAT_ID` | Your numeric Telegram chat ID | Message [@userinfobot](https://t.me/userinfobot) | 🔴 User to provide |
| `ADZUNA_APP_ID` | (Optional) Adzuna India job aggregator ID | [developer.adzuna.com](https://developer.adzuna.com/) | 🟡 Optional |
| `ADZUNA_APP_KEY` | (Optional) Adzuna India job aggregator API key | [developer.adzuna.com](https://developer.adzuna.com/) | 🟡 Optional |

### 2. System Tooling
* **Python 3.11+** installed.
* **`uv` package manager:** Install via `curl -LsSf https://astral.sh/uv/install.sh | sh`
* **`tectonic` LaTeX engine:** Self-contained, single binary. Install via `brew install tectonic` or download release.
* **`playwright` browser:** For auto-apply form interaction (`uv run playwright install chromium --with-deps`).

---

## 4. Functional Requirements

### FR-01: Profile Extraction & Human Confirmation Gate
* **Input:** `data/input/old_resume.pdf`.
* **Behavior:** Extract text via `pymupdf` $\rightarrow$ invoke LLM to structure into `profile` JSON schema $\rightarrow$ print to stdout $\rightarrow$ **halt for human confirmation**.
* **Integrity Guard:** The pipeline **refuses to generate resumes** if `profile.confirmed_at` is `NULL`. This prevents wrong CGPA or phone numbers from propagating.
* **CLI:** `resume-agent profile parse [--force]`

### FR-02: GitHub Synchronization & Quality Scorer
* **Behavior:** Fetch all public repositories for `UtkarshSingh-09` using the GitHub REST API (README, languages, commit count, topics, stars, Docker/CI presence).
* **Deterministic Quality Score (0–100):**
  $$\text{Score} = 25(\text{README}) + 20(\text{commits}) + 15(\text{tests}) + 10(\text{CI}) + 5(\text{Docker}) + 10(\text{diversity}) + 10(\text{recency}) + 5(\text{stars})$$
* **Override Integration:** Merge with `data/config/projects_override.yaml` (pinning Aegis Forge, Trinetra, RudraKernel, MerchantMind with high priority).
* **CLI:** `resume-agent github sync`

### FR-03: ATS Detection & Company Discovery
* **Input:** `data/config/companies.yaml` (300–600 tech companies/startups).
* **Behavior:** Query `https://{domain}/careers` and `/jobs`, follow redirects (max 5), regex for embedded ATS signatures (Greenhouse, Lever, Ashby, Workable, Recruitee, SmartRecruiters).
* **Validation:** Ping discovered ATS endpoint; persist slug only if it returns $\ge 1$ active job. Unresolved companies export to `reports/unresolved_companies.csv`.
* **CLI:** `resume-agent companies detect [--refresh] [--tier 1]`

### FR-04: High-Fidelity Job Ingestion Adapters
* **Architecture:** Abstract base protocol `JobSource` with async `fetch(client, company)` and `normalize(raw)`.
* **Tier 1 (ATS Endpoints):**
  - Greenhouse: `boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true`
  - Lever: `api.lever.co/v0/postings/{slug}?mode=json`
  - Ashby: `api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true`
  - Workable: `apply.workable.com/api/v1/accounts/{slug}?details=true`
  - Recruitee: `{slug}.recruitee.com/api/offers/`
  - SmartRecruiters: `api.smartrecruiters.com/v1/companies/{slug}/postings`
* **Tier 2 (Aggregators):** Adzuna, Arbeitnow.
* **Tier 3 (LLM Fallback):** For tier-1 companies with custom pages, scrape plain text via `trafilatura` and parse via LLM JSON schema (capped at 40/week).
* **CLI:** `resume-agent jobs fetch [--source X] [--dry-run]`

### FR-05: Deduplication, Normalization & Internship Filtering
* **Deduplication:** Compute `content_hash = sha256(norm(company) + norm(title) + norm(location))`. Direct ATS sources override aggregator duplicates.
* **Internship Filter Regex:**
  * **INCLUDE:** `\b(intern|internship|trainee|graduate|campus|entry.?level|fresher|new.?grad|sde.?[01]|associate (software )?engineer)\b`
  * **EXCLUDE:** `\b(senior|staff|principal|lead|manager|director|architect|head of|\d+\+?\s*years?)\b`
* **Location Filter:** India, or `remote` with no non-India geographic restriction. Posted within 30 days.

### FR-06: Two-Stage Semantic Matching
* **Stage A (Local Vector Retrieval - Free):**
  - Embed project metadata (`name + description + topics + README excerpt + manual_notes`) using `BAAI/bge-small-en-v1.5` (384-dim).
  - Embed JD requirements $\rightarrow$ compute cosine similarity $\rightarrow$ retrieve **Top 8 Candidate Projects**.
* **Stage B (LLM Reasoning & Selection):**
  - Prompt Claude Sonnet with JD and the 8 candidate projects $\rightarrow$ select the **best 3 projects** with explicit requirement alignment and `overall_fit` score (0–100).
  - **Threshold Gate:** If `overall_fit < 55` (or production 70), drop the job immediately without generating a resume.
* **CLI:** `resume-agent match --job-id 123`

### FR-07: Anti-Hallucination Bullet Generation & Grounding Verifier
* **Prompt Grounding Contract:** The LLM is strictly forbidden from introducing any technology, framework, database, or number not explicitly present in the project's source corpus.
* **Format:** Exactly 3 bullet points per project, each 14–26 words, single-line, following the **Google X-Y-Z formula**.
* **Deterministic Code Verifier (`verify_grounding()`):**
  - Tokenizes output bullets against `data/gazetteer/skills.yaml`.
  - Asserts: `hallucinated_skills = output_skills - source_skills == empty`.
  - Asserts: All numbers/percentages exist verbatim in source text.
  - On failure: Rejects and retries with explicit feedback (max 2 retries), falling back to pre-verified default bullets if retries exhaust.

### FR-08: ATS-Safe LaTeX Rendering & PDF Compilation
* **Template Engine:** Jinja2 $\rightarrow$ LaTeX $\rightarrow$ `tectonic`.
* **LaTeX Compliance Constraints:**
  - Preamble enforces `\input{glyphtounicode}` and `\pdfgentounicode=1`.
  - Preamble enforces `\hyphenpenalty=10000` and `\exhyphenpenalty=10000` to prevent keyword splitting across linebreaks.
  - Strict single-column layout; zero tables for page layout; zero icon fonts.
  - Clean clickable links with human-readable text (`\href{https://github.com/...}{github.com/...}`).
  - Escape all LaTeX special characters (`& % $ # _ { } ~ ^ \`).
* **Output Path:** `data/output/{YYYY-MM-DD}/{company}__{title_slug}.pdf` + metadata JSON.

### FR-09: 7-Gate Mechanical ATS Validation Suite
Every compiled PDF must pass before moving forward:
1. **Parse-Back Fidelity:** Extract text with `pymupdf`; assert 100% of candidate profile fields and generated bullets are recovered verbatim.
2. **Reading Order:** Assert headers appear in order: `EDUCATION` $\rightarrow$ `SKILLS` $\rightarrow$ `PROJECTS` $\rightarrow$ `EXPERIENCE` $\rightarrow$ `HONORS & ACHIEVEMENTS`.
3. **Unicode Integrity:** Assert zero `\ufffd` or unmapped glyphs; ligatures (`fi`, `fl`) cleanly normalize.
4. **Physical Page Count:** Assert `page_count == 1`.
5. **Keyword Coverage Score:** Match recovered PDF text against JD hard requirements extracted from the skills gazetteer. Assert $\ge 90\%$.
6. **Retry Loop:** If coverage $< 90$ and attempts $< 3$, re-generate bullets with missing grounded skills highlighted.

### FR-10: Automated Application Submission & Telegram Delivery
* **Tier 1 (API Apply):** Submit multipart form data directly to Greenhouse (`/v1/boards/{slug}/jobs/{id}/application`), Lever, and Workable APIs.
* **Tier 2 (Browser Automation):** For custom forms, launch headless Chromium via Playwright, map fields (`name`, `email`, `phone`, `links`), attach PDF resume, submit, and save confirmation screenshot.
* **Safety Guards:**
  - Never attempt account creation or CAPTCHA solving (skip and mark `needs_login` or `captcha_blocked`).
  - Max 10 auto-applies per day; minimum 3-minute cooldown per domain.
  - `--dry-run` flag fills forms and screenshots without clicking submit.
* **Real-Time Telegram Notification:** Send instant message upon submission with attached PDF, fit score, and confirmation screenshot.
* **Daily Digest (09:00 IST):** Send morning summary of all matches, successful submissions, and failed jobs with manual apply links.

---

## 5. Non-Functional Requirements & Guardrails

| ID | Requirement | Specification / Constraint |
|:---:|---|---|
| **NFR-01** | **Politeness & Rate Limits** | Global HTTP concurrency $\le 8$; per-host concurrency $= 1$. Honest User-Agent header with GitHub URL. Respect `robots.txt`. Cache with HTTP `If-None-Match` (ETag). Exponential backoff on 429/5xx (max 3 retries). |
| **NFR-02** | **Zero Hallucination** | Hard deterministic code verifier blocks any resume containing tech tokens or numbers absent from candidate's verified corpus. |
| **NFR-03** | **Cost Circuit Breakers** | Max 15 resumes generated per day (`MAX_DAILY_RESUMES=15`). Max 10 auto-applies per day (`MAX_DAILY_APPLIES=10`). Monthly LLM API spend strictly $<\text{₹}600$. |
| **NFR-04** | **Single-Page Guarantee** | PDF vertical geometry must fit on a single A4 page. Automated truncation drops secondary achievements or project 3 third bullet if spillover occurs. |
| **NFR-05** | **Performance & Latency** | End-to-end latency per resume generation $< 60$ seconds. Daily sweep of 300+ companies completes in $< 10$ minutes. |
| **NFR-06** | **Zero Cloud Infrastructure Ops** | Local SQLite database in WAL mode. Scheduled via GitHub Actions cron (100% free tier). Zero monthly server hosting cost. |

---

## 6. Data Models & Schema Contracts

```sql
-- Core SQLite Schema (migrations/001_init.sql & 002_auto_apply.sql)

CREATE TABLE profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    full_name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT,
    github_url TEXT, linkedin_url TEXT, portfolio_url TEXT,
    college TEXT, degree TEXT, branch TEXT,
    grad_year INTEGER, cgpa REAL, location TEXT,
    skills_json TEXT NOT NULL DEFAULT '[]',
    coursework_json TEXT NOT NULL DEFAULT '[]',
    achievements_json TEXT NOT NULL DEFAULT '[]',
    certifications_json TEXT NOT NULL DEFAULT '[]',
    raw_text TEXT, confirmed_at TIMESTAMP, updated_at TIMESTAMP
);

CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    repo_name TEXT UNIQUE NOT NULL, display_name TEXT,
    description TEXT, readme_md TEXT, manual_notes TEXT,
    languages_json TEXT, primary_language TEXT, topics_json TEXT,
    stars INTEGER DEFAULT 0, commit_count INTEGER DEFAULT 0,
    has_tests BOOLEAN DEFAULT 0, has_ci BOOLEAN DEFAULT 0,
    has_docker BOOLEAN DEFAULT 0, line_count INTEGER,
    quality_score REAL, include_override BOOLEAN,
    priority INTEGER DEFAULT 10,
    embedding BLOB, embedding_source_hash TEXT,
    created_at TIMESTAMP, pushed_at TIMESTAMP, synced_at TIMESTAMP
);

CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL, domain TEXT UNIQUE NOT NULL,
    tier INTEGER DEFAULT 2,
    ats_provider TEXT, ats_slug TEXT,
    detection_status TEXT, -- resolved | unknown | manual | dead
    etag TEXT, last_polled_at TIMESTAMP,
    consecutive_failures INTEGER DEFAULT 0,
    UNIQUE (ats_provider, ats_slug)
);

CREATE TABLE jobs (
    id INTEGER PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    company_name TEXT NOT NULL, title TEXT NOT NULL,
    location TEXT, remote_type TEXT,
    description_md TEXT NOT NULL, apply_url TEXT NOT NULL,
    posted_at TIMESTAMP, source TEXT NOT NULL, source_job_id TEXT,
    content_hash TEXT UNIQUE NOT NULL,
    passed_filter BOOLEAN, first_seen_at TIMESTAMP, last_seen_at TIMESTAMP
);

CREATE TABLE matches (
    id INTEGER PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(id),
    overall_fit REAL, selected_projects_json TEXT,
    selection_reasoning TEXT, uncovered_requirements_json TEXT,
    bullets_json TEXT,
    pdf_path TEXT, parse_ok BOOLEAN,
    coverage_score REAL, missing_terms_json TEXT,
    attempts INTEGER DEFAULT 0, needs_review BOOLEAN DEFAULT 0,
    llm_cost_usd REAL, created_at TIMESTAMP,
    UNIQUE (job_id)
);

CREATE TABLE applications (
    id INTEGER PRIMARY KEY,
    match_id INTEGER REFERENCES matches(id),
    status TEXT DEFAULT 'generated', -- generated | submitted | applied | rejected | interview
    auto_apply_status TEXT DEFAULT 'pending', -- pending | submitted | needs_login | captcha_blocked | form_error | skipped
    confirmation_screenshot TEXT,
    submit_attempted_at TIMESTAMP,
    applied_at TIMESTAMP, notes TEXT
);

CREATE TABLE run_log (
    id INTEGER PRIMARY KEY, run_type TEXT, started_at TIMESTAMP,
    finished_at TIMESTAMP, status TEXT, stats_json TEXT, error TEXT
);
```

---

## 7. Phase-by-Phase Implementation Roadmap

> **📌 Detailed 10-phase plan with manual steps and git checkpoints:** See [`PHASES.md`](file:///Users/utkarshsingh/Desktop/Job_finder/PHASES.md)  
> **📊 Live progress tracking:** See [`progress/CURRENT_STATUS.md`](file:///Users/utkarshsingh/Desktop/Job_finder/progress/CURRENT_STATUS.md)

We build in strict phase order (expanded to 10 phases from the original 8). Each phase must pass its explicit acceptance criteria before the next begins:

```
┌───────────┐     ┌───────────┐     ┌───────────┐     ┌───────────┐
│  Phase 1  │────▶│  Phase 2  │────▶│  Phase 3  │────▶│  Phase 4  │
│Foundation │     │ Identity  │     │ Ingestion │     │ Matching  │
└───────────┘     └───────────┘     └───────────┘     └───────────┘
                                                            │
                                                            ▼
┌───────────┐     ┌───────────┐     ┌───────────┐     ┌───────────┐
│  Phase 8  │◀────│  Phase 7  │◀────│  Phase 6  │◀────│  Phase 5  │
│Auto-Apply │     │Automation │     │Validation │     │Generation │
└───────────┘     └───────────┘     └───────────┘     └───────────┘
```

### Phase 1 — Foundation
* **Deliverables:** `pyproject.toml` (with uv), `src/resume_agent/config.py`, `db.py`, `models.py`, `logging.py`, `cli.py`, `migrations/001_init.sql`.
* **Acceptance Test:** `uv run resume-agent init` successfully executes migrations and initializes `data/agent.db` with all tables created.

### Phase 2 — Identity & Portfolio Corpus
* **Deliverables:** `profile/parser.py` (extracts `old_resume.pdf`), `github/client.py`, `github/scorer.py`, `data/config/projects_override.yaml`.
* **Acceptance Test:** `profile` table is populated and confirmed by human prompt; $\ge 6$ core projects synced with quality scores and grounded manual notes.

### Phase 3 — Job Ingestion & Filtering Pipeline
* **Deliverables:** `jobs/discovery/detector.py`, `jobs/sources/{base,greenhouse,lever,ashby}.py`, `jobs/pipeline/{normalize,dedupe,filter}.py`, `data/config/companies.yaml`.
* **Acceptance Test:** $\ge 50$ seed companies tested; daily sweep returns filtered internship postings; zero duplicate jobs on re-run.

### Phase 4 — Semantic Matching Engine
* **Deliverables:** `matcher/embed.py` (`bge-small-en-v1.5`), `matcher/retrieve.py` (top-8 cosine retrieval), `matcher/select.py` (Claude Sonnet selection).
* **Acceptance Test:** On 10 test JDs, top-3 project selection matches human expected choices on $\ge 7$ cases.

### Phase 5 — Bullet Writer & LaTeX Renderer
* **Deliverables:** `writer/prompts.py`, `writer/generate.py`, `writer/verify.py` (grounding verifier), `render/escape.py`, `render/latex.py`, `templates/resume.tex.j2`.
* **Acceptance Test:** Golden-set anti-hallucination test suite passes 15/15; PDF compiles via `tectonic` to exactly 1 single page.

### Phase 6 — Mechanical ATS Validation Suite
* **Deliverables:** `validate/parseback.py`, `validate/keywords.py` (`data/gazetteer/skills.yaml`), `validate/hygiene.py`.
* **Acceptance Test:** 10/10 generated PDFs recover 100% of candidate data on parse-back; keyword coverage score reaches $\ge 90\%$.

### Phase 7 — Automation & Telegram Delivery
* **Deliverables:** `deliver/telegram.py`, `orchestrate/daily.py`, `.github/workflows/daily.yml`.
* **Acceptance Test:** End-to-end unattended daily pipeline run executes successfully and dispatches Telegram notification with PDF attached.

### Phase 8 — Auto-Apply Engine & Remaining Adapters
* **Deliverables:** `apply/api_submit.py`, `apply/browser_submit.py` (Playwright), `apply/manager.py`, Workable/Recruitee/SmartRecruiters adapters.
* **Acceptance Test:** Dry-run test fills application form, takes confirmation screenshot, and validates safety guardrails.

---

## 8. Actionable Checklist: What to Build First

To begin execution, here is the immediate checklist:

```markdown
- [x] 1. Spec updated with Auto-Apply, Telegram, GitHub Actions, LaTeX format (RESUME_AGENT_SPEC.md)
- [x] 2. System Architecture & 59-file composition mapped (PROJECT_ARCHITECTURE.md)
- [x] 3. Project Knowledge Base & Grounding Corpus created for 6 projects (PROJECTS_PORTFOLIO.md)
- [x] 4. Deep ATS Parser & LaTeX Engineering Research completed (ATS_RESUME_RESEARCH.md)
- [x] 5. Source resume copied to data/input/old_resume.pdf
- [ ] 6. Collect user API keys (.env: ANTHROPIC_API_KEY, GITHUB_TOKEN, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
- [ ] 7. Execute Phase 1: Setup pyproject.toml, SQLite DB migrations, config, and CLI skeleton
- [ ] 8. Execute Phase 2: Parse profile and sync GitHub repositories
```

This file serves as our operational blueprint. Whenever we start building, we follow this document step-by-step.
