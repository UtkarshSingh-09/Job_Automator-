import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

from resume_agent.config import get_settings
from resume_agent.db import get_db
from resume_agent.models import ProjectModel
from resume_agent.github.client import GitHubClient
from resume_agent.github.scorer import compute_quality_score
from resume_agent.logging import logger


def load_overrides() -> List[Dict[str, Any]]:
    """Load curated project manual notes and priorities from projects_override.yaml."""
    settings = get_settings()
    override_path = settings.data_dir / "config" / "projects_override.yaml"
    if not override_path.exists():
        logger.warning(f"Projects override file missing at {override_path}")
        return []

    with open(override_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data.get("projects", []) if isinstance(data, dict) else []


def load_local_readme_content(repo_name: str) -> str:
    """Find any matching local README file in project root if present."""
    settings = get_settings()
    root = settings.project_root
    
    # Map repo names to known local README files if any
    repo_lower = repo_name.lower().replace("-", "").replace("_", "")
    for file in root.glob("README*.md"):
        try:
            content = file.read_text(encoding="utf-8", errors="replace")
            content_lower = content.lower()
            if repo_lower in content_lower:
                return content
        except Exception:
            continue
    return ""


def sync_projects(username: Optional[str] = None, offline: bool = False) -> List[ProjectModel]:
    """
    Synchronize project corpus from overrides, local docs, and optionally GitHub API.
    Upserts each project into SQLite projects table with deterministic quality score.
    """
    settings = get_settings()
    user = username or settings.github_username
    overrides = load_overrides()

    client = None
    if not offline:
        client = GitHubClient()

    saved_projects: List[ProjectModel] = []

    # Map overrides by normalized repo name
    overrides_map = {p["repo_name"].lower(): p for p in overrides}

    # Fetch live repos from GitHub if online
    remote_repos: List[Dict[str, Any]] = []
    if client and not offline:
        logger.info(f"Checking GitHub API for user '{user}'...")
        remote_repos = client.get_user_repos(user)

    remote_map = {r["name"].lower(): r for r in remote_repos}

    # Combine all known repos (overrides take precedence for grounding notes)
    all_repo_names = list(overrides_map.keys())
    for r_name in remote_map:
        if r_name not in all_repo_names:
            all_repo_names.append(r_name)

    for r_name in all_repo_names:
        override = overrides_map.get(r_name, {})
        remote = remote_map.get(r_name, {})

        display_name = override.get("display_name") or remote.get("name") or r_name.title()
        description = override.get("description") or remote.get("description") or ""
        manual_notes = override.get("manual_notes") or ""
        primary_lang = override.get("primary_language") or remote.get("language") or "Python"
        languages = override.get("languages", [primary_lang] if primary_lang else [])
        topics = override.get("topics") or remote.get("topics") or []
        stars = remote.get("stargazers_count") or override.get("stars", 0)
        priority = override.get("priority", 10)
        has_tests = override.get("has_tests", True)
        has_ci = override.get("has_ci", False)
        has_docker = override.get("has_docker", True)
        commit_count = override.get("commit_count", 20)

        # Get README content (local files first, then remote GitHub, then description)
        readme_md = load_local_readme_content(r_name)
        if not readme_md and client and remote:
            owner = remote.get("owner", {}).get("login", user)
            readme_md = client.get_repo_readme(owner, remote["name"])
        if not readme_md:
            readme_md = f"# {display_name}\n\n{description}\n\n{manual_notes}"

        # Compute deterministic quality score
        score_data = {
            "readme_md": readme_md,
            "commit_count": commit_count,
            "has_tests": has_tests,
            "has_ci": has_ci,
            "has_docker": has_docker,
            "languages": languages,
            "primary_language": primary_lang,
            "stars": stars,
            "pushed_at": remote.get("pushed_at"),
        }
        quality_score = compute_quality_score(score_data)

        project = ProjectModel(
            repo_name=r_name,
            display_name=display_name,
            description=description,
            readme_md=readme_md,
            manual_notes=manual_notes,
            languages=languages,
            primary_language=primary_lang,
            topics=topics,
            stars=stars,
            commit_count=commit_count,
            has_tests=has_tests,
            has_ci=has_ci,
            has_docker=has_docker,
            quality_score=quality_score,
            include_override=override.get("include_override", False),
            priority=priority,
        )

        # Upsert into SQLite
        _upsert_project_to_db(project)
        saved_projects.append(project)

    logger.info(f"Successfully synced {len(saved_projects)} project(s) to database.")
    return saved_projects


def _upsert_project_to_db(p: ProjectModel) -> None:
    """Upsert project record into SQLite database."""
    sql = """
    INSERT INTO projects (
        repo_name, display_name, description, readme_md, manual_notes,
        languages_json, primary_language, topics_json, stars, commit_count,
        has_tests, has_ci, has_docker, quality_score, include_override, priority,
        synced_at
    ) VALUES (
        :repo_name, :display_name, :description, :readme_md, :manual_notes,
        :languages_json, :primary_language, :topics_json, :stars, :commit_count,
        :has_tests, :has_ci, :has_docker, :quality_score, :include_override, :priority,
        CURRENT_TIMESTAMP
    )
    ON CONFLICT(repo_name) DO UPDATE SET
        display_name = excluded.display_name,
        description = excluded.description,
        readme_md = excluded.readme_md,
        manual_notes = excluded.manual_notes,
        languages_json = excluded.languages_json,
        primary_language = excluded.primary_language,
        topics_json = excluded.topics_json,
        stars = excluded.stars,
        commit_count = excluded.commit_count,
        has_tests = excluded.has_tests,
        has_ci = excluded.has_ci,
        has_docker = excluded.has_docker,
        quality_score = excluded.quality_score,
        include_override = excluded.include_override,
        priority = excluded.priority,
        synced_at = CURRENT_TIMESTAMP;
    """
    params = {
        "repo_name": p.repo_name,
        "display_name": p.display_name,
        "description": p.description,
        "readme_md": p.readme_md,
        "manual_notes": p.manual_notes,
        "languages_json": json.dumps(p.languages),
        "primary_language": p.primary_language,
        "topics_json": json.dumps(p.topics),
        "stars": p.stars,
        "commit_count": p.commit_count,
        "has_tests": 1 if p.has_tests else 0,
        "has_ci": 1 if p.has_ci else 0,
        "has_docker": 1 if p.has_docker else 0,
        "quality_score": p.quality_score,
        "include_override": 1 if p.include_override else 0,
        "priority": p.priority,
    }
    with get_db() as conn:
        conn.execute(sql, params)


def get_all_projects(min_score: float = 0.0) -> List[ProjectModel]:
    """Retrieve all synced projects sorted by priority ascending (P1 first) and score descending."""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM projects 
            WHERE quality_score >= ? 
            ORDER BY priority ASC, quality_score DESC;
            """,
            (min_score,)
        )
        rows = cursor.fetchall()
        projects = []
        for r in rows:
            projects.append(ProjectModel(
                id=r["id"],
                repo_name=r["repo_name"],
                display_name=r["display_name"],
                description=r["description"],
                readme_md=r["readme_md"],
                manual_notes=r["manual_notes"],
                languages=json.loads(r["languages_json"] or "[]"),
                primary_language=r["primary_language"],
                topics=json.loads(r["topics_json"] or "[]"),
                stars=r["stars"],
                commit_count=r["commit_count"],
                has_tests=bool(r["has_tests"]),
                has_ci=bool(r["has_ci"]),
                has_docker=bool(r["has_docker"]),
                quality_score=r["quality_score"],
                include_override=bool(r["include_override"]),
                priority=r["priority"],
                embedding=r["embedding"],
                embedding_source_hash=r["embedding_source_hash"],
            ))
        return projects


def get_project_by_repo(repo_name: str) -> Optional[ProjectModel]:
    """Retrieve a single project by repository name."""
    with get_db() as conn:
        r = conn.execute(
            "SELECT * FROM projects WHERE repo_name = ? OR LOWER(display_name) = ?;",
            (repo_name.lower(), repo_name.lower())
        ).fetchone()
        if not r:
            return None
        return ProjectModel(
            id=r["id"],
            repo_name=r["repo_name"],
            display_name=r["display_name"],
            description=r["description"],
            readme_md=r["readme_md"],
            manual_notes=r["manual_notes"],
            languages=json.loads(r["languages_json"] or "[]"),
            primary_language=r["primary_language"],
            topics=json.loads(r["topics_json"] or "[]"),
            stars=r["stars"],
            commit_count=r["commit_count"],
            has_tests=bool(r["has_tests"]),
            has_ci=bool(r["has_ci"]),
            has_docker=bool(r["has_docker"]),
            quality_score=r["quality_score"],
            include_override=bool(r["include_override"]),
            priority=r["priority"],
            embedding=r["embedding"],
            embedding_source_hash=r["embedding_source_hash"],
        )
