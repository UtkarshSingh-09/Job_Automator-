from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml
from resume_agent.config import get_settings
from resume_agent.db import get_db
from resume_agent.models import CompanyModel
from resume_agent.logging import logger


def load_seed_companies_yaml() -> List[Dict[str, Any]]:
    """Load curated company list from data/config/companies.yaml or fallback seed paths."""
    import shutil
    settings = get_settings()

    candidate_paths = [
        settings.data_dir / "config" / "companies.yaml",
        settings.project_root / "data" / "config" / "companies.yaml",
        Path("/app/seed_config/companies.yaml"),
        Path("/app/data/config/companies.yaml"),
        Path(__file__).resolve().parent.parent.parent.parent / "data" / "config" / "companies.yaml",
    ]

    yaml_path = None
    for p in candidate_paths:
        if p.exists():
            yaml_path = p
            break

    if not yaml_path:
        logger.warning(f"Companies YAML missing at {settings.data_dir / 'config' / 'companies.yaml'}")
        return []

    # Initialize volume location from seed if running with mounted volume
    target_vol_path = settings.data_dir / "config" / "companies.yaml"
    if yaml_path != target_vol_path and not target_vol_path.exists():
        try:
            target_vol_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(yaml_path, target_vol_path)
            logger.info(f"Initialized volume companies catalog at {target_vol_path} from {yaml_path}")
        except Exception as e:
            logger.debug(f"Could not copy seed companies to volume: {e}")

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data.get("companies", []) if isinstance(data, dict) else []


def seed_companies_from_yaml() -> int:
    """
    Load or sync seed companies from companies.yaml into SQLite database.
    If a company has a pre-seeded ats_slug, its detection_status is marked 'resolved'.
    """
    companies = load_seed_companies_yaml()
    seeded_count = 0

    sql = """
    INSERT INTO companies (
        name, domain, tier, ats_provider, ats_slug, detection_status
    ) VALUES (
        :name, :domain, :tier, :ats_provider, :ats_slug, :detection_status
    )
    ON CONFLICT(domain) DO UPDATE SET
        name = excluded.name,
        tier = excluded.tier,
        ats_provider = COALESCE(companies.ats_provider, excluded.ats_provider),
        ats_slug = COALESCE(companies.ats_slug, excluded.ats_slug),
        detection_status = CASE 
            WHEN companies.detection_status = 'resolved' THEN 'resolved'
            ELSE excluded.detection_status
        END;
    """

    with get_db() as conn:
        for c in companies:
            name = c.get("name", "").strip()
            domain = c.get("domain", "").strip().lower()
            if not domain:
                continue

            tier = c.get("tier", 2)
            provider = c.get("ats_provider")
            slug = c.get("ats_slug")
            status = "resolved" if (provider and slug) else "unknown"

            conn.execute(sql, {
                "name": name,
                "domain": domain,
                "tier": tier,
                "ats_provider": provider,
                "ats_slug": slug,
                "detection_status": status,
            })
            seeded_count += 1

    logger.info(f"Seeded/synchronized {seeded_count} companies into database.")
    return seeded_count


def get_unresolved_companies(limit: Optional[int] = None, tier: Optional[int] = None) -> List[CompanyModel]:
    """Retrieve companies that still require ATS detection."""
    query = "SELECT * FROM companies WHERE detection_status = 'unknown'"
    params = []

    if tier is not None:
        query += " AND tier = ?"
        params.append(tier)

    query += " ORDER BY tier ASC, id ASC"

    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)

    with get_db() as conn:
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        return [_row_to_model(r) for r in rows]


def update_company_ats(company_id: int, provider: str, slug: str, status: str = "resolved") -> None:
    """Update ATS detection outcome for a company."""
    with get_db() as conn:
        conn.execute(
            """
            UPDATE companies 
            SET ats_provider = ?, ats_slug = ?, detection_status = ?, last_polled_at = CURRENT_TIMESTAMP
            WHERE id = ?;
            """,
            (provider, slug, status, company_id)
        )


def mark_company_unknown(company_id: int) -> None:
    """Mark company as probed but unresolved."""
    with get_db() as conn:
        conn.execute(
            """
            UPDATE companies 
            SET detection_status = 'unknown', last_polled_at = CURRENT_TIMESTAMP,
                consecutive_failures = consecutive_failures + 1
            WHERE id = ?;
            """,
            (company_id,)
        )


def get_companies_list(status: Optional[str] = None, tier: Optional[int] = None) -> List[CompanyModel]:
    """Retrieve companies filtered by status and tier."""
    query = "SELECT * FROM companies WHERE 1=1"
    params = []

    if status:
        query += " AND detection_status = ?"
        params.append(status)

    if tier is not None:
        query += " AND tier = ?"
        params.append(tier)

    query += " ORDER BY tier ASC, name ASC;"

    with get_db() as conn:
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        return [_row_to_model(r) for r in rows]


def add_custom_company(name: str, domain: str, tier: int = 2, provider: Optional[str] = None, slug: Optional[str] = None) -> None:
    """Add or update a custom company manually."""
    status = "resolved" if (provider and slug) else "unknown"
    sql = """
    INSERT INTO companies (name, domain, tier, ats_provider, ats_slug, detection_status)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(domain) DO UPDATE SET
        name = excluded.name,
        tier = excluded.tier,
        ats_provider = excluded.ats_provider,
        ats_slug = excluded.ats_slug,
        detection_status = excluded.detection_status;
    """
    with get_db() as conn:
        conn.execute(sql, (name, domain.strip().lower(), tier, provider, slug, status))


def _row_to_model(r) -> CompanyModel:
    return CompanyModel(
        id=r["id"],
        name=r["name"],
        domain=r["domain"],
        tier=r["tier"],
        ats_provider=r["ats_provider"],
        ats_slug=r["ats_slug"],
        detection_status=r["detection_status"],
        etag=r["etag"],
        consecutive_failures=r["consecutive_failures"],
    )
