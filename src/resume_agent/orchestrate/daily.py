import json
import time
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional

from resume_agent.db import get_db
from resume_agent.models import JobModel, MatchModel
from resume_agent.jobs.service import get_job_by_id, ingest_jobs
from resume_agent.matcher.service import match_job
from resume_agent.writer.service import generate_tailored_resume
from resume_agent.validate.runner import validate_resume_pdf
from resume_agent.deliver.telegram import TelegramClient
from resume_agent.logging import logger, console, print_success, print_error, print_info, print_warning


def run_daily_pipeline(
    dry_run: bool = False,
    skip_fetch: bool = False,
    limit: int = 5,
    send_telegram: bool = True,
    send_digest: bool = True,
    auto_apply: bool = False,
    min_fit_threshold: float = 65.0,
    date_str: Optional[str] = None,
    slot_label: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Master Daily Pipeline Orchestrator (09:00 IST Visual Loop).
    Executes:
    1. Ingestion: Polls active ATS company boards for new job postings.
    2. Matching: Semantic embedding retrieval + LLM fit scoring.
    3. Generation: Tailored Google X-Y-Z bullets + LaTeX compilation to 1-page PDF.
    4. Validation: 7-Gate Mechanical ATS Verification Suite.
    5. Delivery: Real-time match cards + attached PDFs + morning executive digest to Telegram.
    
    Returns structured stats dictionary suitable for n8n JSON output.
    """
    today = date_str or time.strftime("%Y-%m-%d")
    logger.info(f"Starting Resume Agent Daily Pipeline for {today} (Dry Run: {dry_run})")

    telegram = TelegramClient(dry_run=dry_run)

    stats: Dict[str, Any] = {
        "date": today,
        "dry_run": dry_run,
        "boards_monitored": 41,
        "jobs_ingested": 0,
        "matches_found": 0,
        "resumes_generated": 0,
        "resumes_validated": 0,
        "applied_count": 0,
        "matches": [],
        "success": True,
        "errors": [],
    }

    current_stage = "Initialization"

    try:
        # Count monitored companies
        with get_db() as conn:
            c_row = conn.execute("SELECT COUNT(*) as cnt FROM companies WHERE ats_slug IS NOT NULL AND ats_slug != '';").fetchone()
            if c_row:
                stats["boards_monitored"] = c_row["cnt"]

        # ----------------------------------------------------------------------
        # Stage 1: Ingestion
        # ----------------------------------------------------------------------
        current_stage = "Job Ingestion"
        if not skip_fetch and not dry_run:
            logger.info("Executing job ingestion across verified company boards...")
            try:
                ingest_res = ingest_jobs(dry_run=dry_run)
                stats["jobs_ingested"] = ingest_res.get("new_inserted", 0)
            except Exception as e:
                logger.warning(f"Live job ingestion encountered non-fatal issues: {e}")
        else:
            logger.info("Skipping live fetch (skip_fetch=True or dry_run=True).")

        # ----------------------------------------------------------------------
        # Stage 2: Semantic Matching
        # ----------------------------------------------------------------------
        current_stage = "Semantic Matching"
        logger.info("Searching for qualifying internship postings...")

        # Find eligible jobs: passed_filter = 1
        with get_db() as conn:
            # First find existing high-fit matches not yet applied to
            matched_rows = conn.execute(
                """
                SELECT m.*, j.title, j.company_name, j.apply_url, j.location, j.remote_type
                FROM matches m
                JOIN jobs j ON m.job_id = j.id
                WHERE m.overall_fit >= ?
                  AND m.id NOT IN (
                      SELECT DISTINCT match_id FROM applications 
                      WHERE status IN ('applied', 'manual_required')
                         OR auto_apply_status IN ('applied', 'manual_required')
                  )
                ORDER BY m.overall_fit DESC
                LIMIT ?;
                """,
                (min_fit_threshold, limit),
            ).fetchall()

            # Query fresh unmatched jobs (id DESC gives newest ingested postings first)
            # Fetch a candidate pool of up to 50 to ensure finding top matches
            unmatched_jobs = conn.execute(
                """
                SELECT * FROM jobs
                WHERE passed_filter = 1
                  AND id NOT IN (SELECT job_id FROM matches)
                ORDER BY id DESC
                LIMIT 50;
                """,
            ).fetchall()

        eligible_matches: List[Dict[str, Any]] = []

        # Run matcher on unmatched jobs until limit is satisfied
        for u_row in unmatched_jobs:
            if len(eligible_matches) >= limit:
                break
            j_id = u_row["id"]
            logger.info(f"Running semantic matching for Job #{j_id} ({u_row['company_name']} - {u_row['title']})...")
            try:
                m_obj = match_job(j_id)
                if m_obj and m_obj.overall_fit >= min_fit_threshold:
                    eligible_matches.append({
                        "job_id": j_id,
                        "match": m_obj,
                        "job": get_job_by_id(j_id),
                    })
            except Exception as e:
                logger.warning(f"Failed to match Job #{j_id}: {e}")

        # Add existing high-fit matches if needed to reach quota
        for m_row in matched_rows:
            if len(eligible_matches) >= limit:
                break
            j_id = m_row["job_id"]
            if not any(item["job_id"] == j_id for item in eligible_matches):
                m_obj = MatchModel(
                    id=m_row["id"],
                    job_id=m_row["job_id"],
                    overall_fit=m_row["overall_fit"],
                    selected_projects=json.loads(m_row["selected_projects_json"] or "[]"),
                    selection_reasoning=m_row["selection_reasoning"],
                    uncovered_requirements=json.loads(m_row["uncovered_requirements_json"] or "[]"),
                    pdf_path=m_row["pdf_path"],
                    created_at=m_row["created_at"],
                )
                eligible_matches.append({
                    "job_id": j_id,
                    "match": m_obj,
                    "job": get_job_by_id(j_id),
                })

        stats["matches_found"] = len(eligible_matches)
        logger.info(f"Identified {len(eligible_matches)} high-fit match(es) for processing.")

        # ----------------------------------------------------------------------
        # Stage 3: Generation & ATS Validation
        # ----------------------------------------------------------------------
        current_stage = "Resume Generation & ATS Validation"

        for item in eligible_matches:
            job_obj: JobModel = item["job"]
            match_obj: MatchModel = item["match"]
            j_id = item["job_id"]

            pdf_path = Path(match_obj.pdf_path) if match_obj.pdf_path else None
            needs_gen = not pdf_path or not pdf_path.exists()

            if needs_gen:
                logger.info(f"Generating tailored resume for Job #{j_id} ({job_obj.company_name})...")
                try:
                    pdf_path = generate_tailored_resume(j_id)
                    stats["resumes_generated"] += 1
                except Exception as e:
                    err_msg = f"Resume generation failed for Job #{j_id}: {e}"
                    logger.error(err_msg)
                    stats["errors"].append(err_msg)
                    continue
            else:
                stats["resumes_generated"] += 1

            # Execute 7-Gate ATS Mechanical Verification
            logger.info(f"Executing 7-Gate ATS verification on {pdf_path.name}...")
            val_report = validate_resume_pdf(pdf_path, job_id=j_id)

            if val_report.is_valid:
                stats["resumes_validated"] += 1
                logger.info(f"Artifact {pdf_path.name} PASSED all 7 gates (Score: {val_report.ats_score}/100)")
            else:
                logger.warning(f"Artifact {pdf_path.name} failed gates: {val_report.all_violations}")

            # ------------------------------------------------------------------
            # Stage 4: Automated Application Submission or Match Delivery
            # ------------------------------------------------------------------
            if val_report.is_valid:
                if auto_apply:
                    logger.info(f"Executing automated application for {job_obj.company_name} (Job #{j_id})...")
                    try:
                        from resume_agent.apply.manager import ApplyManager
                        app_mgr = ApplyManager(dry_run=dry_run)
                        apply_res = app_mgr.apply_for_job(j_id, dry_run=dry_run)
                        if apply_res.success:
                            stats["applied_count"] += 1
                    except Exception as e:
                        logger.error(f"Auto-apply attempt failed for Job #{j_id}: {e}")
                        if send_telegram:
                            telegram.send_match_alert(job_obj, match_obj, pdf_path)
                elif send_telegram:
                    logger.info(f"Dispatching Telegram match card for {job_obj.company_name}...")
                    telegram.send_match_alert(job_obj, match_obj, pdf_path)

            stats["matches"].append({
                "job_id": j_id,
                "company": job_obj.company_name,
                "title": job_obj.title,
                "score": match_obj.overall_fit,
                "ats_score": val_report.ats_score,
                "pdf_path": str(pdf_path),
                "apply_url": job_obj.apply_url,
                "is_valid": val_report.is_valid,
            })

        # ----------------------------------------------------------------------
        # Stage 5: Telegram Reporting (Evening Digest or Slot Status Pulse)
        # ----------------------------------------------------------------------
        current_stage = "Telegram Reporting"
        if send_telegram and send_digest:
            logger.info("Dispatching daily evening executive briefing to Telegram...")
            telegram.send_daily_digest(stats)
        elif send_telegram and not send_digest:
            slot_name = slot_label or "Scheduled Scan"
            valid_cnt = len([m for m in stats.get("matches", []) if m.get("is_valid")])
            if valid_cnt == 0:
                logger.info(f"Dispatching slot heartbeat to Telegram ({slot_name})...")
                telegram.send_message(
                    f"📡 <b>{slot_name} Complete</b>\n\n"
                    f"• ATS Boards Monitored: <b>{stats['boards_monitored']}</b>\n"
                    f"• Postings Scanned & Analyzed: <b>{stats['jobs_ingested']}</b>\n"
                    f"• Qualifying Internships: <i>0 new validated high-fit roles detected in this slot window.</i>\n\n"
                    f"💤 <i>Engine sleeping until next scheduled IST slot.</i>"
                )

    except Exception as e:
        err_str = f"Pipeline failure in stage '{current_stage}': {e}"
        logger.error(f"{err_str}\n{traceback.format_exc()}")
        stats["success"] = False
        stats["errors"].append(err_str)
        if send_telegram:
            telegram.send_error_alert(str(e), stage=current_stage)

    return stats
