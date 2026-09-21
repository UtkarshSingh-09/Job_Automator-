# 🏗️ 10-Phase Execution Plan — Resume Agent

> **Rule:** After each phase is complete, we `git add . && git commit && git push`.  
> **Rule:** After each phase, a `progress/phase_XX_done.md` file is created documenting what was built, what works, and what the user needs to do manually.  
> **Rule:** If chat/memory is lost, read everything inside `progress/` to know exactly where we left off.

---

## Quick Status Board

| Phase | Name | Status | Commit Tag |
|:---:|---|:---:|:---:|
| 1 | Foundation & Project Skeleton | ⬜ Not Started | `phase-1-foundation` |
| 2 | Profile Extraction & Identity | ⬜ Not Started | `phase-2-identity` |
| 3 | GitHub Sync & Portfolio Corpus | ⬜ Not Started | `phase-3-github` |
| 4 | Company Database & ATS Detection | ⬜ Not Started | `phase-4-companies` |
| 5 | Job Ingestion & Filtering Pipeline | ⬜ Not Started | `phase-5-ingestion` |
| 6 | Semantic Matching Engine | ⬜ Not Started | `phase-6-matching` |
| 7 | Bullet Writer & LaTeX Renderer | ⬜ Not Started | `phase-7-generation` |
| 8 | ATS Validation Suite | ⬜ Not Started | `phase-8-validation` |
| 9 | Telegram Delivery & Automation | ⬜ Not Started | `phase-9-automation` |
| 10 | Auto-Apply Engine | ⬜ Not Started | `phase-10-autoapply` |

---

## Phase 1 — Foundation & Project Skeleton

### What Gets Built
- `pyproject.toml` with all dependencies (uv managed)
- `src/resume_agent/__init__.py`, `config.py`, `db.py`, `models.py`, `logging.py`
- `src/resume_agent/cli.py` — Click-based CLI entrypoint
- `migrations/001_init.sql` — Full SQLite schema (profile, projects, companies, jobs, matches, applications, run_log)
- `.env.example` — Template with all required env vars
- `.gitignore` — Ignore `.env`, `*.db`, `data/output/`, `__pycache__/`
- `README.md` — Project overview with setup instructions
- `progress/` folder structure

### Acceptance Test
```bash
uv run resume-agent init
# → Creates data/agent.db with all 7 tables
# → Prints "✅ Database initialized successfully"
```

### 🔧 Manual Steps After Phase 1
| What | Why | How |
|---|---|---|
| Install `uv` | Python package manager | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Install `tectonic` | LaTeX→PDF compiler | `brew install tectonic` (macOS) |
| Copy `.env.example` → `.env` | Config file | `cp .env.example .env` |
| Get Anthropic API Key | Powers LLM matching & bullet writing | [console.anthropic.com](https://console.anthropic.com/) → Create key → paste into `.env` |

### Git Checkpoint
```bash
git add . && git commit -m "Phase 1: Foundation — project skeleton, DB schema, CLI" && git tag phase-1-foundation && git push --tags
```

---

## Phase 2 — Profile Extraction & Identity

### What Gets Built
- `src/resume_agent/profile/parser.py` — Extract old resume PDF → structured profile JSON
- `src/resume_agent/profile/confirm.py` — Human confirmation gate (CLI prompt)
- `data/input/old_resume.pdf` — Copy of `GDG_resume.pdf`
- Profile insertion into SQLite with `confirmed_at` timestamp

### Acceptance Test
```bash
uv run resume-agent profile parse
# → Extracts name, email, phone, CGPA, college, skills from PDF
# → Prints structured profile for human review
# → User confirms → profile.confirmed_at is set

uv run resume-agent profile show
# → Displays confirmed profile
```

### 🔧 Manual Steps After Phase 2
| What | Why | How |
|---|---|---|
| Review the extracted profile | Verify CGPA (8.78), phone, email are correct | Run `resume-agent profile parse` and confirm at prompt |
| Fix any wrong fields | System refuses to generate resumes if profile has errors | Edit via `resume-agent profile edit` or re-parse with `--force` |

### Git Checkpoint
```bash
git add . && git commit -m "Phase 2: Identity — profile parser, confirmation gate" && git tag phase-2-identity && git push --tags
```

---

## Phase 3 — GitHub Sync & Portfolio Corpus

### What Gets Built
- `src/resume_agent/github/client.py` — GitHub REST API client (repos, READMEs, languages, commits)
- `src/resume_agent/github/scorer.py` — Deterministic quality scoring (0–100)
- `data/config/projects_override.yaml` — Pin priority for Aegis Forge, Trinetra, RudraKernel, MerchantMind + manual_notes
- Projects table populated with quality scores and metadata

### Acceptance Test
```bash
uv run resume-agent github sync
# → Fetches all public repos for UtkarshSingh-09
# → Computes quality scores
# → Merges with projects_override.yaml
# → ≥6 projects stored in DB with scores

uv run resume-agent projects list
# → Shows all synced projects with quality scores and priorities
```

### 🔧 Manual Steps After Phase 3
| What | Why | How |
|---|---|---|
| Create GitHub Fine-Grained PAT | System needs to read your repos | [github.com/settings/tokens](https://github.com/settings/tokens?type=beta) → Generate token → Permissions: Contents (Read-only) → Paste into `.env` as `GITHUB_TOKEN=ghp_xxx` |
| Review `projects_override.yaml` | Verify manual_notes and priority pinning | Open file, ensure metrics/descriptions match reality |
| Run `resume-agent github sync` | Populate the projects database | Execute and verify ≥6 projects synced |

### Git Checkpoint
```bash
git add . && git commit -m "Phase 3: GitHub sync — repo fetcher, quality scorer, project corpus" && git tag phase-3-github && git push --tags
```

---

## Phase 4 — Company Database & ATS Detection

### What Gets Built
- `data/config/companies.yaml` — Seed list of 300–600 companies with domains
- `src/resume_agent/jobs/discovery/detector.py` — ATS detection engine (Greenhouse, Lever, Ashby, Workable, Recruitee, SmartRecruiters)
- `src/resume_agent/jobs/discovery/resolver.py` — Domain → ATS slug resolution
- Companies table populated with detected ATS providers

### Acceptance Test
```bash
uv run resume-agent companies detect --limit 50
# → Tests 50 companies from seed list
# → Detects ATS provider and slug for each
# → Prints summary: X resolved, Y unknown, Z dead

uv run resume-agent companies list --status resolved
# → Shows companies with confirmed ATS endpoints
```

### 🔧 Manual Steps After Phase 4
| What | Why | How |
|---|---|---|
| Review resolved companies | Verify ATS detection accuracy | Run `resume-agent companies list` and spot-check a few |
| Add custom companies | If you have specific target companies | Edit `data/config/companies.yaml` and re-run detect |
| Nothing else! | This phase is fully automated | — |

### Git Checkpoint
```bash
git add . && git commit -m "Phase 4: Company DB — 300+ companies, ATS auto-detection" && git tag phase-4-companies && git push --tags
```

---

## Phase 5 — Job Ingestion & Filtering Pipeline

### What Gets Built
- `src/resume_agent/jobs/sources/base.py` — Abstract `JobSource` protocol
- `src/resume_agent/jobs/sources/greenhouse.py` — Greenhouse adapter
- `src/resume_agent/jobs/sources/lever.py` — Lever adapter
- `src/resume_agent/jobs/sources/ashby.py` — Ashby adapter
- `src/resume_agent/jobs/sources/workable.py` — Workable adapter
- `src/resume_agent/jobs/sources/recruitee.py` — Recruitee adapter
- `src/resume_agent/jobs/sources/smartrecruiters.py` — SmartRecruiters adapter
- `src/resume_agent/jobs/pipeline/normalize.py` — Field normalization
- `src/resume_agent/jobs/pipeline/dedupe.py` — SHA-256 content hashing dedup
- `src/resume_agent/jobs/pipeline/filter.py` — Internship/experience-level filter regex
- Jobs table populated with filtered, deduplicated listings

### Acceptance Test
```bash
uv run resume-agent jobs fetch --dry-run --limit 50
# → Fetches from all resolved ATS endpoints
# → Normalizes and deduplicates
# → Filters for internships only
# → Shows count: X total → Y after dedup → Z after filter

uv run resume-agent jobs fetch
# → Actually persists to DB
# → Re-run produces zero new duplicates
```

### 🔧 Manual Steps After Phase 5
| What | Why | How |
|---|---|---|
| (Optional) Get Adzuna API keys | For additional job aggregator coverage | [developer.adzuna.com](https://developer.adzuna.com/) → Sign up → Paste `ADZUNA_APP_ID` and `ADZUNA_APP_KEY` into `.env` |
| Verify filter accuracy | Ensure no senior roles slip through | Run `resume-agent jobs list --recent 10` and check titles |
| Nothing else required! | All adapters auto-discover from Phase 4 data | — |

### Git Checkpoint
```bash
git add . && git commit -m "Phase 5: Job ingestion — 6 ATS adapters, dedup, intern filter" && git tag phase-5-ingestion && git push --tags
```

---

## Phase 6 — Semantic Matching Engine

### What Gets Built
- `src/resume_agent/matcher/embed.py` — `bge-small-en-v1.5` embedding (384-dim, runs locally)
- `src/resume_agent/matcher/retrieve.py` — Cosine similarity → Top 8 candidate projects
- `src/resume_agent/matcher/select.py` — Claude Sonnet final selection (top 3 from 8)
- `data/gazetteer/skills.yaml` — Tech skills vocabulary for grounding
- Matches table populated with fit scores and selected projects

### Acceptance Test
```bash
uv run resume-agent match --job-id <any_job_id>
# → Embeds job description + project corpus
# → Retrieves top 8 candidates via cosine similarity
# → Claude selects best 3 with fit score
# → Prints selection reasoning and fit score

# Test with 10 different jobs:
uv run resume-agent match --test-suite
# → ≥7/10 selections match human-expected choices
```

### 🔧 Manual Steps After Phase 6
| What | Why | How |
|---|---|---|
| Verify Anthropic API Key works | Claude Sonnet is used for smart selection | Run any match command — if it errors with auth, check `.env` |
| Review a few match results | Ensure the right projects are being picked | Run `resume-agent match --job-id X` for 3-4 jobs and check if project selection makes sense |
| Nothing else! | Embedding model downloads automatically on first run | — |

### Git Checkpoint
```bash
git add . && git commit -m "Phase 6: Matching — embeddings, cosine retrieval, Claude selection" && git tag phase-6-matching && git push --tags
```

---

## Phase 7 — Bullet Writer & LaTeX Renderer

### What Gets Built
- `src/resume_agent/writer/prompts.py` — Structured LLM prompts for bullet generation
- `src/resume_agent/writer/generate.py` — Generate 3 bullets per project in JD vocabulary
- `src/resume_agent/writer/verify.py` — Anti-hallucination grounding verifier (zero fabricated tech/metrics)
- `src/resume_agent/render/escape.py` — LaTeX special character escaper
- `src/resume_agent/render/latex.py` — Jinja2 → LaTeX → `tectonic` → PDF pipeline
- `templates/resume.tex.j2` — ATS-safe single-page LaTeX template (glyphtounicode, anti-hyphenation)
- PDF output to `data/output/{YYYY-MM-DD}/{company}__{title}.pdf`

### Acceptance Test
```bash
uv run resume-agent generate --job-id <any_job_id>
# → Generates tailored bullets
# → Passes grounding verification (zero hallucinations)
# → Compiles to single-page PDF via tectonic
# → PDF saved to data/output/

# Anti-hallucination test suite:
uv run resume-agent test-grounding
# → 15/15 golden-set tests pass (no fabricated technologies)
```

### 🔧 Manual Steps After Phase 7
| What | Why | How |
|---|---|---|
| Verify `tectonic` is installed | Required for PDF compilation | `tectonic --version` — if not found: `brew install tectonic` |
| Review a generated PDF | Check visual quality, formatting, page count | Open any PDF from `data/output/` — should be exactly 1 page, clean layout, no broken characters |
| Check for hallucinations | Critical — resume must be 100% truthful | Compare PDF content against `PROJECTS_PORTFOLIO.md` — no tech/metric should appear that isn't in the source |

### Git Checkpoint
```bash
git add . && git commit -m "Phase 7: Generation — bullet writer, grounding verifier, LaTeX→PDF" && git tag phase-7-generation && git push --tags
```

---

## Phase 8 — ATS Validation Suite

### What Gets Built
- `src/resume_agent/validate/parseback.py` — Extract PDF text, assert 100% field recovery
- `src/resume_agent/validate/keywords.py` — JD keyword coverage score (≥90% target)
- `src/resume_agent/validate/hygiene.py` — Unicode integrity, page count, reading order, glyph checks
- `src/resume_agent/validate/runner.py` — 7-gate validation pipeline orchestrator
- Retry loop: if coverage <90%, re-generate with missing keywords highlighted (max 3 attempts)

### Acceptance Test
```bash
uv run resume-agent validate --pdf data/output/2026-09-22/some_company__sde_intern.pdf
# → Runs all 7 validation gates
# → Reports: parse-back ✅, reading order ✅, unicode ✅, page count ✅, keyword coverage 94% ✅

# Batch test:
uv run resume-agent validate --all-recent
# → 10/10 PDFs pass all gates
```

### 🔧 Manual Steps After Phase 8
| What | Why | How |
|---|---|---|
| Nothing! | This phase is fully automated validation | Just review the test results |
| (Optional) Test with online ATS checker | Extra confidence | Upload a generated PDF to [resumeworded.com](https://resumeworded.com) or [jobscan.co](https://jobscan.co) and check score |

### Git Checkpoint
```bash
git add . && git commit -m "Phase 8: Validation — 7-gate ATS verification suite" && git tag phase-8-validation && git push --tags
```

---

## Phase 9 — Telegram Delivery & Automation (n8n Visual Workflow Engine)

### What Gets Built
- `src/resume_agent/deliver/telegram.py` — Telegram Bot API: send text messages, PDFs, screenshots
- `src/resume_agent/orchestrate/daily.py` — Full daily pipeline orchestrator (fetch → match → generate → validate → deliver)
- `n8n/workflows/daily_pipeline.json` — n8n visual workflow definition (Schedule Trigger 09:00 IST → Execute CLI → Condition → Telegram delivery)
- Daily digest: morning summary with all matches, PDFs attached, apply links
- Real-time alerts: instant notification per successful generation
- Error branch: instant visual error alerts on pipeline issues

### Acceptance Test
```bash
# Local CLI test:
uv run resume-agent daily --dry-run
# → Runs full pipeline locally
# → Sends test Telegram message with PDF attached

# n8n Visual Workflow test:
# Open n8n UI (http://localhost:5678 or deployed container) → Click "Execute Workflow" → verify visual node execution & Telegram alert
```

### 🔧 Manual Steps After Phase 9 (⚠️ MOST MANUAL STEPS)
| What | Why | How |
|---|---|---|
| **Create Telegram Bot** | Delivery channel for notifications | 1. Open Telegram → search `@BotFather` → `/newbot` → name it `ResumeAgentBot` → copy the token |
| **Get your Chat ID** | Bot needs to know where to send messages | Message `@userinfobot` on Telegram → it replies with your chat ID (a number like `123456789`) |
| **Paste into `.env`** | Connect bot to pipeline | `TELEGRAM_BOT_TOKEN=your_token_here` and `TELEGRAM_CHAT_ID=your_id_here` |
| **Start n8n** | Visual workflow automation engine | Run `npx n8n` on Mac (opens `http://localhost:5678`) or deploy to Railway/Render/Oracle Free Cloud |
| **Import Workflow** | Load visual pipeline into n8n | In n8n UI → Click "Import from File" → select `n8n/workflows/daily_pipeline.json` |
| **Activate Workflow** | Start the daily 9:00 AM visual schedule | Toggle the "Active" switch to ON in the n8n canvas |

### Git Checkpoint
```bash
git add . && git commit -m "Phase 9: Automation — Telegram delivery, daily pipeline, n8n visual workflow" && git tag phase-9-automation && git push --tags
```

---

## Phase 10 — Auto-Apply Engine

### What Gets Built
- `src/resume_agent/apply/api_submit.py` — Direct API submission (Greenhouse, Lever, Workable)
- `src/resume_agent/apply/browser_submit.py` — Playwright headless Chromium for custom forms
- `src/resume_agent/apply/manager.py` — Apply orchestrator with safety guards
- `migrations/002_auto_apply.sql` — Applications table migration
- Safety: max 10 auto-applies/day, 3-min cooldown, no CAPTCHA, no account creation
- Confirmation screenshots saved + sent via Telegram
- `--dry-run` mode: fills forms and screenshots without submitting

### Acceptance Test
```bash
# Dry-run test (fills form but doesn't submit):
uv run resume-agent apply --job-id <id> --dry-run
# → Opens headless browser
# → Fills application form
# → Takes screenshot → saves to data/output/screenshots/
# → Sends screenshot to Telegram
# → Does NOT click submit

# Live test (with a real job you want to apply to):
uv run resume-agent apply --job-id <id>
# → Submits application
# → Sends Telegram confirmation: "✅ Applied to {company} — {title}"
```

### 🔧 Manual Steps After Phase 10
| What | Why | How |
|---|---|---|
| Install Playwright browser | Needed for form automation | `uv run playwright install chromium --with-deps` |
| Test with `--dry-run` first | Verify form filling works correctly | Run `resume-agent apply --job-id X --dry-run` and check the screenshot |
| Review the first few real applications | Build trust in the system | Watch the Telegram notifications, verify the right jobs were applied to |
| Adjust daily limits if needed | Default: 10/day | Edit `.env`: `MAX_DAILY_APPLIES=10` (increase/decrease as you see fit) |

### Git Checkpoint
```bash
git add . && git commit -m "Phase 10: Auto-Apply — API submit, Playwright automation, safety guards" && git tag phase-10-autoapply && git push --tags
```

---

## 📁 Progress Tracking

The `progress/` folder tracks exactly what's been completed:

```
progress/
├── phase_01_done.md    ← Created after Phase 1 is complete
├── phase_02_done.md    ← Created after Phase 2 is complete
├── ...
├── phase_10_done.md    ← Created after Phase 10 is complete
└── CURRENT_STATUS.md   ← Always shows the latest state
```

Each `phase_XX_done.md` contains:
- ✅ What was built (files created/modified)
- ✅ What tests passed
- ✅ What commit/tag it corresponds to
- ⚠️ Any manual steps the user still needs to complete
- 📝 Notes for resuming work if context is lost

### If Chat/Memory is Lost
1. Read `progress/CURRENT_STATUS.md` → tells you which phase you're on
2. Read the latest `progress/phase_XX_done.md` → tells you what's complete
3. Read `PHASES.md` (this file) → tells you what to build next
4. Read `REQUIREMENTS.md` → full system requirements
5. Read `RESUME_AGENT_SPEC.md` → detailed technical spec
6. Read `PROJECT_ARCHITECTURE.md` → file tree and module composition
7. Start from the next incomplete phase

---

## 📊 Cost Summary (All Phases Complete)

| Resource | Monthly Cost |
|---|---|
| Claude Sonnet API (15 resumes/day) | ~₹400–500 |
| n8n (Self-Hosted Community Edition) | Free (Open-source, unlimited runs) |
| Telegram Bot | Free |
| SQLite database | Free (local file) |
| `tectonic` LaTeX | Free (open source) |
| **Total** | **< ₹600/month** |

---

## 🚀 Ready to Start

**Next step:** Begin Phase 1 — Foundation & Project Skeleton.

Before Phase 1, you need:
- [x] System Spec ready (`RESUME_AGENT_SPEC.md`)
- [x] Architecture mapped (`PROJECT_ARCHITECTURE.md`)
- [x] Project portfolio documented (`PROJECTS_PORTFOLIO.md`)
- [x] ATS research complete (`ATS_RESUME_RESEARCH.md`)
- [x] Requirements defined (`REQUIREMENTS.md`)
- [x] Phase plan created (`PHASES.md` — this file)
- [ ] `.env` with `ANTHROPIC_API_KEY` (needed from Phase 2 onwards)
