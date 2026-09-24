from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from resume_agent.db import get_db
from resume_agent.models import JobModel, CompanyModel
from resume_agent.jobs.companies import get_companies_list
from resume_agent.jobs.sources import get_adapter
from resume_agent.logging import logger


def ingest_jobs(
    limit_companies: Optional[int] = None,
    source_filter: Optional[str] = None,
    dry_run: bool = False
) -> Dict[str, int]:
    """
    Ingest jobs across all resolved companies in database.
    Normalizes, deduplicates, and evaluates filter criteria.
    Returns summary statistics: {'companies_polled': int, 'total_fetched': int, 'new_inserted': int, 'passed_filter': int}
    """
    companies = get_companies_list(status="resolved")
    if source_filter:
        companies = [c for c in companies if c.ats_provider and c.ats_provider.lower() == source_filter.lower()]

    if limit_companies:
        companies = companies[:limit_companies]

    stats = {
        "companies_polled": len(companies),
        "total_fetched": 0,
        "new_inserted": 0,
        "passed_filter": 0,
    }

    import concurrent.futures

    logger.info(f"Starting job ingestion for {len(companies)} resolved company endpoints...")

    def _fetch_one(c):
        if not c.ats_provider or not c.ats_slug:
            return c, []
        adapter = get_adapter(c.ats_provider)
        if not adapter:
            return c, []
        try:
            return c, adapter.fetch_jobs(c)
        except Exception as e:
            logger.debug(f"Error fetching {c.name}: {e}")
            return c, []

    max_workers = min(15, max(1, len(companies)))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_fetch_one, c) for c in companies]
        for f in concurrent.futures.as_completed(futures):
            company, raw_jobs = f.result()
            adapter = get_adapter(company.ats_provider)
            if not adapter:
                continue
            stats["total_fetched"] += len(raw_jobs)
            for raw_item in raw_jobs:
                try:
                    job = adapter.normalize_job(raw_item, company)
                    if job.passed_filter:
                        stats["passed_filter"] += 1

                    if not dry_run:
                        inserted = _upsert_job_to_db(job)
                        if inserted:
                            stats["new_inserted"] += 1
                except Exception as e:
                    logger.debug(f"Error normalizing job for {company.name}: {e}")

    logger.info(f"Ingestion complete: {stats}")
    return stats


def _upsert_job_to_db(job: JobModel) -> bool:
    """
    Upsert job into SQLite database.
    Returns True if a new row was inserted, False if updated existing.
    """
    sql = """
    INSERT INTO jobs (
        company_id, company_name, title, location, remote_type,
        description_md, apply_url, source, source_job_id,
        content_hash, passed_filter, first_seen_at, last_seen_at
    ) VALUES (
        :company_id, :company_name, :title, :location, :remote_type,
        :description_md, :apply_url, :source, :source_job_id,
        :content_hash, :passed_filter, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
    )
    ON CONFLICT(content_hash) DO UPDATE SET
        last_seen_at = CURRENT_TIMESTAMP,
        passed_filter = excluded.passed_filter,
        description_md = excluded.description_md,
        apply_url = excluded.apply_url;
    """
    with get_db() as conn:
        cursor = conn.cursor()
        # Check if already exists to track new insertions
        existing = cursor.execute(
            "SELECT id FROM jobs WHERE content_hash = ?;", (job.content_hash,)
        ).fetchone()

        cursor.execute(sql, {
            "company_id": job.company_id,
            "company_name": job.company_name,
            "title": job.title,
            "location": job.location,
            "remote_type": job.remote_type,
            "description_md": job.description_md,
            "apply_url": job.apply_url,
            "source": job.source,
            "source_job_id": job.source_job_id,
            "content_hash": job.content_hash,
            "passed_filter": 1 if job.passed_filter else 0,
        })
        return existing is None


def get_jobs(passed_only: bool = True, limit: int = 50) -> List[JobModel]:
    """Retrieve ingested job listings from database."""
    query = "SELECT * FROM jobs"
    params = []

    if passed_only:
        query += " WHERE passed_filter = 1"

    query += " ORDER BY id DESC LIMIT ?;"
    params.append(limit)

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
        return [_row_to_job(r) for r in rows]


def get_job_by_id(job_id: int) -> Optional[JobModel]:
    """Retrieve a single job listing by ID."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?;", (job_id,)).fetchone()
        return _row_to_job(row) if row else None


def _row_to_job(r) -> JobModel:
    return JobModel(
        id=r["id"],
        company_id=r["company_id"],
        company_name=r["company_name"],
        title=r["title"],
        location=r["location"],
        remote_type=r["remote_type"],
        description_md=r["description_md"],
        apply_url=r["apply_url"],
        source=r["source"],
        source_job_id=r["source_job_id"],
        content_hash=r["content_hash"],
        passed_filter=bool(r["passed_filter"]),
    )


def seed_verified_jobs() -> int:
    """
    Seed verified fresher/intern jobs from data/config/seed_jobs.json into SQLite.
    Guarantees container and fresh cloud instances always have a populated catalog.
    """
    import json
    from resume_agent.config import get_settings
    settings = get_settings()

    candidate_paths = [
        settings.data_dir / "config" / "seed_jobs.json",
        settings.project_root / "data" / "config" / "seed_jobs.json",
        Path("/app/seed_config/seed_jobs.json"),
        Path("/app/data/config/seed_jobs.json"),
        Path(__file__).resolve().parent.parent.parent.parent / "data" / "config" / "seed_jobs.json",
    ]

    seed_file = None
    for p in candidate_paths:
        if p.exists():
            seed_file = p
            break

    if not seed_file:
        logger.debug("No seed_jobs.json found; skipping seed.")
        return 0

    try:
        with open(seed_file, "r", encoding="utf-8") as f:
            jobs_data = json.load(f)
    except Exception as e:
        logger.warning(f"Failed to read seed_jobs.json: {e}")
        return 0

    inserted_count = 0
    for j in jobs_data:
        try:
            job = JobModel(
                company_id=j.get("company_id"),
                company_name=j.get("company_name", ""),
                title=j.get("title", ""),
                location=j.get("location", ""),
                remote_type=j.get("remote_type", "Onsite"),
                description_md=j.get("description_md", ""),
                apply_url=j.get("apply_url", ""),
                source=j.get("source", "greenhouse"),
                source_job_id=str(j.get("source_job_id", "")),
                content_hash=j.get("content_hash", ""),
                passed_filter=True,
            )
            if _upsert_job_to_db(job):
                inserted_count += 1
        except Exception as e:
            logger.debug(f"Error seeding job {j.get('title')}: {e}")

    logger.info(f"Verified jobs catalog: loaded {len(jobs_data)} entries, inserted {inserted_count} new.")
    return inserted_count

