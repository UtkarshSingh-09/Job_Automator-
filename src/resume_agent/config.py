from functools import lru_cache
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


def _find_project_root() -> Path:
    # 1. Check current working directory
    cwd = Path.cwd()
    if (cwd / "migrations").exists() or (cwd / "templates").exists():
        return cwd
    # 2. Check /app (standard Docker container working directory)
    if Path("/app/migrations").exists() or Path("/app/templates").exists():
        return Path("/app")
    # 3. Fallback to package relative path
    return Path(__file__).resolve().parent.parent.parent


PROJECT_ROOT = _find_project_root()


class Settings(BaseSettings):
    """System configuration loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Project paths
    project_root: Path = PROJECT_ROOT
    data_dir: Path = Path("/app/data") if Path("/app/data").exists() else PROJECT_ROOT / "data"
    db_path: Path = Path("/app/data/agent.db") if Path("/app/data").exists() else PROJECT_ROOT / "data" / "agent.db"
    migrations_dir: Path = Path("/app/migrations") if Path("/app/migrations").exists() else PROJECT_ROOT / "migrations"
    output_dir: Path = Path("/app/data/output") if Path("/app/data").exists() else PROJECT_ROOT / "data" / "output"

    # API Keys & Tokens
    openrouter_api_key: Optional[str] = Field(default=None, alias="OPENROUTER_API_KEY")
    llm_model: str = Field(default="deepseek/deepseek-chat", alias="LLM_MODEL")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    github_token: Optional[str] = Field(default=None, alias="GITHUB_TOKEN")
    github_username: str = Field(default="UtkarshSingh-09", alias="GITHUB_USERNAME")
    telegram_bot_token: Optional[str] = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: Optional[str] = Field(default=None, alias="TELEGRAM_CHAT_ID")
    adzuna_app_id: Optional[str] = Field(default=None, alias="ADZUNA_APP_ID")
    adzuna_app_key: Optional[str] = Field(default=None, alias="ADZUNA_APP_KEY")

    # Guardrails & Limits
    max_daily_resumes: int = Field(default=15, alias="MAX_DAILY_RESUMES")
    max_daily_applies: int = Field(default=10, alias="MAX_DAILY_APPLIES")
    min_cooldown_seconds: int = Field(default=180, alias="MIN_COOLDOWN_SECONDS")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


@lru_cache()
def get_settings() -> Settings:
    """Return cached singleton settings instance."""
    return Settings()
