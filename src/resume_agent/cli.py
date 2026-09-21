import click
from rich.table import Table
from rich.panel import Panel
from resume_agent import __version__
from resume_agent.config import get_settings
from resume_agent.db import run_migrations, get_table_counts
from resume_agent.logging import setup_logging, console, print_success, print_error, print_info


@click.group()
@click.version_option(version=__version__, prog_name="resume-agent")
def cli():
    """Autonomous Internship-Matching, Resume Generation & Auto-Apply System."""
    pass


@cli.command("init")
def init_cmd():
    """Initialize database and execute all schema migrations."""
    settings = get_settings()
    setup_logging(settings.log_level)
    console.print(Panel.fit(
        f"[bold cyan]Resume Agent v{__version__}[/bold cyan]\n"
        f"Database target: [yellow]{settings.db_path}[/yellow]",
        title="Database Initialization"
    ))

    try:
        applied = run_migrations()
        if applied:
            print_success(f"Applied {len(applied)} migration(s): {', '.join(applied)}")
        else:
            print_info("Database is already up to date. No new migrations.")

        counts = get_table_counts()
        table = Table(title="Database Tables Status", border_style="cyan")
        table.add_column("Table Name", style="bold white")
        table.add_column("Row Count", justify="right", style="green")

        for tbl, cnt in counts.items():
            table.add_row(tbl, str(cnt))

        console.print(table)
        print_success("Database initialized successfully in WAL mode.")

    except Exception as e:
        print_error(f"Failed to initialize database: {e}")
        raise click.Abort()


@cli.command("status")
def status_cmd():
    """Check system health, database state, and environment configuration."""
    settings = get_settings()
    setup_logging(settings.log_level)
    
    console.print(Panel.fit(
        f"[bold cyan]Resume Agent System Status[/bold cyan]\n"
        f"Target Candidate: [bold]Utkarsh Singh[/bold] (GitHub: {settings.github_username})",
        title="System Health"
    ))

    # 1. Environment variables check
    env_table = Table(title="Configuration & Credentials", border_style="blue")
    env_table.add_column("Service / Variable", style="bold white")
    env_table.add_column("Status", style="bold")
    env_table.add_column("Details", style="dim")

    def mask_key(k: str | None) -> str:
        if not k:
            return "Not configured"
        if len(k) <= 8:
            return "Configured (***)"
        return f"{k[:4]}...{k[-4:]}"

    env_table.add_row(
        "Anthropic API Key",
        "[green]Ready[/green]" if settings.anthropic_api_key else "[yellow]Missing[/yellow]",
        mask_key(settings.anthropic_api_key)
    )
    env_table.add_row(
        "GitHub Token (PAT)",
        "[green]Ready[/green]" if settings.github_token else "[yellow]Missing[/yellow]",
        mask_key(settings.github_token)
    )
    env_table.add_row(
        "Telegram Bot Token",
        "[green]Ready[/green]" if settings.telegram_bot_token else "[yellow]Missing[/yellow]",
        mask_key(settings.telegram_bot_token)
    )
    env_table.add_row(
        "Telegram Chat ID",
        "[green]Ready[/green]" if settings.telegram_chat_id else "[yellow]Missing[/yellow]",
        settings.telegram_chat_id or "Not configured"
    )
    env_table.add_row(
        "Database Path",
        "[green]Ready[/green]" if settings.db_path.exists() else "[red]Not found (run init)[/red]",
        str(settings.db_path)
    )
    console.print(env_table)

    # 2. Database statistics
    if settings.db_path.exists():
        counts = get_table_counts()
        db_table = Table(title="Database Record Counts", border_style="cyan")
        db_table.add_column("Entity / Table", style="bold white")
        db_table.add_column("Records", justify="right", style="green")

        for tbl, cnt in counts.items():
            db_table.add_row(tbl, str(cnt))
        console.print(db_table)
    else:
        print_info("Run [bold cyan]resume-agent init[/bold cyan] to create database tables.")


# --- Stub Groups for Future Phases ---

@cli.group("profile")
def profile_group():
    """Manage candidate identity and resume extraction (Phase 2)."""
    pass

@profile_group.command("parse")
def profile_parse_cmd():
    print_info("Profile parser will be available in Phase 2.")

@cli.group("github")
def github_group():
    """Sync repositories and compute project scores (Phase 3)."""
    pass

@github_group.command("sync")
def github_sync_cmd():
    print_info("GitHub synchronization will be available in Phase 3.")

@cli.group("companies")
def companies_group():
    """Manage company catalog and ATS detection (Phase 4)."""
    pass

@cli.group("jobs")
def jobs_group():
    """Ingest, deduplicate, and filter job postings (Phase 5)."""
    pass

@cli.command("match")
def match_cmd():
    """Run semantic matching against active jobs (Phase 6)."""
    print_info("Semantic matching will be available in Phase 6.")

@cli.command("generate")
def generate_cmd():
    """Generate tailored resume and compile PDF (Phase 7)."""
    print_info("Resume generator will be available in Phase 7.")

@cli.command("validate")
def validate_cmd():
    """Run mechanical ATS validation suite (Phase 8)."""
    print_info("Validation suite will be available in Phase 8.")

@cli.command("daily")
def daily_cmd():
    """Run full automated daily pipeline (Phase 9)."""
    print_info("Daily orchestrator will be available in Phase 9.")

@cli.command("apply")
def apply_cmd():
    """Execute auto-apply submission engine (Phase 10)."""
    print_info("Auto-apply engine will be available in Phase 10.")


if __name__ == "__main__":
    cli()
