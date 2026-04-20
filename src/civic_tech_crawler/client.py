import logging
import time
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx
from github import Auth, Github, GithubException, Repository

from civic_tech_crawler.utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


# Lightweight replacements for PyGithub's StatsContributor / StatsCommitActivity.
# PyGithub's Requester recursively retries HTTP 202 responses (Requester.py:1238),
# which causes RecursionError on stats endpoints that take minutes to compute
# (observed on DemocracyClub/UK-Polling-Stations, WhoCanIVoteFor).
@dataclass(frozen=True, slots=True)
class StatsWeek:
    w: int   # unix timestamp (seconds)
    a: int   # additions
    d: int   # deletions
    c: int   # commits


@dataclass(frozen=True, slots=True)
class StatsAuthor:
    login: str | None


@dataclass(frozen=True, slots=True)
class StatsContributorRecord:
    author: StatsAuthor | None
    total: int
    weeks: list[StatsWeek]


@dataclass(frozen=True, slots=True)
class StatsCommitActivityRecord:
    week: int           # unix timestamp (seconds) of the week start (Sunday)
    total: int
    days: list[int]


@dataclass(frozen=True, slots=True)
class CommitRecord:
    """Commit data fetched in bulk via GraphQL (100 commits per API call).

    Replaces the REST per-commit-stats pattern that costs N API calls for N
    commits. For a repo with 8k commits: 80 GraphQL calls instead of 8000.
    """
    sha: str
    additions: int
    deletions: int
    committed_date: datetime
    author_email: str
    author_name: str
    author_login: str | None


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

    def _get_stats_endpoint(self, slug: str, endpoint: str) -> list | None:
        """Fetch a /stats/{endpoint} JSON payload with iterative 202-retry.

        GitHub returns 202 while computing stats. We retry with linear backoff
        (3s, 6s, 9s, ...). Returns the parsed JSON list, or None if the endpoint
        never finished computing or returned an error.
        """
        url = f"/repos/{slug}/stats/{endpoint}"
        for attempt in range(1, self._max_retries + 1):
            self._rate_limiter.wait_if_needed()
            try:
                resp = self._httpx.get(url)
            except httpx.HTTPError as e:
                logger.warning("stats/%s for %s transport error: %s", endpoint, slug, e)
                return None
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 202:
                delay = self._retry_delay * attempt
                logger.info(
                    "stats/%s for %s computing (attempt %d/%d), waiting %.1fs...",
                    endpoint, slug, attempt, self._max_retries, delay,
                )
                time.sleep(delay)
                continue
            logger.warning(
                "stats/%s for %s returned HTTP %d", endpoint, slug, resp.status_code
            )
            return None
        logger.warning("stats/%s for %s still 202 after %d attempts", endpoint, slug, self._max_retries)
        return None

    def get_stats_contributors(
        self, repo: Repository.Repository
    ) -> list[StatsContributorRecord] | None:
        """Get contributor stats via httpx with iterative 202-retry.

        Bypasses PyGithub's get_stats_contributors, which recursively retries
        202 responses and hits RecursionError on large repos.
        """
        data = self._get_stats_endpoint(repo.full_name, "contributors")
        if not data:
            return None
        return [
            StatsContributorRecord(
                author=(
                    StatsAuthor(login=(c.get("author") or {}).get("login"))
                    if c.get("author") is not None
                    else None
                ),
                total=int(c.get("total", 0)),
                weeks=[
                    StatsWeek(
                        w=int(w.get("w", 0)),
                        a=int(w.get("a", 0)),
                        d=int(w.get("d", 0)),
                        c=int(w.get("c", 0)),
                    )
                    for w in (c.get("weeks") or [])
                ],
            )
            for c in data
        ]

    def get_stats_commit_activity(
        self, repo: Repository.Repository
    ) -> list[StatsCommitActivityRecord] | None:
        """Get weekly commit activity via httpx with iterative 202-retry."""
        data = self._get_stats_endpoint(repo.full_name, "commit_activity")
        if not data:
            return None
        return [
            StatsCommitActivityRecord(
                week=int(item.get("week", 0)),
                total=int(item.get("total", 0)),
                days=list(item.get("days") or []),
            )
            for item in data
        ]

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
                "bio": user.bio,
                "email": user.email,
            }
        except GithubException:
            info = {"login": login, "name": None, "company": None, "bio": None, "email": None}
        self._user_cache[login] = info
        return info

    def get_user_orgs(self, login: str) -> list[str]:
        """Get public organization memberships for a user.

        Uses: GET /users/{login}/orgs
        Returns list of org login names.
        """
        self._rate_limiter.wait_if_needed()
        resp = self._httpx.get(f"/users/{login}/orgs")
        if resp.status_code == 200:
            return [org.get("login", "") for org in resp.json()]
        return []

    def get_commit_stats(self, slug: str, sha: str) -> tuple[int, int] | None:
        """Return (additions, deletions) for a single commit via httpx.

        Bypasses PyGithub's lazy-load on Commit.stats, which has been observed
        to trigger RecursionError on large repos (see feature/weekly-line-changes).
        """
        self._rate_limiter.wait_if_needed()
        try:
            resp = self._httpx.get(f"/repos/{slug}/commits/{sha}")
        except httpx.HTTPError as e:
            logger.debug("get_commit_stats %s/%s transport error: %s", slug, sha, e)
            return None
        if resp.status_code != 200:
            return None
        stats = resp.json().get("stats") or {}
        return int(stats.get("additions", 0)), int(stats.get("deletions", 0))

    def get_last_commit_date_for_path(self, slug: str, path: str) -> str | None:
        """Get ISO date string of the most recent commit touching a file path.

        Uses: GET /repos/{owner}/{repo}/commits?path={path}&per_page=1
        """
        self._rate_limiter.wait_if_needed()
        resp = self._httpx.get(
            f"/repos/{slug}/commits",
            params={"path": path, "per_page": 1},
        )
        if resp.status_code == 200:
            data = resp.json()
            if data and len(data) > 0:
                return data[0].get("commit", {}).get("author", {}).get("date")
        return None

    def execute_graphql(
        self,
        query: str,
        variables: dict | None = None,
    ) -> dict | None:
        """Execute a GraphQL query. Returns the 'data' payload or None on error."""
        self._rate_limiter.wait_if_needed()
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables
        try:
            resp = self._httpx.post("/graphql", json=payload)
        except httpx.HTTPError as e:
            logger.warning("GraphQL transport error: %s", e)
            return None
        if resp.status_code != 200:
            logger.warning(
                "GraphQL returned HTTP %d: %s", resp.status_code, resp.text[:200]
            )
            return None
        body = resp.json()
        if body.get("errors"):
            logger.warning("GraphQL errors: %s", body["errors"])
        return body.get("data")

    def iter_commits_graphql(self, slug: str) -> Iterator[CommitRecord]:
        """Yield every commit on the default branch via GraphQL, 100 per API call.

        Each CommitRecord includes additions/deletions/committedDate/author, so
        callers don't need the per-commit REST stats call. For a repo with N
        commits this costs ceil(N/100) API calls instead of N.
        """
        try:
            owner, name = slug.split("/", 1)
        except ValueError:
            logger.warning("Invalid slug %r", slug)
            return

        query = """
        query ($owner: String!, $name: String!, $cursor: String) {
          repository(owner: $owner, name: $name) {
            defaultBranchRef {
              target {
                ... on Commit {
                  history(first: 100, after: $cursor) {
                    pageInfo { hasNextPage endCursor }
                    nodes {
                      oid
                      additions
                      deletions
                      committedDate
                      author {
                        email
                        name
                        user { login }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """
        cursor: str | None = None
        while True:
            data = self.execute_graphql(
                query, {"owner": owner, "name": name, "cursor": cursor}
            )
            if data is None:
                return
            repo_data = data.get("repository")
            if not repo_data:
                return
            branch = repo_data.get("defaultBranchRef")
            if not branch:
                return
            target = (branch or {}).get("target") or {}
            history = target.get("history")
            if not history:
                return
            for node in history.get("nodes") or []:
                if not node:
                    continue
                sha = node.get("oid")
                if not sha:
                    continue
                committed_raw = node.get("committedDate")
                try:
                    committed_date = datetime.fromisoformat(
                        committed_raw.replace("Z", "+00:00")
                    ) if committed_raw else None
                except (AttributeError, ValueError):
                    committed_date = None
                if committed_date is None:
                    continue
                author = node.get("author") or {}
                user = author.get("user") or {}
                yield CommitRecord(
                    sha=sha,
                    additions=int(node.get("additions") or 0),
                    deletions=int(node.get("deletions") or 0),
                    committed_date=committed_date,
                    author_email=author.get("email") or "unknown",
                    author_name=author.get("name") or "",
                    author_login=user.get("login"),
                )
            page_info = history.get("pageInfo") or {}
            if not page_info.get("hasNextPage"):
                return
            cursor = page_info.get("endCursor")
            if not cursor:
                return

    @property
    def rate_limit_remaining(self) -> int:
        return self._rate_limiter.remaining

    def close(self) -> None:
        self._httpx.close()
        self._github.close()
