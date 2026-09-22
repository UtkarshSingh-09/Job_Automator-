# ✅ Phase 10 Complete: Auto-Apply Engine

> **Date Completed:** 2026-09-22  
> **Status:** PASSED  
> **Commit Tag:** `phase-10-auto-apply`

---

## 📦 What Was Built

| Component | File | Purpose |
|---|---|---|
| Database Migration | [`migrations/002_auto_apply.sql`](file:///Users/utkarshsingh/Desktop/Job_finder/migrations/002_auto_apply.sql) | Enhanced `applications` table with `apply_method`, `response_payload`, and indices on `applied_at`, `status`, and `auto_apply_status`. |
| Apply Models | [`src/resume_agent/apply/models.py`](file:///Users/utkarshsingh/Desktop/Job_finder/src/resume_agent/apply/models.py) | Normalized `CandidateSubmissionPayload` and `ApplyResult` structures. |
| Tier 1: Direct ATS API Submitter | [`src/resume_agent/apply/api_submit.py`](file:///Users/utkarshsingh/Desktop/Job_finder/src/resume_agent/apply/api_submit.py) | High-reliability multipart form submission for Greenhouse (`POST /v1/boards/{slug}/jobs/{id}`) and Lever (`POST /v0/postings/{slug}/{id}/apply`) with dry-run support. |
| Tier 2: Playwright Browser Submitter | [`src/resume_agent/apply/browser_submit.py`](file:///Users/utkarshsingh/Desktop/Job_finder/src/resume_agent/apply/browser_submit.py) | Headless Chromium automation engine with smart fuzzy field matching (Name, Email, Phone, URLs, Resume upload), CAPTCHA detection, login wall detection, confidence scoring (<80% fallback), and screenshot capture. |
| Apply Orchestrator & Safety Controller | [`src/resume_agent/apply/manager.py`](file:///Users/utkarshsingh/Desktop/Job_finder/src/resume_agent/apply/manager.py) | Enforces daily limit circuit breakers (max 10/day), domain cooldowns (3-min delay), candidate profile loading, ATS router, SQLite logging, and Telegram proof dispatch. |
| Package Surface | [`src/resume_agent/apply/__init__.py`](file:///Users/utkarshsingh/Desktop/Job_finder/src/resume_agent/apply/__init__.py) | Clean module exports (`ApplyManager`, `submit_via_api`, `submit_via_browser`, `ApplyResult`). |
| Telegram Confirmation Updates | [`src/resume_agent/deliver/telegram.py`](file:///Users/utkarshsingh/Desktop/Job_finder/src/resume_agent/deliver/telegram.py) | Added `send_photo()` and `send_apply_confirmation()` with attached confirmation screenshot and PDF. |
| Daily Pipeline Integration | [`src/resume_agent/orchestrate/daily.py`](file:///Users/utkarshsingh/Desktop/Job_finder/src/resume_agent/orchestrate/daily.py) | Added Stage 4.5 (`--auto-apply`) connecting ATS validation directly to automated submission. |
| CLI Commands | [`src/resume_agent/cli.py`](file:///Users/utkarshsingh/Desktop/Job_finder/src/resume_agent/cli.py) | Added `resume-agent apply --job-id <id> [--dry-run] [--force]`, `resume-agent apply-batch`, `resume-agent applications`, and updated `daily --auto-apply`. |
| Automated Test Suite | [`tests/test_apply.py`](file:///Users/utkarshsingh/Desktop/Job_finder/tests/test_apply.py) | 10 dedicated tests covering payload normalization, API provider detection, dry-run multipart payloads, daily limits, cooldowns, CAPTCHA detection, and login wall detection. |

---

## 🛡️ Non-Negotiable Safety Guardrails Enforced

1. **Daily Circuit Breaker (`MAX_DAILY_APPLIES`)**: Hard limit of **10 applications per calendar day**.
2. **Domain Cooldown (`MIN_COOLDOWN_SECONDS`)**: Minimum **180 seconds (3 minutes)** cooldown between submissions to the same company.
3. **Zero CAPTCHA Solving**: If a CAPTCHA (Cloudflare Turnstile, reCAPTCHA, hCaptcha, Arkose Labs) is detected, **never attempt to bypass or solve it**. Immediately mark status as `captcha_blocked`, take a screenshot, and notify Telegram with a direct manual apply link.
4. **Zero Account Creation**: Never attempt automated account creation. If an ATS requires a login wall (e.g., Workday, Oracle Taleo, iCIMS), immediately mark status as `needs_login` and provide a manual apply link.
5. **Confidence Gate (< 80% fallback)**: If form field detection confidence is below 80% (ambiguous custom questions), abort automated submit, mark as `form_error`, and send the application link to Telegram for manual submission.
6. **Dry-Run Mode (`--dry-run`)**: Completely fills the form, attaches the generated PDF resume, captures a full-page verification screenshot in `data/output/screenshots/`, records the simulated transaction, and **never clicks the final Submit button**.

---

## 🧪 Verification & Acceptance Tests

1. **Unit Test Suite (`pytest tests/test_apply.py`)**:
   - `test_candidate_payload_normalization`: PASSED
   - `test_detect_api_provider_greenhouse`: PASSED
   - `test_detect_api_provider_lever`: PASSED
   - `test_greenhouse_api_dry_run`: PASSED
   - `test_lever_api_dry_run`: PASSED
   - `test_clean_slug_sanitization`: PASSED
   - `test_daily_limit_circuit_breaker`: PASSED
   - `test_domain_cooldown`: PASSED
   - `test_captcha_detection_logic`: PASSED
   - `test_login_wall_detection_logic`: PASSED
   - **Result:** **10/10 tests PASSED in 0.72s**.

2. **Total Project Test Suite (`pytest tests/`)**:
   - **38/38 tests PASSED across all suites (100% pass rate)**.
     - `test_grounding.py`: 10/10 passed
     - `test_validation.py`: 11/11 passed
     - `test_delivery.py`: 7/7 passed
     - `test_apply.py`: 10/10 passed

3. **Live Single Application Simulation (`resume-agent apply --job-id 2648 --dry-run`)**:
   - Successfully routed Stripe SWE Intern to Greenhouse Board API simulation.
   - Recorded transaction to SQLite `applications` table.
   - Dispatched simulated Telegram notification card.

4. **Live Batch Application Simulation (`resume-agent apply-batch --limit 3 --min-score 70 --dry-run`)**:
   - Evaluated candidate match rankings and submitted 3 simulated applications.
   - 3/3 succeeded with audit records persisted in database.

5. **Audit Trail Verification (`resume-agent applications`)**:
   - Rendered interactive Rich table displaying App ID, Company, Role, Status, Method, and Timestamp.
