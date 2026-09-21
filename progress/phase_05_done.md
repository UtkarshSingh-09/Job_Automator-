# ✅ Phase 5 Complete: Job Ingestion & Filtering Pipeline

> **Date Completed:** 2026-09-22  
> **Status:** PASSED  
> **Commit Tag:** `phase-5-ingestion`

---

## 📦 What Was Built

| Component | File | Purpose |
|---|---|---|
| ATS Adapters | [`src/resume_agent/jobs/sources/`](file:///Users/utkarshsingh/Desktop/Job_finder/src/resume_agent/jobs/sources/) | Concrete adapters for Greenhouse (`greenhouse.py`), Lever (`lever.py`), Ashby (`ashby.py`), and Workable (`workable.py`) inheriting from [`JobSourceAdapter`](file:///Users/utkarshsingh/Desktop/Job_finder/src/resume_agent/jobs/sources/base.py) |
| HTML Normalizer | [`src/resume_agent/jobs/pipeline/normalize.py`](file:///Users/utkarshsingh/Desktop/Job_finder/src/resume_agent/jobs/pipeline/normalize.py) | Unescapes HTML entities, strips `<script>`/`<style>`, converts headings/lists/paragraphs to clean Markdown, and classifies remote status (`remote`, `hybrid`, `onsite`) |
| Content Deduplication | [`src/resume_agent/jobs/pipeline/dedupe.py`](file:///Users/utkarshsingh/Desktop/Job_finder/src/resume_agent/jobs/pipeline/dedupe.py) | Generates deterministic SHA-256 content hashes from normalized `(company_name, title, location)` tuples for idempotent upserts |
| Internship Filter | [`src/resume_agent/jobs/pipeline/filter.py`](file:///Users/utkarshsingh/Desktop/Job_finder/src/resume_agent/jobs/pipeline/filter.py) | Evaluates title against internship/new grad inclusions vs senior exclusions (`staff`, `lead`, `vp`, `sr.`, etc.), with India/Remote location checks |
| Job Ingestion Service | [`src/resume_agent/jobs/service.py`](file:///Users/utkarshsingh/Desktop/Job_finder/src/resume_agent/jobs/service.py) | Coordinates multi-source fetching, normalization, SQLite upserts (`ON CONFLICT DO UPDATE`), and listing queries |
| CLI Commands | [`src/resume_agent/cli.py`](file:///Users/utkarshsingh/Desktop/Job_finder/src/resume_agent/cli.py) | `resume-agent jobs fetch`, `resume-agent jobs list`, and `resume-agent jobs show <job_id>` |

---

## 🧪 Verification & Acceptance Tests

1. **`resume-agent jobs fetch` (Live Multi-ATS Ingestion)**:
   - Polled **41 resolved company endpoints** across Greenhouse, Lever, Ashby, and Workable.
   - Fetched **1,608 live job postings**.
   - Successfully inserted listings into SQLite `jobs` table with clean Markdown descriptions.
2. **Internship & Location Filter (`passed_filter = 1`)**:
   - Filtered out experienced roles (Staff, Principal, Director, Senior).
   - Identified **62 high-relevance internship / new grad opportunities**, including:
     - **Stripe:** *Software Engineer, Intern* (Bengaluru, India)
     - **Figma:** *Software Engineer Intern (Summer 2027)* (Remote / US)
     - **Coinbase:** *Software Engineer Intern* (Hybrid)
     - **Scale AI:** *SWE Fellow* (Remote)
3. **Deduplication Idempotency**:
   - Re-running `resume-agent jobs fetch --limit-companies 10` on existing postings resulted in **0 new insertions** (`new_inserted: 0`), proving `content_hash` deduplication is 100% idempotent.
4. **Markdown Rendering & Preview (`resume-agent jobs show 2648`)**:
   - Verified that job postings preview clean Markdown with parsed bullet points, headers, and apply URLs.
5. **Database Row Counts**:
   - `jobs` table contains **1,598 stored listings** (62 passing candidate filter).

---

## 🔧 Action Items for User

1. Inspect passed internship listings:
   ```bash
   uv run resume-agent jobs list --limit 20
   ```
2. View detailed job requirements for the Stripe Bengaluru SWE Intern posting:
   ```bash
   uv run resume-agent jobs show 2648
   ```
3. Phase 5 is fully complete and verified. Ready to proceed to **Phase 6: Semantic Matching Engine**!
