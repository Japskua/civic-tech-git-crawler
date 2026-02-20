import logging
from typing import Any

import httpx
from github import Auth, Github, GithubException, Repository

from civic_tech_crawler.utils.rate_limiter import RateLimiter
from civic_tech_crawler.utils.retry import retry_on_none

logger = logging.getLogger(__name__)


class GitHubClient:
    def __init__(
        self,
        token: str,
        max_retries: int = 5,
        retry_delay: float = 3.0,
        rate_limit_buffer: int = 100,
    ):
        self._github = Github(auth=Auth.Token(token), per_page=100)
        self._httpx = httpx.Client(
            base_url="https://api.github.com",
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30.0,
        )
        self._rate_limiter = RateLimiter(self._github, buffer=rate_limit_buffer)
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._user_cache: dict[str, dict] = {}

    def get_repo(self, slug: str) -> Repository.Repository:
        self._rate_limiter.wait_if_needed()
        return self._github.get_repo(slug)

    def get_stats_contributors(self, repo: Repository.Repository) -> Any:
        """Get contributor stats with 202-retry logic."""
        return retry_on_none(
            func=lambda: repo.get_stats_contributors(),
            max_retries=self._max_retries,
            base_delay=self._retry_delay,
            description=f"stats/contributors for {repo.full_name}",
        )

    def get_stats_commit_activity(self, repo: Repository.Repository) -> Any:
        """Get weekly commit activity with 202-retry logic."""
        return retry_on_none(
            func=lambda: repo.get_stats_commit_activity(),
            max_retries=self._max_retries,
            base_delay=self._retry_delay,
            description=f"stats/commit_activity for {repo.full_name}",
        )

    def get_community_profile(self, slug: str) -> dict:
        """GET /repos/{owner}/{repo}/community/profile via httpx."""
        self._rate_limiter.wait_if_needed()
        resp = self._httpx.get(f"/repos/{slug}/community/profile")
        if resp.status_code == 200:
            return resp.json()
        logger.warning("Community profile for %s returned %d", slug, resp.status_code)
        return {}

    def get_workflows(self, slug: str) -> list[dict]:
        """GET /repos/{owner}/{repo}/actions/workflows via httpx."""
        self._rate_limiter.wait_if_needed()
        resp = self._httpx.get(f"/repos/{slug}/actions/workflows")
        if resp.status_code == 200:
            return resp.json().get("workflows", [])
        logger.warning("Workflows for %s returned %d", slug, resp.status_code)
        return []

    def get_repo_contents_names(self, slug: str, path: str = "") -> list[str]:
        """List file/directory names at a path in the repo."""
        self._rate_limiter.wait_if_needed()
        resp = self._httpx.get(f"/repos/{slug}/contents/{path}")
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                return [item["name"] for item in data]
        return []

    def get_file_content(self, slug: str, path: str) -> str | None:
        """Get decoded file content from the repository."""
        self._rate_limiter.wait_if_needed()
        resp = self._httpx.get(f"/repos/{slug}/contents/{path}")
        if resp.status_code == 200:
            data = resp.json()
            if data.get("encoding") == "base64":
                import base64

                return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
            return data.get("content", "")
        return None

    def file_exists(self, slug: str, path: str) -> bool:
        """Check if a file exists in the repo (HEAD request)."""
        self._rate_limiter.wait_if_needed()
        resp = self._httpx.head(f"/repos/{slug}/contents/{path}")
        return resp.status_code == 200

    def get_user_info(self, login: str) -> dict:
        """Get user profile info with caching."""
        if login in self._user_cache:
            return self._user_cache[login]
        self._rate_limiter.wait_if_needed()
        try:
            user = self._github.get_user(login)
            info = {
                "login": user.login,
                "name": user.name,
                "company": user.company,
            }
        except GithubException:
            info = {"login": login, "name": None, "company": None}
        self._user_cache[login] = info
        return info

    @property
    def rate_limit_remaining(self) -> int:
        return self._rate_limiter.remaining

    def close(self) -> None:
        self._httpx.close()
        self._github.close()
