import base64
from typing import List, Dict, Any, Optional
import httpx
from resume_agent.config import get_settings
from resume_agent.logging import logger


class GitHubClient:
    """REST API Client for GitHub repository metadata and content fetching."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None):
        settings = get_settings()
        self.token = token or settings.github_token
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": f"ResumeAgent/{settings.github_username}",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    def get_user_repos(self, username: str) -> List[Dict[str, Any]]:
        """Fetch list of public repositories for a user."""
        url = f"{self.BASE_URL}/users/{username}/repos?per_page=100&sort=updated"
        try:
            with httpx.Client(headers=self.headers, timeout=15.0) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code == 403:
                    logger.warning("GitHub API rate limit exceeded or token missing.")
                    return []
                else:
                    logger.warning(f"GitHub API returned status {resp.status_code} for user {username}")
                    return []
        except Exception as e:
            logger.warning(f"Failed to connect to GitHub API: {e}")
            return []

    def get_repo_readme(self, owner: str, repo: str) -> str:
        """Fetch and decode the raw README content for a repository."""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/readme"
        try:
            with httpx.Client(headers=self.headers, timeout=15.0) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    content_b64 = data.get("content", "")
                    return base64.b64decode(content_b64).decode("utf-8", errors="replace")
                return ""
        except Exception as e:
            logger.warning(f"Could not fetch README for {owner}/{repo}: {e}")
            return ""

    def get_repo_languages(self, owner: str, repo: str) -> List[str]:
        """Fetch list of languages used in repository."""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/languages"
        try:
            with httpx.Client(headers=self.headers, timeout=15.0) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    return list(resp.json().keys())
                return []
        except Exception as e:
            logger.warning(f"Could not fetch languages for {owner}/{repo}: {e}")
            return []
