import html
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import httpx
from rich.panel import Panel

from resume_agent.config import get_settings
from resume_agent.models import JobModel, MatchModel
from resume_agent.logging import logger, console


class TelegramClient:
    """
    Production Telegram Bot API client for candidate match dispatch and morning digests.
    Supports native PDF document attachments, HTML formatting, and inline action buttons.
    Includes built-in dry-run and mock mode when credentials are not configured.
    """

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
        dry_run: bool = False,
        timeout: float = 30.0
    ):
        settings = get_settings()
        self.bot_token = bot_token or settings.telegram_bot_token
        self.chat_id = chat_id or settings.telegram_chat_id
        self.dry_run = dry_run
        self.timeout = timeout
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else ""

    @property
    def is_configured(self) -> bool:
        """Check if Telegram API credentials are fully configured."""
        return bool(self.bot_token and self.chat_id)

    def _record_dry_run(self, action: str, payload: Dict[str, Any]) -> None:
        """Save and log simulated Telegram notification in dry-run mode."""
        settings = get_settings()
        notif_dir = settings.data_dir / "notifications"
        notif_dir.mkdir(parents=True, exist_ok=True)
        ts = int(time.time())
        record_path = notif_dir / f"telegram_{action}_{ts}.json"
        with open(record_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        preview = payload.get("text") or payload.get("caption") or str(payload)
        console.print(
            Panel(
                f"[bold cyan][DRY-RUN TELEGRAM NOTIFICATION][/bold cyan]\n"
                f"[yellow]Action:[/yellow] {action}\n"
                f"[yellow]Chat ID:[/yellow] {self.chat_id or 'Simulated'}\n\n"
                f"{preview[:500]}...",
                title="Telegram Simulation",
                border_style="cyan",
            )
        )
        logger.info(f"[DRY-RUN] Saved simulated Telegram payload to {record_path}")

    def send_message(
        self,
        text: str,
        parse_mode: str = "HTML",
        reply_markup: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send an HTML-formatted message to the candidate."""
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False,
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup

        if self.dry_run or not self.is_configured:
            self._record_dry_run("send_message", payload)
            return True

        url = f"{self.base_url}/sendMessage"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                if data.get("ok"):
                    logger.info("Telegram message dispatched successfully.")
                    return True
                else:
                    logger.error(f"Telegram API error: {data.get('description')}")
                    return False
        except Exception as e:
            logger.error(f"Failed to dispatch Telegram message: {e}")
            return False

    def send_document(
        self,
        document_path: Path,
        caption: str = "",
        parse_mode: str = "HTML",
        reply_markup: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Upload and send a PDF document (e.g. ATS Resume) with caption."""
        doc_p = Path(document_path)
        if not doc_p.exists():
            logger.error(f"Document file not found: {doc_p}")
            return False

        payload = {
            "chat_id": self.chat_id,
            "caption": caption,
            "parse_mode": parse_mode,
            "document_path": str(doc_p),
            "file_size_bytes": doc_p.stat().st_size,
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup

        if self.dry_run or not self.is_configured:
            self._record_dry_run("send_document", payload)
            return True

        url = f"{self.base_url}/sendDocument"
        data = {
            "chat_id": self.chat_id,
            "caption": caption,
            "parse_mode": parse_mode,
        }
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)

        try:
            with open(doc_p, "rb") as f:
                files = {"document": (doc_p.name, f, "application/pdf")}
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.post(url, data=data, files=files)
                    resp.raise_for_status()
                    res_json = resp.json()
                    if res_json.get("ok"):
                        logger.info(f"Telegram document '{doc_p.name}' dispatched successfully.")
                        return True
                    else:
                        logger.error(f"Telegram sendDocument error: {res_json.get('description')}")
                        return False
        except Exception as e:
            logger.error(f"Failed to upload Telegram document: {e}")
            return False

    def send_match_alert(
        self,
        job: JobModel,
        match: MatchModel,
        pdf_path: Optional[Path] = None
    ) -> bool:
        """
        Send an individual candidate match alert with company, role, match score,
        tailored projects, application link button, and attached ATS PDF.
        """
        company_escaped = html.escape(job.company_name)
        title_escaped = html.escape(job.title)
        loc_escaped = html.escape(f"{job.location or 'Global'} ({job.remote_type or 'Onsite'})")
        fit_score = match.overall_fit

        # Format flagship project highlights
        proj_lines = []
        for p in match.selected_projects[:3]:
            r_name = html.escape(p.get("repo_name", ""))
            relevance = html.escape(p.get("relevance", ""))
            proj_lines.append(f"• <b>{r_name}</b>: <i>{relevance[:65]}...</i>" if relevance else f"• <b>{r_name}</b>")

        projects_block = "\n".join(proj_lines) if proj_lines else "• Tailored flagship portfolio"

        caption = (
            f"🎯 <b>NEW INTERNSHIP MATCH</b> (Fit: <b>{fit_score:.1f}/100</b>)\n\n"
            f"🏢 <b>Company:</b> {company_escaped}\n"
            f"💼 <b>Role:</b> {title_escaped}\n"
            f"📍 <b>Location:</b> {loc_escaped}\n\n"
            f"🧠 <b>Selected Portfolio Projects:</b>\n{projects_block}\n\n"
            f"📄 <b>ATS Resume:</b> 1-Page Compliant PDF Attached below"
        )

        reply_markup = None
        if job.apply_url:
            reply_markup = {
                "inline_keyboard": [
                    [
                        {"text": "🚀 Apply on Career Page", "url": job.apply_url}
                    ]
                ]
            }

        if pdf_path and Path(pdf_path).exists():
            return self.send_document(
                document_path=Path(pdf_path),
                caption=caption,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
        else:
            return self.send_message(
                text=caption,
                parse_mode="HTML",
                reply_markup=reply_markup
            )

    def send_daily_digest(self, stats: Dict[str, Any]) -> bool:
        """
        Send the 09:00 PM IST executive evening briefing summarizing pipeline activity,
        including direct career page links and attached tailored ATS resumes for all applied jobs.
        """
        date_str = stats.get("date", time.strftime("%Y-%m-%d"))
        boards_count = stats.get("boards_monitored", 41)
        jobs_ingested = stats.get("jobs_ingested", 0)
        matches_found = stats.get("matches_found", 0)
        resumes_generated = stats.get("resumes_generated", 0)
        resumes_validated = stats.get("resumes_validated", 0)
        applied_count = stats.get("applied_count", 0)

        match_items = list(stats.get("matches", []))

        # Query database to aggregate all jobs processed/applied throughout the entire day
        try:
            from resume_agent.db import get_db
            with get_db() as conn:
                db_apps = conn.execute("""
                    SELECT j.company_name as company, j.title, j.apply_url, m.overall_fit as score, m.pdf_path
                    FROM applications a
                    JOIN matches m ON a.match_id = m.id
                    JOIN jobs j ON m.job_id = j.id
                    WHERE DATE(a.submit_attempted_at) = DATE('now')
                       OR DATE(a.applied_at) = DATE('now')
                    ORDER BY a.submit_attempted_at DESC;
                """).fetchall()
                if db_apps:
                    applied_count = max(applied_count, len(db_apps))
                    existing_pairs = {(m.get("company"), m.get("title")) for m in match_items}
                    for r in db_apps:
                        pair = (r["company"], r["title"])
                        if pair not in existing_pairs:
                            match_items.append(dict(r))
                            existing_pairs.add(pair)
        except Exception as e:
            logger.debug(f"Could not aggregate daily apps from DB: {e}")
        if match_items:
            bullets = []
            for idx, m in enumerate(match_items[:8], 1):
                comp = html.escape(m.get("company", ""))
                tit = html.escape(m.get("title", ""))
                sc = m.get("score", 0.0)
                apply_url = m.get("apply_url", "")
                link_html = f" | <a href='{apply_url}'>Career Link</a>" if apply_url else ""
                bullets.append(f"{idx}. 🏢 <b>{comp}</b> — {tit} (<b>{sc:.1f}/100</b>){link_html}")
            matches_section = "🚀 <b>Roles & Career Links:</b>\n" + "\n".join(bullets)
        else:
            matches_section = "ℹ️ <i>0 new internships exceeded threshold today. Continuous monitoring active across 41 boards.</i>"

        text = (
            f"🌙 <b>DAILY 9:00 PM EXECUTIVE BRIEFING — {date_str}</b>\n\n"
            f"📊 <b>Today's Autonomous Pipeline Activity:</b>\n"
            f"• Verified ATS Boards Monitored: <b>{boards_count}</b>\n"
            f"• New Job Postings Analyzed: <b>{jobs_ingested}</b>\n"
            f"• High-Fit Matches Identified: <b>{matches_found}</b>\n"
            f"• Tailored Resumes Generated: <b>{resumes_generated}</b>\n"
            f"• 7-Gate ATS Validations Passed: <b>{resumes_validated}</b>\n"
            f"• Applications Auto-Submitted: <b>{applied_count}</b>\n\n"
            f"{matches_section}\n\n"
            f"📎 <i>Tailored 1-page ATS resumes dispatched below...</i>\n\n"
            f"⚡ <i>Orchestrated by n8n Visual Workflow Engine & Resume Agent v0.1.0</i>"
        )

        ok = self.send_message(text=text, parse_mode="HTML")

        # Automatically dispatch PDFs for applied / validated matches
        for m in match_items:
            pdf_str = m.get("pdf_path")
            if pdf_str and Path(pdf_str).exists():
                comp = m.get("company", "")
                tit = m.get("title", "")
                url = m.get("apply_url", "")
                markup = {"inline_keyboard": [[{"text": "🔗 View Job Posting", "url": url}]]} if url else None
                self.send_document(
                    document_path=Path(pdf_str),
                    caption=f"📄 <b>ATS Resume:</b> {comp} — {tit}",
                    reply_markup=markup
                )

        return ok

    def send_photo(
        self,
        photo_path: Path,
        caption: str = "",
        parse_mode: str = "HTML",
        reply_markup: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Upload and send a photo screenshot to Telegram."""
        photo_p = Path(photo_path)
        if not photo_p.exists():
            logger.error(f"Photo file not found: {photo_p}")
            return False

        payload = {
            "chat_id": self.chat_id,
            "caption": caption,
            "parse_mode": parse_mode,
            "photo_path": str(photo_p),
            "file_size_bytes": photo_p.stat().st_size,
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup

        if self.dry_run or not self.is_configured:
            self._record_dry_run("send_photo", payload)
            return True

        url = f"{self.base_url}/sendPhoto"
        data = {
            "chat_id": self.chat_id,
            "caption": caption,
            "parse_mode": parse_mode,
        }
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)

        try:
            with open(photo_p, "rb") as f:
                files = {"photo": (photo_p.name, f, "image/png")}
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.post(url, data=data, files=files)
                    resp.raise_for_status()
                    res_json = resp.json()
                    if res_json.get("ok"):
                        logger.info(f"Telegram photo '{photo_p.name}' dispatched successfully.")
                        return True
                    else:
                        logger.error(f"Telegram sendPhoto error: {res_json.get('description')}")
                        return False
        except Exception as e:
            logger.error(f"Failed to upload Telegram photo: {e}")
            return False

    def send_apply_confirmation(
        self,
        job: JobModel,
        status: str,
        method: str,
        pdf_path: Optional[Path] = None,
        screenshot_path: Optional[Path] = None,
        notes: str = ""
    ) -> bool:
        """
        Send application dispatch confirmation or safety intervention alert to Telegram.
        """
        comp = html.escape(job.company_name)
        title = html.escape(job.title)
        apply_url = job.apply_url

        reply_markup = None
        if apply_url:
            reply_markup = {
                "inline_keyboard": [
                    [{"text": "🔗 View Job Page", "url": apply_url}]
                ]
            }

        if status == "submitted":
            caption = (
                f"✅ <b>APPLICATION SUBMITTED!</b>\n\n"
                f"🏢 <b>Company:</b> {comp}\n"
                f"💼 <b>Role:</b> {title}\n"
                f"⚙️ <b>Submission Method:</b> <code>{method}</code>\n"
                f"📝 <b>Status:</b> Success\n\n"
                f"📸 Confirmation screenshot attached."
            )
        elif status == "dry_run":
            caption = (
                f"🧪 <b>SIMULATED APPLICATION (DRY-RUN)</b>\n\n"
                f"🏢 <b>Company:</b> {comp}\n"
                f"💼 <b>Role:</b> {title}\n"
                f"⚙️ <b>Engine:</b> <code>{method}</code>\n"
                f"📝 <b>Note:</b> {html.escape(notes or 'Form filled and verified.')}\n\n"
                f"📸 Pre-submit form screenshot attached below."
            )
        else:
            caption = (
                f"⚠️ <b>AUTO-APPLY SKIPPED (Manual Action Needed)</b>\n\n"
                f"🏢 <b>Company:</b> {comp}\n"
                f"💼 <b>Role:</b> {title}\n"
                f"🛑 <b>Reason:</b> <code>{status}</code> — {html.escape(notes)}\n\n"
                f"Please click below to submit manually:"
            )

        # Dispatch photo screenshot if available
        if screenshot_path and Path(screenshot_path).exists():
            self.send_photo(Path(screenshot_path), caption=caption, reply_markup=reply_markup)
        else:
            self.send_message(text=caption, reply_markup=reply_markup)

        # Also dispatch PDF resume if available
        if pdf_path and Path(pdf_path).exists() and status != "dry_run":
            caption_prefix = "📎 ATS Resume Submitted" if status == "submitted" else "📎 Tailored ATS Resume (Ready to Upload)"
            self.send_document(
                document_path=Path(pdf_path),
                caption=f"{caption_prefix} for {comp} — {title}"
            )

        return True

    def send_error_alert(self, error_message: str, stage: str = "") -> bool:
        """Send instant visual alert when an error occurs in the daily pipeline."""
        stage_str = f" at stage <b>{html.escape(stage)}</b>" if stage else ""
        err_escaped = html.escape(error_message[:400])

        text = (
            f"🚨 <b>RESUME AGENT PIPELINE ALERT</b>\n\n"
            f"An error occurred{stage_str}:\n"
            f"<code>{err_escaped}</code>\n\n"
            f"⚠️ Please inspect system logs at <code>data/agent.log</code>."
        )
        return self.send_message(text=text, parse_mode="HTML")
