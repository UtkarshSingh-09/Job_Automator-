# Autonomous Internship-Matching & Resume Generation System

**Spec version:** 1.0
**Audience:** Coding agent (Claude Code / Cursor / equivalent)
**Owner:** Single user (student, India, seeking SDE/ML internships)

---

## 0. How to read this document

This is an implementation specification, not a suggestion. Where a decision has
already been made (library, schema, endpoint), implement it as written. Where a
section is marked `[DECISION]`, you may choose, but record your choice in
`docs/decisions.md`.

Build in the phase order given in §12. Do not build ahead. Each phase must pass
its acceptance test before the next begins.

---

## 1. Problem statement

The user has ~40 GitHub repositories, of which ~7 are substantial enough to put
on a resume. Manually tailoring a resume for each internship application is slow
and inconsistent.

The system must, without human intervention:

1. Poll internship/entry-level openings from startups and large companies daily.
2. Score each opening against the user's actual project portfolio.
3. For a good match, select the **3 most relevant projects**.
4. Rewrite those project bullets in the vocabulary of that specific job description.
5. Render a single-page, ATS-parseable PDF.
6. Validate the PDF mechanically, and regenerate if validation fails.
7. Deliver the PDF plus the apply link to the user.

The system automatically submits applications where possible and notifies the
user via Telegram after each submission (see §6.11).

---

## 2. Success criteria

| Criterion | Target |
|---|---|
| Job ingestion coverage | ≥ 300 companies polled daily |
| Ingestion runtime | < 10 min for full daily sweep |
| Parse-back fidelity (see §9) | 100% of fields recovered, correct order |
| JD keyword coverage (see §9) | ≥ 90% of extracted hard requirements |
| Hallucination rate | 0 — no tech/metric in output absent from source |
| End-to-end latency per resume | < 60 s |
| Monthly running cost | < ₹600 |

---

## 3. Explicit non-goals

Do not build these. They were evaluated and rejected.

| Non-goal | Reason |
|---|---|
| LinkedIn job scraping | No public jobs API. Scraping risks account restriction on the user's primary professional account. |
| LinkedIn profile connector | Same. Use the user's one-time LinkedIn **data export** (ZIP) instead. |
| Querying a real "ATS score" API | No such thing exists. Workday, Greenhouse, Taleo, iCIMS do not expose a 0–100 score to applicants. The "90+ score" target is satisfied by our own validator (§9). |
| Per-site HTML scrapers for custom career pages | Infinite maintenance. Use the LLM extraction fallback (§6.4) instead. |
| Multi-user / SaaS features | Single-user system. No auth layer, no tenancy. |

---

## 4. Architecture

```
                        ┌────────────────────────┐
                        │  ONE-TIME BOOTSTRAP    │
                        │  • parse old resume    │
                        │  • ingest GitHub repos │
                        │  • detect ATS slugs    │
                        └───────────┬────────────┘
                                    │  writes
                                    ▼
┌──────────────┐          ┌──────────────────┐
│ ATS adapters │─────────▶│                  │
│ (greenhouse, │          │                  │
│  lever, …)   │          │   SQLite / PG    │
├──────────────┤          │                  │
│ Aggregators  │─────────▶│  profile         │
│ (adzuna, …)  │          │  projects        │
└──────────────┘          │  companies       │
                          │  jobs            │
      DAILY CRON ────────▶│  matches         │
                          │  applications    │
                          └────────┬─────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │  normalize → dedupe → filter│
                    └──────────────┬──────────────┘
                                   ▼
                    ┌─────────────────────────────┐
                    │  MATCHER                    │
                    │  embeddings → top-8 projects│
                    │  LLM → final 3 + reasoning  │
                    └──────────────┬──────────────┘
                                   ▼
                    ┌─────────────────────────────┐
                    │  BULLET WRITER (LLM)        │
                    │  strict grounding contract  │
                    └──────────────┬──────────────┘
                                   ▼
                    ┌─────────────────────────────┐
                    │  RENDERER                   │
                    │  Jinja2 → LaTeX → PDF       │
                    └──────────────┬──────────────┘
                                   ▼
                    ┌─────────────────────────────┐
                    │  VALIDATOR            ◀─┐   │
                    │  parse-back + keywords  │   │
                    │  fail → retry (max 3) ──┘   │
                    └──────────────┬──────────────┘
                                   ▼
                    ┌─────────────────────────────┐
                    │  DELIVERY: email / Telegram │
                    └─────────────────────────────┘
```

---

## 5. Tech stack

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.11+ | Ecosystem for PDF, embeddings, HTTP |
| Package manager | `uv` | Fast, lockfile, reproducible |
| HTTP client | `httpx` (async) | Connection pooling, HTTP/2, timeouts |
| Retry/backoff | `tenacity` | Declarative |
| DB | SQLite via `sqlite3` + raw SQL | Single user, zero ops. Schema is Postgres-compatible for later migration. |
| Migrations | Plain numbered `.sql` files in `migrations/` | No ORM overhead |
| Validation | `pydantic` v2 | Every external payload is parsed into a model before it touches the DB |
| Resume parsing (input) | `pymupdf` (fitz) | Fast, accurate text + layout |
| GitHub | `httpx` against REST v3 | `PyGithub` is heavier than needed |
| Embeddings | `sentence-transformers`, model `BAAI/bge-small-en-v1.5` | Runs locally on CPU, free, 384-dim, strong on short technical text |
| Vector store | `sqlite-vec` extension, or numpy brute force | ~40 projects. Brute force is fine. Do not add a vector DB. |
| LLM | Anthropic API, `claude-sonnet-4-6` | Selection + bullet rewriting |
| Templating | `Jinja2` | LaTeX generation |
| PDF render | `tectonic` | Self-contained LaTeX engine, single binary, no TeXLive install |
| PDF validate | `pymupdf` | Text extraction for parse-back |
| Keyword extraction | `spacy` `en_core_web_sm` + curated skill gazetteer | Deterministic; do not use an LLM for this — it must be reproducible |
| Scheduler | GitHub Actions cron (free) | Best fit: free, no infra to maintain, built-in secrets management. |
| Delivery | Telegram Bot API via `python-telegram-bot` | Instant push notifications, inline buttons, PDF file sharing. |
| Config | `pydantic-settings` + `.env` + `companies.yaml` | |
| Logging | `structlog`, JSON to stdout | |
| Tests | `pytest`, `pytest-asyncio`, `respx` for HTTP mocks | |
| Lint/format | `ruff` | |

### On n8n

n8n is acceptable **only** as the scheduler and notification layer. The
matching, rendering, and validation logic must live in Python modules invoked as
a CLI. Do not implement business logic inside n8n code nodes — it is
untestable, unversionable, and slower than plain Python.

---

## 6. Modules

### 6.1 `profile/` — one-time identity ingestion

**Input:** the user's existing resume PDF at `data/input/old_resume.pdf`,
optionally a LinkedIn data export ZIP.

**Task:** extract to `profile` table, then **stop and print the parsed JSON for
human confirmation**. Do not proceed automatically — a wrong CGPA propagates to
every resume forever.

Extract: `full_name, email, phone, github_url, linkedin_url, portfolio_url,
college, degree, branch, grad_year, cgpa, location, skills[], coursework[],
achievements[], certifications[]`.

Method: `pymupdf` text extraction → single LLM call with a strict JSON schema →
write to DB. Store the raw extracted text in `profile.raw_text` for audit.

**Acceptance:** re-running is idempotent; a `--force` flag re-parses.

---

### 6.2 `github/` — project corpus

Authenticate with a fine-grained PAT, scope `public_repo` read only.

For each repo owned by the user (exclude forks unless `fork_contributions > 20`):

```
GET /user/repos?per_page=100&affiliation=owner
GET /repos/{owner}/{repo}/readme        → base64 decode
GET /repos/{owner}/{repo}/languages     → byte counts per language
GET /repos/{owner}/{repo}/commits?author={user}&per_page=1  → use Link header for count
GET /repos/{owner}/{repo}/topics
```

Store per project:

```
name, description, readme_md, languages{}, primary_language,
topics[], stars, commit_count, created_at, pushed_at, is_fork,
has_tests (bool: detect test dir/file patterns),
has_ci     (bool: .github/workflows exists),
has_docker (bool: Dockerfile exists),
line_count (approx, from languages byte sum / 30)
```

Then compute `quality_score` (0–100), a deterministic heuristic:

```
readme_length_norm   × 25
commit_count_norm    × 20   (log-scaled, cap at 100 commits)
has_tests            × 15
has_ci               × 10
has_docker           ×  5
language_diversity   × 10
recency              × 10   (decay over 24 months)
stars_norm           ×  5   (log-scaled)
```

**User override:** `data/config/projects_override.yaml` lets the user pin
`include: true/false` and supply `manual_notes` (things not in the README —
metrics, scale, outcomes). Manual notes are **part of the grounding corpus**
(§6.6) and are the correct place to add real numbers the README lacks.

Refresh weekly.

---

### 6.3 `jobs/discovery/` — ATS detection (one-time + monthly)

**Input:** `data/config/companies.yaml`:

```yaml
companies:
  - name: Razorpay
    domain: razorpay.com
    tier: 1
  - name: Zerodha
    domain: zerodha.com
    tier: 1
```

Seed this list from: YC company directory, Wellfound browse pages, a list of
Indian unicorns/soonicorns, and the user's own target list. Aim for 300–600.

**Algorithm per company:**

1. `GET https://{domain}/careers`, then `/jobs`, `/join-us`, `/company/careers`.
   Follow redirects (max 5). Timeout 10 s.
2. Regex the final URL **and** the response body:

```python
ATS_PATTERNS = {
    "greenhouse":     r"(?:boards|job-boards)\.greenhouse\.io/(?:embed/job_board\?for=)?([\w-]+)",
    "lever":          r"jobs\.lever\.co/([\w-]+)",
    "ashby":          r"jobs\.ashbyhq\.com/([\w-]+)",
    "workable":       r"apply\.workable\.com/([\w-]+)",
    "recruitee":      r"([\w-]+)\.recruitee\.com",
    "smartrecruiters":r"careers\.smartrecruiters\.com/([\w-]+)",
    "teamtailor":     r"([\w-]+)\.teamtailor\.com",
    "personio":       r"([\w-]+)\.jobs\.personio\.(?:de|com)",
}
```

3. **Validate** the candidate slug by calling the ATS endpoint once. Only persist
   if it returns ≥ 1 job.
4. On failure, mark `ats_provider = 'unknown'` and set `needs_manual_review`.

Expect 60–75% auto-resolution. Emit `reports/unresolved_companies.csv` for the
user to fill in manually. Re-run monthly with `--refresh` to catch ATS switches.

---

### 6.4 `jobs/sources/` — ingestion adapters

Every adapter implements:

```python
class JobSource(Protocol):
    name: str
    async def fetch(self, client: httpx.AsyncClient, ref: SourceRef) -> list[RawJob]: ...
    def normalize(self, raw: RawJob) -> Job: ...
```

**Tier 1 — ATS endpoints (primary, high quality):**

| Provider | Endpoint |
|---|---|
| Greenhouse | `https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true` |
| Lever | `https://api.lever.co/v0/postings/{slug}?mode=json` |
| Ashby | `https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true` |
| Workable | `https://apply.workable.com/api/v1/accounts/{slug}?details=true` |
| Recruitee | `https://{slug}.recruitee.com/api/offers/` |
| SmartRecruiters | `https://api.smartrecruiters.com/v1/companies/{slug}/postings` |

No authentication required for read. Greenhouse's board endpoints are public and
not rate-limited; be polite to the others regardless.

**Tier 2 — aggregators (breadth, noisier):**
Adzuna (free tier, covers India), Arbeitnow (no key), Jooble, Findwork.
Treat these as a **discovery feed** — when they surface a company not in
`companies.yaml`, append it to `reports/new_company_candidates.csv` for the next
detection run.

**Tier 3 — LLM extraction fallback (weekly, tier-1 companies only):**
For companies where `ats_provider = 'unknown'` **and** `tier = 1`:
fetch the careers page, strip to plain text (`trafilatura`), send to the LLM with
a strict JSON schema. Cap at 40 companies/week. Log cost per call.

**Not implemented:** Internshala and Naukri (no API, ToS prohibits scraping).
The user checks these manually. Emit a reminder in the weekly digest.

**Politeness rules — non-negotiable:**
- Global concurrency ≤ 8; per-host concurrency = 1.
- `User-Agent: resume-agent/1.0 (+{user_github_url}; personal job search)`
- Honour `robots.txt` via `urllib.robotparser` for Tier 3.
- Cache with `If-None-Match` / `If-Modified-Since`; store ETags in `companies`.
- Exponential backoff on 429/5xx, max 3 retries.

---

### 6.5 `jobs/pipeline/` — normalize, dedupe, filter

**Normalized `Job` model:**

```python
company: str
title: str
location: str | None
remote_type: Literal["onsite","hybrid","remote","unknown"]
description_md: str          # HTML stripped, markdown-ish
apply_url: str
posted_at: datetime | None
source: str                  # "greenhouse" | "adzuna" | ...
source_job_id: str
content_hash: str
```

**Dedupe:** `content_hash = sha256(norm(company) + norm(title) + norm(location))`
where `norm` lowercases, strips punctuation, and collapses whitespace.
Aggregators re-surface jobs already pulled directly from the ATS — direct
sources win on conflict (fresher, fuller description).

**Filter — must pass all:**

```python
INCLUDE = r"\b(intern|internship|trainee|graduate|campus|entry.?level|fresher|new.?grad|sde.?[01]|associate (software )?engineer)\b"
EXCLUDE = r"\b(senior|staff|principal|lead|manager|director|architect|head of|\d+\+?\s*years?)\b"
```

Location: India, or `remote_type == "remote"` with no geo restriction
conflicting with India. Posted within 30 days. Not already in `applications`.

---

### 6.6 `matcher/` — project selection

**Stage A — retrieval (local, free, deterministic):**

For each project, build the embedding text as:
`name + description + topics + first 1200 chars of README + manual_notes`.
Embed with `bge-small-en-v1.5`. Cache embeddings in `projects.embedding` (BLOB);
invalidate on `pushed_at` change.

Embed the JD (title + requirements section, truncated to 1500 chars).
Cosine similarity → take **top 8**.

**Stage B — selection (LLM):**

Single call. Input: the JD, and the 8 candidates with full README + manual notes.
Output schema:

```json
{
  "overall_fit": 0-100,
  "selected": [
    {"project_id": 12, "rank": 1, "why": "…", "jd_requirements_covered": ["…"]}
  ],
  "uncovered_requirements": ["…"],
  "recommend_apply": true
}
```

If `overall_fit < 55`, skip the job. Log it; do not generate a resume.

---

### 6.7 `writer/` — bullet generation

**This is the highest-risk module.** The model will want to embellish. A
fabricated claim ("architected a scalable microservices platform" for a CRUD
app) will be caught in an interview and is worse than a weaker resume.

**Grounding contract, enforced in the prompt and verified in code:**

```
You are rewriting resume bullets for ONE project.

SOURCE OF TRUTH (the only facts you may use):
<project>{readme}{manual_notes}{languages}{topics}</project>

TARGET JOB:
<jd>{description}</jd>

RULES — violating any is a failure:
1. Every technology, framework, tool, number, percentage, and scale figure in
   your output MUST appear verbatim in SOURCE OF TRUTH. Never introduce one.
2. If the JD wants a technology the project does not use, do NOT add it.
   Report it in `unmet` instead.
3. You MAY reorder, re-emphasise, and rephrase to match JD vocabulary.
4. Use past tense, strong verbs, no first person, no articles where droppable.
5. 3 bullets, each 14–26 words, each on a single line.
6. Output JSON only: {"bullets": [...], "tech_used": [...], "unmet": [...]}
```

**Post-generation verifier (code, not LLM) — mandatory:**

```python
def verify_grounding(bullets, source_text, skill_gazetteer):
    out_tokens  = extract_tech_tokens(" ".join(bullets), skill_gazetteer)
    src_tokens  = extract_tech_tokens(source_text, skill_gazetteer)
    hallucinated = out_tokens - src_tokens
    numbers = re.findall(r"\d[\d,.]*%?", " ".join(bullets))
    ungrounded_numbers = [n for n in numbers if n not in source_text]
    return hallucinated, ungrounded_numbers
```

If either set is non-empty → reject, retry with the offending tokens named
explicitly. After 2 failed retries, fall back to the project's generic bullets
stored in `projects_override.yaml` and flag the resume for manual review.

---

### 6.8 `render/` — PDF generation

Jinja2 → LaTeX → `tectonic`.

**ATS-safe template rules — these are the actual reason resumes get rejected:**

- **Single column.** No `multicol`, no `tabular` for layout, no text boxes.
- **No images, icons, logos, or glyph fonts.** No FontAwesome. Contact line is
  plain text.
- **No headers/footers.** Some parsers drop them.
- Standard section headings, exactly: `EDUCATION`, `SKILLS`, `PROJECTS`,
  `EXPERIENCE`, `ACHIEVEMENTS`. Non-standard names ("What I've Built") break
  section classifiers.
- Embeddable Type 1 / OpenType font — Latin Modern or Charter. Never a font that
  rasterises.
- Dates right-aligned via `\hfill`, not tabs or tables.
- Bullets via `itemize`, one line each, no nested lists.
- Hyperlinks: `\href{url}{visible text}` where **visible text is the URL itself**
  — some parsers read only the visible text.
- Escape LaTeX specials in all interpolated fields: `& % $ # _ { } ~ ^ \`
- Target exactly one page. If overflow, drop in this order:
  coursework → achievements beyond 2 → third bullet of project 3.

Output: `data/output/{date}/{company}__{title_slug}.pdf` plus a sibling
`.json` with the generation metadata (selected projects, scores, prompt hashes).

---

### 6.9 `validate/` — the "ATS score" module

There is no external score to query. This module **is** the score.

**Check 1 — parse-back fidelity (weight: pass/fail, blocking):**

Extract text from the generated PDF with `pymupdf`. Assert:

- Name, email, phone, college, CGPA, grad year all present and exact.
- Every generated bullet is recoverable as contiguous text.
- Section headings appear in the intended reading order.
- No ligature corruption (`ﬁ`, `ﬂ` must normalise back to `fi`, `fl`).
- Page count == 1.
- No text is inside an image XObject.

Any failure is **blocking**. Log the diff and fail loudly — this is the real
reason resumes silently disappear into ATS databases.

**Check 2 — keyword coverage (weight: the 0–100 number):**

```
1. Extract hard requirements from the JD: match against a curated gazetteer
   (data/gazetteer/skills.yaml — languages, frameworks, tools, cloud, concepts).
   Deterministic, no LLM.
2. Weight: terms in a "Requirements"/"Must have" block = 2.0; elsewhere = 1.0.
3. coverage = Σ(weight of matched terms) / Σ(weight of all terms) × 100
4. Count a term as matched only if it appears in recovered PDF text, and only
   if it is grounded (i.e. genuinely in the user's corpus).
```

**Check 3 — format hygiene (advisory, feeds the report):**
word count 400–650; no first-person pronouns; every bullet starts with a verb;
no passive voice beyond 1 bullet; consistent tense.

**Retry loop:**
`coverage < 90` and `attempts < 3` → re-run §6.7 with the missing grounded terms
supplied as `emphasise_if_grounded`. Never inject ungrounded terms to raise the
score — that defeats the purpose and creates an interview liability.

Persist `parse_ok`, `coverage_score`, `attempts`, `missing_terms` to `matches`.

---

### 6.10 `deliver/` — Telegram notifications

Daily digest at 09:00 IST via Telegram Bot:

```
🎯 7 new matches today (fit ≥ 55)

1. Razorpay — SDE Intern, Payments        fit 84  coverage 93
   Projects: paytm-clone, rate-limiter, k8s-deploy
   Missing: Kafka, gRPC
   ✅ Auto-applied                         PDF attached

...
3 jobs skipped (fit < 55). 1 resume flagged for manual review.
⚠️ 2 applications failed auto-submit (manual apply links below).
Reminder: check Internshala manually (no API).
```

Send PDFs as Telegram documents (cap 10/digest). Include inline buttons:
`[View Job]` `[View Resume]` `[Mark Applied]` `[Skip]`.

Real-time notifications: send a Telegram message **immediately** after each
successful auto-apply (see §6.11), don't wait for the daily digest.

---

### 6.11 `apply/` — automated application submission

**This module automates job applications where technically feasible.**

After a resume passes validation (§6.9), the system attempts to auto-apply:

**Tier 1 — API-based submission (highest reliability):**

Some ATS platforms support application submission via API:

| Provider | Method |
|---|---|
| Greenhouse | `POST /v1/boards/{slug}/jobs/{id}/application` (multipart form) |
| Lever | `POST /v0/postings/{slug}/{id}/apply` (multipart form) |
| Workable | `POST /api/v1/accounts/{slug}/jobs/{shortcode}/candidates` |

These accept: `name, email, phone, resume (PDF upload), linkedin_url,
github_url, cover_letter (optional)`.

**Tier 2 — Browser automation (best effort):**

For ATS platforms without public apply APIs, use `playwright` (headless
Chromium) to fill and submit application forms:

1. Navigate to `apply_url`.
2. Detect form fields via label text / `name` / `aria-label` matching.
3. Fill: name, email, phone, LinkedIn, GitHub, portfolio from `profile`.
4. Upload the generated PDF to the resume file input.
5. Handle dropdowns (e.g., "How did you hear about us?" → "Company website").
6. Submit the form.
7. Screenshot the confirmation page as proof.

**Safety guardrails — non-negotiable:**

- **Never create accounts** on behalf of the user. If login is required, skip
  and mark `auto_apply_status = 'needs_login'`.
- **Never solve CAPTCHAs.** If one appears, skip and mark
  `auto_apply_status = 'captcha_blocked'`.
- **Max 10 auto-applies per day.** Circuit breaker to avoid pattern flagging.
- **Cooldown:** minimum 3 minutes between submissions to the same domain.
- **Dry-run mode:** `--dry-run` fills forms but does NOT click submit.
  Screenshot the filled form for user review.
- **Human-in-the-loop fallback:** If confidence in form detection is < 80%
  (too many unrecognized fields), skip and send the apply link to Telegram
  for manual submission.

**Post-apply actions:**

1. Update `applications.status` → `'applied'`, set `applied_at`.
2. Save confirmation screenshot to `data/output/{date}/confirmations/`.
3. Send Telegram notification:
   ```
   ✅ Applied: Razorpay — SDE Intern, Payments
   Fit: 84 | Coverage: 93
   Projects used: paytm-clone, rate-limiter, k8s-deploy
   📎 Resume attached
   📸 Confirmation screenshot attached
   ```
4. If submission fails, send:
   ```
   ❌ Auto-apply failed: Razorpay — SDE Intern
   Reason: CAPTCHA detected
   🔗 Apply manually: https://...
   📎 Resume attached
   ```

**Database additions:**

```sql
ALTER TABLE applications ADD COLUMN auto_apply_status TEXT
    DEFAULT 'pending';  -- pending|submitted|needs_login|captcha_blocked|form_error|skipped
ALTER TABLE applications ADD COLUMN confirmation_screenshot TEXT;
ALTER TABLE applications ADD COLUMN submit_attempted_at TIMESTAMP;
```

**Tech additions:**

| Layer | Choice | Why |
|---|---|---|
| Browser automation | `playwright` (async) | Reliable, headless Chromium, good form interaction |
| Screenshot | `playwright` built-in | Confirmation proof |

---

## 7. Database schema

```sql
-- migrations/001_init.sql

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
    embedding BLOB, embedding_source_hash TEXT,
    created_at TIMESTAMP, pushed_at TIMESTAMP, synced_at TIMESTAMP
);

CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL, domain TEXT UNIQUE NOT NULL,
    tier INTEGER DEFAULT 2,
    ats_provider TEXT, ats_slug TEXT,
    detection_status TEXT,        -- resolved | unknown | manual | dead
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
CREATE INDEX idx_jobs_hash ON jobs(content_hash);
CREATE INDEX idx_jobs_seen ON jobs(first_seen_at);

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
    status TEXT DEFAULT 'generated',   -- generated|sent|applied|rejected|interview|offer
    applied_at TIMESTAMP, notes TEXT
);

CREATE TABLE run_log (
    id INTEGER PRIMARY KEY, run_type TEXT, started_at TIMESTAMP,
    finished_at TIMESTAMP, status TEXT, stats_json TEXT, error TEXT
);
```

---

## 8. Repository layout

```
resume-agent/
├── pyproject.toml
├── .env.example
├── README.md
├── docs/decisions.md
├── migrations/001_init.sql
├── data/
│   ├── config/companies.yaml
│   ├── config/projects_override.yaml
│   ├── gazetteer/skills.yaml
│   ├── input/old_resume.pdf
│   ├── output/{YYYY-MM-DD}/
│   └── agent.db
├── templates/resume.tex.j2
├── reports/
└── src/resume_agent/
    ├── cli.py                # typer entrypoint
    ├── config.py  db.py  models.py  logging.py
    ├── profile/parser.py
    ├── github/client.py  scorer.py
    ├── jobs/
    │   ├── discovery/detector.py
    │   ├── sources/{base,greenhouse,lever,ashby,workable,recruitee,
    │   │            smartrecruiters,adzuna,arbeitnow,llm_fallback}.py
    │   └── pipeline/{normalize,dedupe,filter}.py
    ├── matcher/{embed,retrieve,select}.py
    ├── writer/{prompts,generate,verify}.py
    ├── render/{latex,escape}.py
    ├── validate/{parseback,keywords,hygiene}.py
    ├── deliver/{email,telegram}.py
    └── orchestrate/daily.py
```

**CLI surface:**

```bash
resume-agent init                       # migrations + dirs
resume-agent profile parse [--force]
resume-agent github sync
resume-agent companies detect [--refresh] [--tier 1]
resume-agent jobs fetch [--source greenhouse] [--dry-run]
resume-agent match --job-id 123
resume-agent generate --job-id 123 [--no-validate]
resume-agent run daily                  # full pipeline
resume-agent report weekly
```

---

## 9. Configuration

`.env.example`:

```
ANTHROPIC_API_KEY=
GITHUB_TOKEN=
GITHUB_USERNAME=
ADZUNA_APP_ID=
ADZUNA_APP_KEY=
DATABASE_PATH=data/agent.db
LLM_MODEL=claude-sonnet-4-6
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
MIN_FIT_SCORE=55
MIN_COVERAGE_SCORE=90
MAX_RETRIES=3
MAX_DAILY_RESUMES=15
NOTIFY_CHANNEL=email
SMTP_HOST=
SMTP_USER=
SMTP_PASSWORD=
NOTIFY_TO=
LOG_LEVEL=INFO
DRY_RUN=false
```

`MAX_DAILY_RESUMES` is a cost circuit-breaker. Exceeding it halts generation and
alerts rather than silently burning API credit.

---

## 10. Testing

| Layer | Requirement |
|---|---|
| Adapters | `respx`-mocked fixtures of real payloads, one per provider, committed under `tests/fixtures/`. Schema drift must fail loudly. |
| Detector | Fixture HTML for each ATS embed pattern + 3 known-negative pages |
| Dedupe | Same job from Greenhouse and Adzuna → 1 row, direct source retained |
| Filter | Table-driven: 40 real titles, expected include/exclude |
| Grounding verifier | Golden set of 15 bullets with known hallucinations → 100% detection. **This test may never be skipped.** |
| Renderer | Snapshot the generated `.tex`; assert zero unescaped LaTeX specials |
| Parse-back | Round-trip 10 generated PDFs; assert field-level equality |
| Coverage scorer | 10 (JD, resume) pairs with hand-computed expected scores, ±3 tolerance |
| End-to-end | One `--dry-run` pass with fixtures, no network, no LLM (stub) |

Minimum coverage on `writer/` and `validate/`: 90%. Elsewhere: 70%.

---

## 11. Cost & performance

| Item | Estimate |
|---|---|
| Job ingestion | ₹0 (free public endpoints) |
| Embeddings | ₹0 (local CPU) |
| LLM: selection | ~6k in / 0.6k out per job |
| LLM: bullets | ~4k in / 0.4k out × 3 projects |
| LLM: retries | ~30% of jobs need 1 retry |
| **Per resume** | **≈ ₹4–7** |
| **Monthly (15/day)** | **≈ ₹1,800–3,000** → tune `MIN_FIT_SCORE` upward or `MAX_DAILY_RESUMES` down to hit the ₹600 target; 4–5 high-quality resumes/day is the realistic setting |
| Tier-3 LLM extraction | ~₹80/week |
| Hosting | ₹0 (GitHub Actions free tier) |

Prompt-cache the profile and project corpus across calls within a run.

**Note:** the ₹600 target in §2 implies ~4 resumes/day. Targeted applications
outperform volume anyway. Set `MIN_FIT_SCORE=70` in production.

---

## 12. Build phases

Each phase ships working, tested code. Do not start a phase before the previous
one passes its acceptance test.

**Phase 1 — Foundation**
Repo, `pyproject.toml`, config, DB + migrations, logging, CLI skeleton.
*Accept:* `resume-agent init` creates the DB; all tables exist.

**Phase 2 — Identity**
Resume parser, GitHub sync, quality scorer, override file.
*Accept:* `profile` populated and human-confirmed; ≥ 30 projects synced with scores.

**Phase 3 — Job ingestion**
Detector + Greenhouse, Lever, Ashby adapters + normalize/dedupe/filter.
*Accept:* ≥ 200 companies resolved; a daily run yields ≥ 20 filtered internships;
re-running produces 0 duplicates.

**Phase 4 — Matching**
Embeddings, retrieval, LLM selection.
*Accept:* on 10 hand-labelled JDs, top-3 selection agrees with the user's own
choice on ≥ 7.

**Phase 5 — Generation**
LaTeX template, bullet writer, grounding verifier.
*Accept:* golden-set hallucination test passes 15/15; PDF compiles; 1 page.

**Phase 6 — Validation**
Parse-back, keyword coverage, retry loop.
*Accept:* 10/10 PDFs parse-back clean; ≥ 8/10 reach coverage ≥ 90.

**Phase 7 — Automation**
Scheduler, delivery, run log, circuit breakers, weekly report.
*Accept:* 7 consecutive unattended daily runs with no manual intervention.

**Phase 8 — Remaining adapters + tier-3 fallback**
Workable, Recruitee, SmartRecruiters, Adzuna, Arbeitnow, LLM extraction.

---

## 13. Risk register

| Risk | Mitigation |
|---|---|
| LLM fabricates a technology | Code verifier in §6.7; blocking; golden test |
| ATS changes response schema | Pydantic parse fails loudly; per-adapter fixtures; alert on `consecutive_failures ≥ 3` |
| Slug goes stale / company switches ATS | Monthly `--refresh`; mark `dead` after 5 failures |
| Cost runaway | `MAX_DAILY_RESUMES` circuit breaker; per-run cost logged to `run_log` |
| Wrong CGPA/college propagates everywhere | Human confirmation gate in §6.1; `profile.confirmed_at` must be non-null before generation |
| Resume silently unparseable by ATS | Parse-back check is blocking, not advisory |
| Being blocked by a source | Per-host concurrency 1, honest UA, ETag caching, backoff |
| Over-applying damages reputation | No auto-submit; raise `MIN_FIT_SCORE` rather than volume |

---

## 14. Resolved decisions

| Decision | Choice | Rationale |
|---|---|---|
| Scheduler | **GitHub Actions cron** | Free tier, no infra to maintain, built-in secrets management, reliable. |
| Delivery | **Telegram Bot API** | Instant push notifications, inline buttons, PDF/screenshot sharing. |
| Resume format | **LaTeX → PDF** | Superior typography, ATS-safe output via `tectonic`. DOCX export deferred to a later phase. |
| Auto-apply | **Enabled** | API-based (Greenhouse/Lever/Workable) + Playwright browser automation with safety guardrails. Telegram notification after each apply. |

## 15. Remaining user inputs needed

1. **Seed company list** — the user must supply or approve the initial 300–600
   companies. System will auto-discover via YC directory, Wellfound, and Indian
   unicorn lists.
2. **`manual_notes` for top 7 projects** — the single highest-leverage input to
   output quality. Real metrics here (users served, latency, dataset size) are
   what make bullets strong, and they cannot be invented by the model.
3. **Telegram Bot token** — create via @BotFather, add to `.env`.
4. **GitHub PAT** — fine-grained, `public_repo` read-only scope.
