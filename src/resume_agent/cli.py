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
@click.option("--pdf", type=click.Path(exists=True), default=None, help="Path to resume PDF file (defaults to data/input/old_resume.pdf)")
@click.option("--force", is_flag=True, help="Force re-parsing even if profile is already confirmed")
@click.option("--confirm-now", is_flag=True, help="Automatically confirm the parsed profile without prompt")
def profile_parse_cmd(pdf: str | None, force: bool, confirm_now: bool):
    """Parse candidate resume PDF and extract profile into database."""
    from pathlib import Path
    from resume_agent.profile.parser import extract_text_from_pdf, parse_profile_deterministic
    from resume_agent.profile.service import save_profile, get_profile, confirm_profile

    settings = get_settings()
    setup_logging(settings.log_level)

    # Check if already confirmed
    existing = get_profile()
    if existing and existing.confirmed_at and not force:
        print_warning(
            f"Profile is already confirmed on {existing.confirmed_at.strftime('%Y-%m-%d %H:%M')}. "
            "Use --force to overwrite."
        )
        return

    pdf_path = Path(pdf) if pdf else settings.data_dir / "input" / "old_resume.pdf"
    if not pdf_path.exists():
        print_error(f"Resume PDF not found at: {pdf_path}")
        raise click.Abort()

    console.print(f"[bold cyan]Parsing resume PDF:[/bold cyan] {pdf_path}")
    raw_text = extract_text_from_pdf(pdf_path)
    profile = parse_profile_deterministic(raw_text)

    save_profile(profile)
    print_success("Extracted profile saved to database!")

    # Display profile preview
    _display_profile(profile)

    if confirm_now:
        confirm_profile()
        print_success("Profile automatically confirmed!")
    else:
        # Prompt for confirmation
        if click.confirm("\nAre these candidate profile details correct?", default=True):
            confirm_profile()
            print_success("Candidate profile verified and confirmed! Integrity gate PASSED.")
        else:
            print_warning(
                "Profile saved as unconfirmed. Run 'resume-agent profile edit' or "
                "'resume-agent profile confirm' after correcting."
            )


@profile_group.command("show")
def profile_show_cmd():
    """Display the currently stored candidate profile."""
    from resume_agent.profile.service import get_profile

    settings = get_settings()
    setup_logging(settings.log_level)

    profile = get_profile()
    if not profile:
        print_error("No profile found in database. Run 'resume-agent profile parse' first.")
        return

    _display_profile(profile)


@profile_group.command("confirm")
def profile_confirm_cmd():
    """Manually confirm the candidate profile (satisfies Human Confirmation Gate)."""
    from resume_agent.profile.service import get_profile, confirm_profile

    settings = get_settings()
    setup_logging(settings.log_level)

    profile = get_profile()
    if not profile:
        print_error("No profile found to confirm. Run 'resume-agent profile parse' first.")
        return

    confirm_profile()
    print_success("Candidate profile confirmed! confirmed_at timestamp has been updated.")


@profile_group.command("edit")
@click.option("--field", required=True, help="Field to edit (e.g. cgpa, phone, college, degree)")
@click.option("--value", required=True, help="New value for the field")
def profile_edit_cmd(field: str, value: str):
    """Edit a single field in the candidate profile."""
    from resume_agent.profile.service import update_profile_field, get_profile

    settings = get_settings()
    setup_logging(settings.log_level)

    profile = get_profile()
    if not profile:
        print_error("No profile found to edit. Run 'resume-agent profile parse' first.")
        return

    # Convert numeric fields if applicable
    parsed_value: Any = value
    if field == "cgpa":
        try:
            parsed_value = float(value)
        except ValueError:
            print_error("CGPA must be a valid float (e.g. 8.78)")
            return
    elif field == "grad_year":
        try:
            parsed_value = int(value)
        except ValueError:
            print_error("Graduation year must be a valid integer (e.g. 2028)")
            return

    try:
        update_profile_field(field, parsed_value)
        print_success(f"Updated '{field}' to '{parsed_value}'.")
    except Exception as e:
        print_error(f"Failed to update field: {e}")


def _display_profile(profile):
    """Render structured profile overview."""
    confirmation_status = (
        f"[green]✔ Confirmed on {profile.confirmed_at.strftime('%Y-%m-%d %H:%M')}[/green]"
        if profile.confirmed_at else
        "[bold red]✖ Unconfirmed (Action Required: run 'resume-agent profile confirm')[/bold red]"
    )

    console.print(Panel.fit(
        f"[bold white]{profile.full_name}[/bold white]\n"
        f"Email: [cyan]{profile.email}[/cyan] | Phone: [cyan]{profile.phone}[/cyan]\n"
        f"Location: {profile.location}\n"
        f"GitHub: [blue]{profile.github_url}[/blue] | LinkedIn: [blue]{profile.linkedin_url}[/blue]\n"
        f"Status: {confirmation_status}",
        title="Candidate Identity"
    ))

    # Academics Table
    acad_table = Table(title="Academic Credentials", border_style="cyan")
    acad_table.add_column("Institution", style="bold white")
    acad_table.add_column("Degree & Branch")
    acad_table.add_column("Grad Year", justify="center")
    acad_table.add_column("CGPA", justify="center", style="bold green")

    acad_table.add_row(
        profile.college or "N/A",
        f"{profile.degree or 'B.Tech'} ({profile.branch or 'CSE'})",
        str(profile.grad_year or "N/A"),
        f"{profile.cgpa:.2f}/10.00" if profile.cgpa else "N/A"
    )
    console.print(acad_table)

    # Skills Summary
    if profile.skills:
        console.print(f"\n[bold cyan]Technical Skills ({len(profile.skills)} extracted):[/bold cyan]")
        console.print(", ".join(profile.skills[:25]) + ("..." if len(profile.skills) > 25 else ""))

    # Achievements Summary
    if profile.achievements:
        console.print(f"\n[bold cyan]Honors & Achievements ({len(profile.achievements)} extracted):[/bold cyan]")
        for ach in profile.achievements[:4]:
            console.print(f"  • {ach}")

@cli.group("github")
def github_group():
    """Sync repositories and compute project scores (Phase 3)."""
    pass


@github_group.command("sync")
@click.option("--username", default=None, help="GitHub username to sync (defaults to config)")
@click.option("--offline", is_flag=True, help="Force offline sync from local overrides only")
def github_sync_cmd(username: str | None, offline: bool):
    """Sync candidate repositories, compute quality scores, and merge manual notes."""
    from resume_agent.github.sync import sync_projects

    settings = get_settings()
    setup_logging(settings.log_level)

    user = username or settings.github_username
    console.print(Panel.fit(
        f"[bold cyan]Synchronizing Project Portfolio Corpus[/bold cyan]\n"
        f"Target User: [bold]{user}[/bold] (Mode: {'Offline' if offline else 'Hybrid GitHub/Local'})",
        title="GitHub Sync"
    ))

    projects = sync_projects(username=user, offline=offline)
    print_success(f"Synchronized {len(projects)} projects into database!")

    # Display summary table
    _display_projects_table(projects)


@cli.group("projects")
def projects_group():
    """Manage and inspect the candidate's project portfolio corpus."""
    pass


@projects_group.command("list")
@click.option("--min-score", default=0.0, type=float, help="Filter projects by minimum quality score")
def projects_list_cmd(min_score: float):
    """List all candidate projects sorted by priority and quality score."""
    from resume_agent.github.sync import get_all_projects

    settings = get_settings()
    setup_logging(settings.log_level)

    projects = get_all_projects(min_score=min_score)
    if not projects:
        print_info("No projects found in database. Run 'resume-agent github sync' first.")
        return

    _display_projects_table(projects)


@projects_group.command("show")
@click.argument("repo_name")
def projects_show_cmd(repo_name: str):
    """Show detailed metadata, manual notes, and metrics for a single project."""
    from resume_agent.github.sync import get_project_by_repo

    settings = get_settings()
    setup_logging(settings.log_level)

    project = get_project_by_repo(repo_name)
    if not project:
        print_error(f"Project '{repo_name}' not found in database.")
        return

    priority_label = (
        "[bold green]P0 (Top Priority)[/bold green]" if project.priority == 1 else
        f"[yellow]Priority {project.priority}[/yellow]"
    )

    console.print(Panel.fit(
        f"[bold white]{project.display_name}[/bold white] ({project.repo_name})\n"
        f"Priority: {priority_label} | Quality Score: [bold green]{project.quality_score}/100[/bold green]\n"
        f"Primary Language: [cyan]{project.primary_language}[/cyan] | Stars: ⭐ {project.stars} | Commits: {project.commit_count}\n"
        f"Tests: {'[green]✔ Yes[/green]' if project.has_tests else '[red]✖ No[/red]'} | "
        f"CI/CD: {'[green]✔ Yes[/green]' if project.has_ci else '[yellow]✖ No[/yellow]'} | "
        f"Docker: {'[green]✔ Yes[/green]' if project.has_docker else '[yellow]✖ No[/yellow]'}\n\n"
        f"[bold cyan]Description:[/bold cyan]\n{project.description}\n\n"
        f"[bold cyan]Grounded Manual Notes (Verified Metrics):[/bold cyan]\n{project.manual_notes}",
        title=f"Project Details: {project.display_name}"
    ))


def _display_projects_table(projects):
    """Render Rich table of projects."""
    table = Table(title="Candidate Project Portfolio Corpus", border_style="cyan")
    table.add_column("Priority", justify="center", style="bold")
    table.add_column("Display Name", style="bold white")
    table.add_column("Repository", style="dim")
    table.add_column("Language", style="cyan")
    table.add_column("Score", justify="right", style="bold green")
    table.add_column("Tests", justify="center")
    table.add_column("Docker", justify="center")
    table.add_column("CI", justify="center")

    for p in projects:
        p_badge = f"[bold green]P{p.priority}[/bold green]" if p.priority == 1 else f"P{p.priority}"
        table.add_row(
            p_badge,
            p.display_name,
            p.repo_name,
            p.primary_language or "N/A",
            f"{p.quality_score:.1f}",
            "[green]✔[/green]" if p.has_tests else "[dim]—[/dim]",
            "[green]✔[/green]" if p.has_docker else "[dim]—[/dim]",
            "[green]✔[/green]" if p.has_ci else "[dim]—[/dim]",
        )

    console.print(table)

@cli.group("companies")
def companies_group():
    """Manage company catalog and ATS detection (Phase 4)."""
    pass


@companies_group.command("seed")
def companies_seed_cmd():
    """Load or sync curated seed companies from data/config/companies.yaml."""
    from resume_agent.jobs.companies import seed_companies_from_yaml, get_companies_list

    settings = get_settings()
    setup_logging(settings.log_level)

    console.print(Panel.fit(
        "[bold cyan]Seeding Company Catalog[/bold cyan]\n"
        "Loading targets from [yellow]data/config/companies.yaml[/yellow]",
        title="Company Seed"
    ))

    count = seed_companies_from_yaml()
    resolved = len(get_companies_list(status="resolved"))
    unknown = len(get_companies_list(status="unknown"))

    print_success(f"Seeded {count} companies ({resolved} pre-resolved ATS, {unknown} pending detection).")


@companies_group.command("detect")
@click.option("--limit", default=10, type=int, help="Maximum number of unresolved companies to probe")
@click.option("--tier", default=None, type=int, help="Filter probe to specific tier (1 or 2)")
def companies_detect_cmd(limit: int, tier: int | None):
    """Run automated career portal probe and ATS signature detection."""
    from resume_agent.jobs.companies import get_unresolved_companies, update_company_ats, mark_company_unknown
    from resume_agent.jobs.discovery.detector import detect_ats

    settings = get_settings()
    setup_logging(settings.log_level)

    targets = get_unresolved_companies(limit=limit, tier=tier)
    if not targets:
        print_info("No unresolved companies found matching criteria.")
        return

    console.print(f"[bold cyan]Probing {len(targets)} company career portals for ATS signatures...[/bold cyan]\n")

    resolved_count = 0
    with console.status("[bold green]Probing career portals...[/bold green]"):
        for c in targets:
            console.print(f"Probing [bold]{c.name}[/bold] ([dim]{c.domain}[/dim])...", end=" ")
            res = detect_ats(c.domain)
            if res:
                provider, slug = res
                update_company_ats(c.id, provider, slug, status="resolved")
                console.print(f"[bold green]✔ DETECTED {provider.upper()} ({slug})[/bold green]")
                resolved_count += 1
            else:
                mark_company_unknown(c.id)
                console.print("[yellow]✖ Not resolved[/yellow]")

    print_success(f"Detection run finished: {resolved_count}/{len(targets)} newly resolved.")


@companies_group.command("list")
@click.option("--status", default=None, type=click.Choice(["resolved", "unknown", "dead"]), help="Filter by detection status")
@click.option("--tier", default=None, type=int, help="Filter by tier (1 or 2)")
def companies_list_cmd(status: str | None, tier: int | None):
    """List companies in the catalog with ATS provider and slug status."""
    from resume_agent.jobs.companies import get_companies_list

    settings = get_settings()
    setup_logging(settings.log_level)

    companies = get_companies_list(status=status, tier=tier)
    if not companies:
        print_info("No companies found. Run 'resume-agent companies seed' first.")
        return

    table = Table(title="Company Catalog & ATS Endpoints", border_style="cyan")
    table.add_column("Tier", justify="center", style="bold")
    table.add_column("Company Name", style="bold white")
    table.add_column("Domain", style="dim")
    table.add_column("ATS Provider", style="cyan")
    table.add_column("ATS Slug", style="green")
    table.add_column("Status", justify="center")

    for c in companies:
        tier_str = f"T{c.tier}"
        status_badge = (
            "[bold green]✔ Resolved[/bold green]" if c.detection_status == "resolved" else
            "[yellow]Pending[/yellow]"
        )
        table.add_row(
            tier_str,
            c.name,
            c.domain,
            c.ats_provider or "—",
            c.ats_slug or "—",
            status_badge,
        )

    console.print(table)


@companies_group.command("add")
@click.option("--name", required=True, help="Company name")
@click.option("--domain", required=True, help="Company website domain (e.g. stripe.com)")
@click.option("--tier", default=2, type=int, help="Priority tier (1, 2, or 3)")
@click.option("--provider", default=None, help="ATS provider (greenhouse, lever, ashby, workable)")
@click.option("--slug", default=None, help="ATS company slug")
def companies_add_cmd(name: str, domain: str, tier: int, provider: str | None, slug: str | None):
    """Manually add or update a target company."""
    from resume_agent.jobs.companies import add_custom_company

    settings = get_settings()
    setup_logging(settings.log_level)

    add_custom_company(name, domain, tier=tier, provider=provider, slug=slug)
    print_success(f"Company '{name}' ({domain}) added to catalog.")

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
