import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from resume_agent.config import get_settings
from resume_agent.db import get_db
from resume_agent.models import JobModel, CompanyModel, MatchModel, ProfileModel
from resume_agent.profile.service import get_profile
from resume_agent.jobs.service import get_job_by_id
from resume_agent.apply.models import ApplyResult, CandidateSubmissionPayload
from resume_agent.apply.api_submit import detect_api_provider, submit_via_api
from resume_agent.apply.browser_submit import submit_via_browser
from resume_agent.deliver.telegram import TelegramClient
from resume_agent.logging import logger, console, print_success, print_error, print_warning, print_info


class ApplyManager:
    """
    Master Application Controller.
    Enforces daily quota circuit breakers, domain cooldowns, routing between
    Direct ATS APIs and Headless Browser Automation, SQLite auditing, and Telegram delivery.
    """

    def __init__(self, dry_run: bool = False):
        self.settings = get_settings()
        self.dry_run = dry_run
        self.telegram = TelegramClient(dry_run=dry_run)

    def get_daily_applied_count(self) -> int:
        """Calculate number of applications submitted today."""
        with get_db() as conn:
            row = conn.execute(
                "SELECT COUNT(*) as cnt FROM applications WHERE status = 'applied' AND date(applied_at) = date('now');"
            ).fetchone()
            return row["cnt"] if row else 0

    def check_domain_cooldown(self, company_name: str) -> Optional[int]:
        """
        Check if an application was recently attempted for the same company.
        Returns remaining cooldown seconds if active, or None if clear.
        """
        with get_db() as conn:
            row = conn.execute(
                """
                SELECT a.submit_attempted_at
                FROM applications a
                JOIN matches m ON a.match_id = m.id
                JOIN jobs j ON m.job_id = j.id
                WHERE j.company_name = ?
                  AND a.submit_attempted_at IS NOT NULL
                ORDER BY a.submit_attempted_at DESC
                LIMIT 1;
                """,
                (company_name,)
            ).fetchone()

            if not row or not row["submit_attempted_at"]:
                return None

            try:
                # Parse timestamp
                ts_str = row["submit_attempted_at"]
                last_time = datetime.fromisoformat(ts_str)
                elapsed = (datetime.now() - last_time).total_seconds()
                min_cd = self.settings.min_cooldown_seconds
                if elapsed < min_cd:
                    return int(min_cd - elapsed)
            except Exception:
                pass

        return None

    def apply_for_job(
        self,
        job_id: int,
        dry_run: Optional[bool] = None,
        force: bool = False
    ) -> ApplyResult:
        """
        Execute automated or simulated application submission for a specific job ID.
        """
        is_dry_run = self.dry_run if dry_run is None else dry_run

        # 1. Load Job
        job = get_job_by_id(job_id)
        if not job:
            return ApplyResult(
                success=False,
                status="failed",
                method="guard",
                error=f"Job #{job_id} not found in database."
            )

        # 2. Load Match and Resume PDF
        with get_db() as conn:
            m_row = conn.execute("SELECT * FROM matches WHERE job_id = ?;", (job_id,)).fetchone()
            if not m_row:
                return ApplyResult(
                    success=False,
                    status="failed",
                    method="guard",
                    error=f"No match record exists for Job #{job_id}. Run 'resume-agent match' first."
                )
            match_id = m_row["id"]
            pdf_path_str = m_row["pdf_path"]

            # Load Company ATS metadata if present
            c_row = conn.execute("SELECT * FROM companies WHERE id = ?;", (job.company_id,)).fetchone() if job.company_id else None
            company = CompanyModel(
                id=c_row["id"],
                name=c_row["name"],
                domain=c_row["domain"],
                tier=c_row["tier"],
                ats_provider=c_row["ats_provider"],
                ats_slug=c_row["ats_slug"],
                detection_status=c_row["detection_status"],
            ) if c_row else None

        if not pdf_path_str or not Path(pdf_path_str).exists():
            return ApplyResult(
                success=False,
                status="failed",
                method="guard",
                error=f"Resume PDF not generated for Job #{job_id}. Run 'resume-agent generate' first."
            )

        resume_pdf_path = Path(pdf_path_str)

        # 3. Load Candidate Profile
        profile = get_profile()
        if not profile:
            return ApplyResult(
                success=False,
                status="failed",
                method="guard",
                error="Candidate profile not found. Run 'resume-agent init-profile' first."
            )

        candidate = CandidateSubmissionPayload.from_profile_model(profile)

        # 4. Safety Guard: Daily Circuit Breaker
        daily_count = self.get_daily_applied_count()
        if not is_dry_run and not force and daily_count >= self.settings.max_daily_applies:
            msg = f"Daily limit reached: {daily_count}/{self.settings.max_daily_applies} applications submitted today."
            logger.warning(msg)
            return ApplyResult(
                success=False,
                status="daily_limit_reached",
                method="guard",
                notes=msg
            )

        # 5. Safety Guard: Domain Cooldown
        cd_remaining = self.check_domain_cooldown(job.company_name)
        if not is_dry_run and not force and cd_remaining is not None:
            msg = f"Cooldown active: {cd_remaining}s remaining before next submission to {job.company_name}."
            logger.warning(msg)
            return ApplyResult(
                success=False,
                status="cooldown_active",
                method="guard",
                notes=msg
            )

        # 6. Route: Tier 1 Direct API vs Tier 2 Playwright Browser
        can_api, provider, slug, posting_id = detect_api_provider(job, company)

        if can_api:
            logger.info(f"Routing Job #{job_id} to Tier 1 Direct API ({provider})")
            result = submit_via_api(job, candidate, resume_pdf_path, company=company, dry_run=is_dry_run)
        else:
            logger.info(f"Routing Job #{job_id} to Tier 2 Headless Browser Automation (Playwright)")
            result = submit_via_browser(job, candidate, resume_pdf_path, company=company, dry_run=is_dry_run)

        # 7. Persist to SQLite Database
        app_status = "applied" if result.status == "submitted" else "generated"
        screenshot_str = str(result.screenshot_path) if result.screenshot_path else None
        response_str = json.dumps(result.response_data or {})

        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO applications (
                    match_id, status, auto_apply_status, apply_method,
                    confirmation_screenshot, response_payload,
                    submit_attempted_at, applied_at, notes
                ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status = excluded.status,
                    auto_apply_status = excluded.auto_apply_status,
                    apply_method = excluded.apply_method,
                    confirmation_screenshot = excluded.confirmation_screenshot,
                    response_payload = excluded.response_payload,
                    submit_attempted_at = CURRENT_TIMESTAMP,
                    applied_at = excluded.applied_at,
                    notes = excluded.notes;
                """,
                (
                    match_id,
                    app_status,
                    result.status,
                    result.method,
                    screenshot_str,
                    response_str,
                    datetime.now().isoformat() if result.status == "submitted" else None,
                    result.notes or result.error or "",
                )
            )

        # 8. Dispatch Telegram Notification
        try:
            self.telegram.send_apply_confirmation(
                job=job,
                status=result.status,
                method=result.method,
                pdf_path=resume_pdf_path,
                screenshot_path=result.screenshot_path,
                notes=result.notes or result.error or ""
            )
        except Exception as e:
            logger.warning(f"Failed to dispatch Telegram application confirmation: {e}")

        return result

    def apply_batch(
        self,
        limit: int = 5,
        min_fit_threshold: float = 80.0,
        dry_run: Optional[bool] = None
    ) -> List[ApplyResult]:
        """
        Batch apply to top qualified matches that have not been applied yet.
        """
        is_dry_run = self.dry_run if dry_run is None else dry_run

        with get_db() as conn:
            rows = conn.execute(
                """
                SELECT m.job_id, j.company_name, j.title, m.overall_fit
                FROM matches m
                JOIN jobs j ON m.job_id = j.id
                WHERE m.overall_fit >= ?
                  AND m.pdf_path IS NOT NULL
                  AND m.job_id NOT IN (
                      SELECT m2.job_id FROM applications a
                      JOIN matches m2 ON a.match_id = m2.id
                      WHERE a.status = 'applied' OR a.auto_apply_status = 'submitted'
                  )
                ORDER BY m.overall_fit DESC
                LIMIT ?;
                """,
                (min_fit_threshold, limit)
            ).fetchall()

        results: List[ApplyResult] = []
        logger.info(f"Identified {len(rows)} unapplied candidate matches for batch submission.")

        for row in rows:
            j_id = row["job_id"]
            logger.info(f"Processing candidate Job #{j_id}: {row['company_name']} - {row['title']} (Fit: {row['overall_fit']})")
            res = self.apply_for_job(j_id, dry_run=is_dry_run)
            results.append(res)

            # In live mode, respect cooldown pause between loop submissions
            if not is_dry_run and res.success:
                time.sleep(2)

        return results

    def get_applications_history(self) -> List[Dict[str, Any]]:
        """Return chronological application history records."""
        with get_db() as conn:
            rows = conn.execute(
                """
                SELECT a.id, j.id as job_id, j.company_name, j.title, j.apply_url,
                       a.status, a.auto_apply_status, a.apply_method,
                       a.confirmation_screenshot, a.submit_attempted_at, a.applied_at, a.notes
                FROM applications a
                JOIN matches m ON a.match_id = m.id
                JOIN jobs j ON m.job_id = j.id
                ORDER BY a.submit_attempted_at DESC;
                """
            ).fetchall()

            return [dict(r) for r in rows]
