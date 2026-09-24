import os
import time
import signal
import sys
from datetime import datetime, time as dtime, timedelta
from zoneinfo import ZoneInfo
from typing import Tuple, List, Optional
from rich.console import Console

from resume_agent.logging import logger
from resume_agent.orchestrate.daily import run_daily_pipeline
from resume_agent.jobs.companies import seed_companies_from_yaml
from resume_agent.db import run_migrations

IST = ZoneInfo("Asia/Kolkata")

# The 4 requested daily slots in IST:
# 1. 09:00 AM IST - Morning Scan & Instant Apply
# 2. 01:30 PM IST - Afternoon Scan & Instant Apply
# 3. 05:30 PM IST - Evening Scan & Instant Apply
# 4. 09:00 PM IST - Night Finale Scan & Instant Apply + 9:00 PM Executive Digest
SCHEDULED_SLOTS: List[Tuple[dtime, str, bool]] = [
    (dtime(9, 0), "Morning Scan & Instant Apply", False),
    (dtime(13, 30), "Afternoon Scan & Instant Apply", False),
    (dtime(17, 30), "Evening Scan & Instant Apply", False),
    (dtime(21, 0), "Night Finale Scan & 09:30 PM Executive Digest", True),
]


def get_next_slot(now_ist: Optional[datetime] = None) -> Tuple[datetime, str, bool]:
    """
    Given the current time in IST, calculate the next target slot datetime,
    its descriptive label, and whether it dispatches the evening daily digest.
    """
    if now_ist is None:
        now_ist = datetime.now(IST)

    today = now_ist.date()

    for slot_time, label, is_digest in SCHEDULED_SLOTS:
        candidate_dt = datetime.combine(today, slot_time, tzinfo=IST)
        if candidate_dt > now_ist:
            return candidate_dt, label, is_digest

    # If all slots today have passed, target first slot tomorrow (09:00 AM IST)
    tomorrow = today + timedelta(days=1)
    first_slot_time, first_label, first_digest = SCHEDULED_SLOTS[0]
    return datetime.combine(tomorrow, first_slot_time, tzinfo=IST), first_label, first_digest


def seconds_until_next_slot(now_ist: Optional[datetime] = None) -> Tuple[float, str, bool]:
    """Return the number of seconds remaining until the next slot."""
    if now_ist is None:
        now_ist = datetime.now(IST)

    next_dt, label, is_digest = get_next_slot(now_ist)
    delay = (next_dt - now_ist).total_seconds()
    return max(0.0, delay), label, is_digest


def run_ist_daemon(run_immediately: bool = False, dry_run: bool = False):
    """
    Autonomous Railway/Cloud Daemon that loops continuously, sleeping
    until each designated IST slot to minimize CPU/RAM utilization.
    """
    from resume_agent.logging import setup_logging
    from resume_agent.config import get_settings

    settings = get_settings()
    setup_logging(settings.log_level)

    console = Console()
    console.print("[bold cyan]════════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]   🚀 Resume Agent 4-Slot IST Autonomous Daemon Engine    [/bold cyan]")
    console.print("[bold cyan]════════════════════════════════════════════════════════════[/bold cyan]")
    logger.info("Initializing SQLite database migrations & catalog...")

    # Ensure DB schema, seed companies, and verified jobs exist on container start
    applied = run_migrations()
    seeded = seed_companies_from_yaml()
    from resume_agent.jobs.service import seed_verified_jobs
    seeded_jobs = seed_verified_jobs()
    logger.info(f"Database ready: applied {len(applied)} migrations, loaded {seeded} seed companies, {seeded_jobs} verified fresher roles.")

    # Ensure Candidate Profile and Verified Projects exist in DB
    from resume_agent.profile.service import ensure_candidate_profile
    from resume_agent.github.sync import get_all_projects, sync_projects
    prof = ensure_candidate_profile()
    if prof:
        logger.info(f"Candidate profile active: {prof.full_name} ({prof.college}, CGPA {prof.cgpa})")

    existing_projs = get_all_projects()
    if not existing_projs:
        logger.info("Projects table is empty on volume; synchronizing portfolio from GitHub & verified overrides...")
        try:
            synced_projs = sync_projects(offline=False)
            logger.info(f"Synchronized {len(synced_projs)} projects into candidate portfolio.")
        except Exception as e:
            logger.warning(f"Live GitHub sync failed ({e}), falling back to offline overrides sync...")
            synced_projs = sync_projects(offline=True)
            logger.info(f"Loaded {len(synced_projs)} projects from verified overrides.")
    else:
        logger.info(f"Loaded {len(existing_projs)} verified projects from portfolio.")

    running = True

    def handle_signal(sig, frame):
        nonlocal running
        logger.info(f"Received termination signal ({sig}). Shutting down daemon gracefully...")
        running = False
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    run_on_start = run_immediately or os.environ.get("RUN_ON_STARTUP", "").lower() in ("1", "true", "yes")
    if run_on_start:
        logger.info("Immediate run requested on startup (RUN_ON_STARTUP=true or --run-now). Running pipeline cycle...")
        now = datetime.now(IST)
        # Only send evening digest if close to 9 PM IST (between 20:30 and 22:00)
        is_evening = (now.hour == 20 and now.minute >= 30) or (now.hour == 21) or (now.hour == 22 and now.minute <= 30)
        run_daily_pipeline(
            auto_apply=True,
            send_telegram=True,
            send_digest=is_evening,
            dry_run=dry_run,
            slot_label="Afternoon Catch-Up Scan",
        )

    while running:
        now_ist = datetime.now(IST)
        delay_sec, label, is_digest = seconds_until_next_slot(now_ist)
        next_dt, _, _ = get_next_slot(now_ist)

        hours = int(delay_sec // 3600)
        minutes = int((delay_sec % 3600) // 60)
        secs = int(delay_sec % 60)

        logger.info(
            f"Next Scheduled Slot: [{next_dt.strftime('%Y-%m-%d %I:%M %p IST')}] "
            f"— {label} (Sleeping for {hours}h {minutes}m {secs}s)"
        )

        # Sleep in small increments to respond quickly to termination signals
        sleep_chunk = min(60, delay_sec)
        while delay_sec > 0 and running:
            time.sleep(min(sleep_chunk, delay_sec))
            delay_sec -= sleep_chunk

        if not running:
            break

        logger.info(f"⚡ Slot Triggered: {label}! Starting autonomous execution...")
        try:
            stats = run_daily_pipeline(
                auto_apply=True,
                send_telegram=True,
                send_digest=is_digest,
                dry_run=dry_run,
                slot_label=label,
            )
            logger.info(f"Cycle completed successfully. Stats: {stats}")
        except Exception as e:
            logger.error(f"Error executing slot '{label}': {e}", exc_info=True)

        # Pause 5 seconds to ensure we do not double-fire the exact same second
        time.sleep(5)
