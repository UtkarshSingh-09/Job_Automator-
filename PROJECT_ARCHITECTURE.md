# Resume Agent — Project Architecture & File Composition

**This document describes every file, folder, and module in the system.**
Use this alongside `RESUME_AGENT_SPEC.md` for implementation.

---

## User Decisions (Resolved)

| Decision | Choice |
|---|---|
| Scheduler | n8n (Self-Hosted Community Edition, free) |
| Delivery | Telegram Bot API |
| Resume format | LaTeX → PDF (via `tectonic`) |
| Auto-apply | Enabled (API + Playwright) |
| Primary projects | **Aegis Forge, Trinetra, RudraKernel, MerchantMind** (P0) + **AstraGuard** (P1) |
| GitHub Username | `UtkarshSingh-09` |
| GitHub PAT | User needs to create one (instructions below) |
| Telegram Bot | User will create via @BotFather |

---

## GitHub PAT — How to Create

> The system needs a **GitHub Personal Access Token** to read your repos, READMEs,
> languages, topics, and commit counts via the GitHub REST API.

1. Go to https://github.com/settings/tokens?type=beta
2. Click **"Generate new token"**
3. Name: `resume-agent`
4. Expiration: 90 days (renew when it expires)
5. Repository access: **"All repositories"** (or select specific ones)
6. Permissions → Repository permissions:
   - **Contents**: Read-only
   - **Metadata**: Read-only (auto-selected)
7. Click **"Generate token"**
8. Copy the token → paste into `.env` as `GITHUB_TOKEN=ghp_xxxx...`

That's it. No other scopes needed. Read-only, no write access.

---

## Complete File Tree

```
resume-agent/
├── n8n/
│   └── workflows/
│       └── daily_pipeline.json          # n8n visual workflow — scheduled daily at 09:00 IST
│
├── migrations/
│   ├── 001_init.sql                     # Core schema: profile, projects, companies, jobs, matches, applications, run_log
│   └── 002_auto_apply.sql               # Auto-apply columns: auto_apply_status, confirmation_screenshot, submit_attempted_at
│
├── data/
│   ├── config/
│   │   ├── companies.yaml               # Seed list of 300–600 target companies (name, domain, tier)
│   │   └── projects_override.yaml       # Manual overrides: include/exclude projects, manual_notes with real metrics
│   ├── gazetteer/
│   │   └── skills.yaml                  # Curated skill dictionary: languages, frameworks, tools, cloud, concepts
│   ├── input/
│   │   ├── old_resume.pdf               # User's existing resume (one-time input)
│   │   └── linkedin_export.zip          # Optional LinkedIn data export
│   ├── output/
│   │   └── {YYYY-MM-DD}/               # Daily output directory
│   │       ├── {company}__{title_slug}.pdf      # Generated resume PDF
│   │       ├── {company}__{title_slug}.json     # Generation metadata (projects, scores, prompt hashes)
│   │       └── confirmations/                    # Auto-apply confirmation screenshots
│   │           └── {company}__{title_slug}.png
│   └── agent.db                         # SQLite database (created by `resume-agent init`)
│
├── templates/
│   └── resume.tex.j2                    # Jinja2 LaTeX template — single-column, ATS-safe
│
├── reports/
│   ├── unresolved_companies.csv         # Companies where ATS detection failed — user fills manually
│   ├── new_company_candidates.csv       # New companies discovered via aggregators
│   └── weekly_summary.md                # Auto-generated weekly report
│
├── docs/
│   └── decisions.md                     # Record of [DECISION] choices made during implementation
│
├── tests/
│   ├── conftest.py                      # Shared fixtures, DB setup, mock clients
│   ├── fixtures/                        # Real API response snapshots for testing
│   │   ├── greenhouse_response.json
│   │   ├── lever_response.json
│   │   ├── ashby_response.json
│   │   ├── workable_response.json
│   │   ├── recruitee_response.json
│   │   ├── smartrecruiters_response.json
│   │   ├── adzuna_response.json
│   │   ├── arbeitnow_response.json
│   │   ├── ats_detection_pages/         # HTML snapshots for detector tests
│   │   │   ├── greenhouse_embed.html
│   │   │   ├── lever_embed.html
│   │   │   ├── ashby_embed.html
│   │   │   ├── no_ats.html
│   │   │   ├── custom_careers.html
│   │   │   └── redirect_chain.html
│   │   ├── resumes/                     # Test resume PDFs for parse-back validation
│   │   │   └── sample_resume.pdf
│   │   └── golden_bullets/              # Hallucination detection test cases
│   │       └── grounding_test_cases.json
│   ├── test_profile.py                  # Profile parser tests
│   ├── test_github.py                   # GitHub sync + quality scorer tests
│   ├── test_detector.py                 # ATS detection tests
│   ├── test_adapters.py                 # Per-provider adapter tests (mocked HTTP)
│   ├── test_pipeline.py                 # Normalize, dedupe, filter tests
│   ├── test_matcher.py                  # Embedding retrieval + LLM selection tests
│   ├── test_writer.py                   # Bullet generation + grounding verifier tests
│   ├── test_render.py                   # LaTeX rendering + escape tests
│   ├── test_validate.py                 # Parse-back + keyword coverage tests
│   ├── test_apply.py                    # Auto-apply module tests
│   └── test_e2e.py                      # End-to-end dry-run with stubs
│
├── src/
│   └── resume_agent/
│       ├── __init__.py
│       ├── cli.py                       # Typer CLI entrypoint — all commands
│       ├── config.py                    # pydantic-settings: loads .env + companies.yaml
│       ├── db.py                        # SQLite connection, migration runner, query helpers
│       ├── models.py                    # All Pydantic models (shared across modules)
│       ├── logging.py                   # structlog JSON setup
│       │
│       ├── profile/
│       │   ├── __init__.py
│       │   └── parser.py               # Resume PDF → LLM → profile table (with human confirmation gate)
│       │
│       ├── github/
│       │   ├── __init__.py
│       │   ├── client.py               # GitHub REST API client (repos, READMEs, languages, topics, commits)
│       │   └── scorer.py               # Quality score heuristic (0–100)
│       │
│       ├── jobs/
│       │   ├── __init__.py
│       │   ├── discovery/
│       │   │   ├── __init__.py
│       │   │   └── detector.py          # ATS detection: fetch careers page → regex → validate slug
│       │   ├── sources/
│       │   │   ├── __init__.py
│       │   │   ├── base.py              # JobSource Protocol + RawJob/SourceRef types
│       │   │   ├── greenhouse.py        # Greenhouse boards API adapter
│       │   │   ├── lever.py             # Lever postings API adapter
│       │   │   ├── ashby.py             # Ashby job board API adapter
│       │   │   ├── workable.py          # Workable API adapter
│       │   │   ├── recruitee.py         # Recruitee API adapter
│       │   │   ├── smartrecruiters.py   # SmartRecruiters API adapter
│       │   │   ├── adzuna.py            # Adzuna aggregator adapter
│       │   │   ├── arbeitnow.py         # Arbeitnow aggregator adapter
│       │   │   └── llm_fallback.py      # Tier 3: fetch page → trafilatura → LLM extraction
│       │   └── pipeline/
│       │       ├── __init__.py
│       │       ├── normalize.py         # Raw → normalized Job model
│       │       ├── dedupe.py            # content_hash deduplication, direct source wins
│       │       └── filter.py            # Title regex (intern/entry), location, date, not-applied
│       │
│       ├── matcher/
│       │   ├── __init__.py
│       │   ├── embed.py                 # bge-small-en-v1.5 embedding: projects + JD
│       │   ├── retrieve.py              # Cosine similarity → top-8 candidates
│       │   └── select.py               # LLM call → final 3 projects + reasoning + fit score
│       │
│       ├── writer/
│       │   ├── __init__.py
│       │   ├── prompts.py               # Grounding contract prompt template
│       │   ├── generate.py              # LLM call → 3 bullets per project
│       │   └── verify.py               # Post-generation grounding verifier (code, not LLM)
│       │
│       ├── render/
│       │   ├── __init__.py
│       │   ├── latex.py                 # Jinja2 template rendering → .tex file
│       │   └── escape.py               # LaTeX special character escaper
│       │
│       ├── validate/
│       │   ├── __init__.py
│       │   ├── parseback.py             # PDF text extraction → field-level equality check
│       │   ├── keywords.py              # JD keyword extraction + coverage scoring (0–100)
│       │   └── hygiene.py               # Format checks: word count, tense, pronouns, verb starts
│       │
│       ├── apply/
│       │   ├── __init__.py
│       │   ├── api_submit.py            # Tier 1: API-based apply (Greenhouse, Lever, Workable)
│       │   ├── browser_submit.py        # Tier 2: Playwright browser automation
│       │   └── manager.py              # Orchestrates apply attempts, respects guardrails
│       │
│       ├── deliver/
│       │   ├── __init__.py
│       │   └── telegram.py              # Telegram Bot: daily digest, real-time apply notifications, inline buttons
│       │
│       └── orchestrate/
│           ├── __init__.py
│           └── daily.py                 # Full pipeline: fetch → filter → match → generate → validate → apply → notify
│
├── pyproject.toml                       # Project metadata, dependencies, scripts, ruff config
├── .env.example                         # Template for all required environment variables
├── .gitignore                           # data/agent.db, data/output/, .env, __pycache__, etc.
├── README.md                            # Project overview, setup, usage
├── RESUME_AGENT_SPEC.md                 # The full implementation spec
└── PROJECT_ARCHITECTURE.md              # This file
```

---

## Module Composition — What Each File Does

### `cli.py` — Command Entrypoint

```
typer app with commands:
  init          → run migrations, create dirs
  profile parse → call profile/parser.py [--force]
  github sync   → call github/client.py + scorer.py
  companies detect → call jobs/discovery/detector.py [--refresh] [--tier N]
  jobs fetch    → call all adapters → pipeline [--source X] [--dry-run]
  match         → call matcher/* --job-id N
  generate      → call writer/* + render/* + validate/* --job-id N [--no-validate]
  apply         → call apply/* --job-id N [--dry-run]
  run daily     → call orchestrate/daily.py (full pipeline)
  report weekly → generate weekly_summary.md
```

### `config.py` — Configuration

```python
class Settings(BaseSettings):
    # API keys
    anthropic_api_key: str
    github_token: str
    github_username: str
    telegram_bot_token: str
    telegram_chat_id: str

    # Optional aggregator keys
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""

    # Paths
    database_path: str = "data/agent.db"

    # Model config
    llm_model: str = "claude-sonnet-4-6"
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    # Thresholds
    min_fit_score: int = 55
    min_coverage_score: int = 90
    max_retries: int = 3
    max_daily_resumes: int = 15
    max_daily_applies: int = 10
    apply_cooldown_seconds: int = 180

    # Runtime
    log_level: str = "INFO"
    dry_run: bool = False

    model_config = SettingsConfigDict(env_file=".env")
```

### `db.py` — Database Layer

```
- get_connection() → sqlite3.Connection (with WAL mode, foreign keys ON)
- run_migrations(migrations_dir) → applies numbered .sql files in order
- Generic query helpers: execute, fetch_one, fetch_all, insert_returning_id
- No ORM. Raw SQL. Pydantic models for validation only.
```

### `models.py` — Shared Pydantic Models

```
Profile          — full user identity (name, email, college, skills[], etc.)
Project          — GitHub repo data + quality_score + embedding
Company          — name, domain, tier, ats_provider, ats_slug, detection_status
RawJob           — provider-specific raw data
Job              — normalized job (company, title, location, description_md, apply_url, content_hash)
MatchResult      — overall_fit, selected_projects[], uncovered_requirements[]
BulletOutput     — bullets[], tech_used[], unmet[]
ValidationResult — parse_ok, coverage_score, missing_terms[], hygiene_issues[]
ApplyResult      — status, confirmation_screenshot_path, error_reason
RunStats         — jobs_fetched, jobs_filtered, matches, resumes_generated, applies_attempted
```

---

## Data Flow — The Daily Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        orchestrate/daily.py                            │
│                                                                        │
│  1. FETCH JOBS                                                         │
│     for each company with resolved ATS:                                │
│       adapter = get_adapter(company.ats_provider)                      │
│       raw_jobs = await adapter.fetch(client, company)                  │
│       jobs = [adapter.normalize(r) for r in raw_jobs]                  │
│       dedupe(jobs)  →  filter(jobs)  →  insert to DB                  │
│                                                                        │
│  2. MATCH                                                              │
│     for each new filtered job (not yet in matches):                    │
│       candidates = retrieve(job, projects, top_k=8)     # embeddings  │
│       result = select(job, candidates)                   # LLM call   │
│       if result.overall_fit < MIN_FIT_SCORE: skip                     │
│       save match to DB                                                │
│                                                                        │
│  3. GENERATE RESUME                                                    │
│     for each match (up to MAX_DAILY_RESUMES):                         │
│       for each selected project (3):                                   │
│         bullets = generate_bullets(project, job)          # LLM call  │
│         hallucinated, ungrounded = verify_grounding(bullets, source)   │
│         if bad: retry with feedback (max 2 retries)                   │
│       tex = render_latex(profile, projects, bullets)                   │
│       pdf = compile_pdf(tex)                              # tectonic  │
│                                                                        │
│  4. VALIDATE                                                           │
│     parse_ok = parseback_check(pdf, profile, bullets)                  │
│     coverage = keyword_coverage(pdf_text, jd, gazetteer)              │
│     hygiene = hygiene_check(pdf_text)                                 │
│     if not parse_ok: FAIL (blocking, no retry can fix bad rendering)  │
│     if coverage < 90 and attempts < 3: re-run step 3 with hints      │
│                                                                        │
│  5. AUTO-APPLY                                                         │
│     if daily_apply_count < MAX_DAILY_APPLIES:                         │
│       if ats has API apply: api_submit(job, pdf, profile)             │
│       else: browser_submit(job.apply_url, pdf, profile)   # Playwright│
│       save confirmation screenshot                                     │
│       send Telegram notification (success or failure)                  │
│                                                                        │
│  6. DELIVER DIGEST                                                     │
│     compile all results → send Telegram daily digest at 09:00 IST     │
│     attach PDFs (cap 10), include inline buttons                       │
│     log run stats to run_log table                                     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## n8n Visual Workflow Engine

The daily orchestration is driven visually by **n8n (Self-Hosted Community Edition)**.

### Architecture:
```
┌─────────────────────────┐
│ Schedule Trigger (9 AM) │  (Cron: exact 09:00 IST / 03:30 UTC, zero delay)
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Execute Command Node   │  (Runs: uv run resume-agent daily --format json)
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│    IF / Switch Node     │  (Checks if matches > 0)
└─────┬─────────────┬─────┘
      │ YES         │ NO
      │             ▼
      │     ┌─────────────────────────┐
      │     │  Telegram Node (Digest) │  ("No new internships passed threshold today")
      │     └─────────────────────────┘
      ▼
┌─────────────────────────┐
│ Telegram Node (Batched) │  (Sends formatted digest + PDF attachments via Bot API)
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Error Trigger Node      │  (Catches failures & dispatches immediate Telegram alert)
└─────────────────────────┘
```

### Why n8n instead of cron scripts:
1. **Interactive Visual Debugger:** Every step's payload and execution time can be inspected in real time in the browser UI (`localhost:5678` or hosted cloud container).
2. **Exact Timing:** No GitHub Actions queue delay or jitter.
3. **Native Telegram Integration:** Drag-and-drop Telegram node with HTML formatting, inline buttons ("Apply Link"), and PDF attachment handling.
4. **Deployable Anywhere:** Runs locally on Mac (`npx n8n`) or in a free Docker container (Railway / Render / Oracle Always-Free).
5. **Workflow Template:** Exported as `n8n/workflows/daily_pipeline.json` for 1-click import into any n8n instance.

---

## Dependencies (`pyproject.toml`)

```toml
[project]
name = "resume-agent"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    # Core
    "httpx[http2]>=0.27",
    "tenacity>=8.2",
    "pydantic>=2.5",
    "pydantic-settings>=2.1",

    # CLI
    "typer>=0.9",

    # Resume parsing
    "pymupdf>=1.23",

    # Embeddings
    "sentence-transformers>=2.2",
    "numpy>=1.24",

    # LLM
    "anthropic>=0.39",

    # Templating & PDF
    "jinja2>=3.1",
    # tectonic is a system binary, not a pip package

    # NLP / keyword extraction
    "spacy>=3.7",

    # Web content extraction (Tier 3 fallback)
    "trafilatura>=1.6",

    # Browser automation (auto-apply)
    "playwright>=1.40",

    # Telegram
    "python-telegram-bot>=20.7",

    # Logging
    "structlog>=23.2",

    # YAML config
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "pytest-asyncio>=0.23",
    "respx>=0.20",
    "ruff>=0.1",
]

[project.scripts]
resume-agent = "resume_agent.cli:app"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

---

## `.env.example`

```bash
# === Required ===
ANTHROPIC_API_KEY=
GITHUB_TOKEN=              # Fine-grained PAT, read-only (see GitHub PAT section above)
GITHUB_USERNAME=

# === Telegram ===
TELEGRAM_BOT_TOKEN=        # From @BotFather
TELEGRAM_CHAT_ID=          # Your chat ID (use @userinfobot to find it)

# === Optional: Aggregators ===
ADZUNA_APP_ID=
ADZUNA_APP_KEY=

# === Database ===
DATABASE_PATH=data/agent.db

# === Model Config ===
LLM_MODEL=claude-sonnet-4-6
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5

# === Thresholds ===
MIN_FIT_SCORE=55           # Skip jobs below this (raise to 70 for cost savings)
MIN_COVERAGE_SCORE=90      # Minimum keyword coverage to accept a resume
MAX_RETRIES=3              # Max bullet rewrite retries
MAX_DAILY_RESUMES=15       # Cost circuit breaker
MAX_DAILY_APPLIES=10       # Auto-apply circuit breaker
APPLY_COOLDOWN_SECONDS=180 # Min gap between applies to same domain

# === Runtime ===
LOG_LEVEL=INFO
DRY_RUN=false              # Set true to test without submitting
NOTIFY_CHANNEL=telegram
```

---

## Key Projects (User's Portfolio)

The user's projects for resume generation (detailed in [`PROJECTS_PORTFOLIO.md`](file:///Users/utkarshsingh/Desktop/Job_finder/PROJECTS_PORTFOLIO.md)):

| Project | Priority | Links | Key Domains & Tech |
|---|:---:|---|---|
| **Aegis Forge** | **P0 (Highest)** | [GitHub](https://github.com/UtkarshSingh-09/Aegis-Forge-Agents) • [Demo Video](https://youtu.be/6XJ7HiaCKKQ) | Multi-Agent AI Interviewer, LiveKit Voice (~850ms), DQI, OSINT |
| **Trinetra** | **P0 (Highest)** | [GitHub](https://github.com/UtkarshSingh-09/Trinetra-Agent) • **Patent Filed** | Credit Intelligence OS, 14 Agents × 14 Qdrant Collections, 60s CAM |
| **RudraKernel** | **P0 (Highest)** | [GitHub](https://github.com/UtkarshSingh-09/RudraKernel) • [Live HF Space](https://huggingface.co/spaces/UtkarshSingh09/RudraKernel-env) | OpenEnv India 2026, RL LLM Reliability, SIEGE, R1–R9 Rewards |
| **MerchantMind** | **P0 (Highest)** | [GitHub](https://github.com/UtkarshSingh-09/MerchentMind-) • [Live](https://merchantmind-ai.netlify.app) • [Video](https://youtu.be/hS77jr1y1z4) | Razorpay Buildathon '26, 2PC Checkout Saga, Deepgram Voice, <650ms |
| **AstraGuard** | **P1** | [GitHub](https://github.com/UtkarshSingh-09/AstraGuard) • [Live Demo](https://astra-guard.vercel.app/) | Behavioral Fintech, LangGraph, Form 16/CAS Ingestion, Twilio Alerts |
| **Madad AI** | **P1** | [GitHub](https://github.com/UtkarshSingh-09/MadadAI) | Offline Mesh Network, DTN Store-and-Forward, Sockets, AES-128, Qdrant |

These are pinned as `include: true` in `data/config/projects_override.yaml` with pre-grounded `manual_notes`.

---

## Build Phases (from spec §12)

| Phase | What | Acceptance Criteria |
|---|---|---|
| **1. Foundation** | Repo, pyproject.toml, config, DB + migrations, logging, CLI skeleton | `resume-agent init` creates DB; all tables exist |
| **2. Identity** | Resume parser, GitHub sync, quality scorer, override file | Profile populated + confirmed; ≥30 projects synced with scores |
| **3. Job Ingestion** | Detector + Greenhouse/Lever/Ashby adapters + normalize/dedupe/filter | ≥200 companies resolved; daily run yields ≥20 filtered internships; 0 dupes on re-run |
| **4. Matching** | Embeddings, retrieval, LLM selection | On 10 hand-labelled JDs, top-3 agrees with user's choice on ≥7 |
| **5. Generation** | LaTeX template, bullet writer, grounding verifier | Golden-set hallucination test 15/15; PDF compiles; 1 page |
| **6. Validation** | Parse-back, keyword coverage, retry loop | 10/10 PDFs parse-back clean; ≥8/10 reach coverage ≥90 |
| **7. Automation** | Scheduler, Telegram delivery, run log, circuit breakers, weekly report | 7 consecutive unattended daily runs |
| **8. Full Coverage** | Remaining adapters + Tier 3 fallback + auto-apply | All providers working; auto-apply with guardrails |

---

## File Count Summary

| Category | Files |
|---|---|
| Source modules | 33 |
| Tests | 12 |
| Config/Data | 8 |
| Templates | 1 |
| CI/CD | 1 |
| Docs | 4 |
| **Total** | **~59 files** |
