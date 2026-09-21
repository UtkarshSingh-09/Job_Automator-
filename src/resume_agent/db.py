import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, List, Dict, Any
from resume_agent.config import get_settings
from resume_agent.logging import logger


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """
    Establish a connection to the SQLite database with WAL mode and foreign keys enabled.
    """
    settings = get_settings()
    target_path = db_path or settings.db_path
    
    # Ensure parent directory exists
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(target_path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    
    # Critical pragmas for durability and performance
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA busy_timeout = 10000;")
    
    return conn


@contextmanager
def get_db(db_path: Path | None = None) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database connections with automatic commit and rollback.
    """
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def ensure_migration_table(conn: sqlite3.Connection) -> None:
    """Create schema_migrations tracker table if it does not exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()


def run_migrations(db_path: Path | None = None) -> List[str]:
    """
    Execute all pending SQL migrations in alphabetical order.
    Returns the list of newly applied migration file names.
    """
    settings = get_settings()
    migrations_dir = settings.migrations_dir
    applied_now: List[str] = []

    if not migrations_dir.exists():
        logger.warning(f"Migrations directory does not exist: {migrations_dir}")
        return applied_now

    sql_files = sorted(migrations_dir.glob("*.sql"))

    with get_db(db_path) as conn:
        ensure_migration_table(conn)
        
        cursor = conn.execute("SELECT version FROM schema_migrations;")
        already_applied = {row["version"] for row in cursor.fetchall()}

        for sql_file in sql_files:
            version_name = sql_file.name
            if version_name in already_applied:
                continue

            logger.info(f"Applying migration: {version_name}")
            with open(sql_file, "r", encoding="utf-8") as f:
                script = f.read()

            conn.executescript(script)
            conn.execute(
                "INSERT INTO schema_migrations (version) VALUES (?);",
                (version_name,)
            )
            applied_now.append(version_name)

    return applied_now


def get_table_counts(db_path: Path | None = None) -> Dict[str, int]:
    """Return dictionary of table names and their row counts."""
    counts: Dict[str, int] = {}
    with get_db(db_path) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
        )
        tables = [row["name"] for row in cursor.fetchall()]
        
        for table in tables:
            c = conn.execute(f"SELECT COUNT(*) as cnt FROM {table};")
            counts[table] = c.fetchone()["cnt"]
            
    return counts
