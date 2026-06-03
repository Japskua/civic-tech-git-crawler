import logging
import re
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
    message: str = ""


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

    def warm_stats_endpoints(self, slugs: list[str], endpoints: tuple[str, ...] = ("commit_activity", "contributors")) -> dict[str, int]:
        """Fire one request per (slug, endpoint) to trigger GitHub's async stats build.

        GitHub computes /stats/* asynchronously: the first request returns 202 and
        starts the build, subsequent requests return 200 once it finishes. By
        firing all requests up-front, the per-repo builds proceed in parallel
        server-side while the crawler does its sequential work — so by the time
        we actually need a repo's stats during chaoss_metrics collection, GitHub
        has typically had several minutes to compute them.

        Sequential, no retries, no body parsing. ~0.3 s per request, so 37 repos
        × 2 endpoints ≈ 22 s of pre-pass. Returns a dict of HTTP status counts.
        """
        counts: dict[int, int] = {}
        logger.info("Warming stats endpoints for %d repos × %d endpoints...", len(slugs), len(endpoints))
        for slug in slugs:
            for endpoint in endpoints:
                self._rate_limiter.wait_if_needed()
                try:
                    resp = self._httpx.get(f"/repos/{slug}/stats/{endpoint}")
                    counts[resp.status_code] = counts.get(resp.status_code, 0) + 1
                except httpx.HTTPError:
                    counts[-1] = counts.get(-1, 0) + 1
        summary = ", ".join(f"{k}: {v}" for k, v in sorted(counts.items()))
        logger.info("Stats warm-up complete: %s", summary)
        return counts

    def _get_stats_endpoint(self, slug: str, endpoint: str) -> list | None:
        """Fetch a /stats/{endpoint} JSON payload with iterative 202-retry.

        GitHub returns 202 while computing stats and the computation is async,
        so the first request typically *triggers* the build rather than
        returning data. For active repositories the build can take 30–180 s.
        We retry with exponential backoff capped at 30 s per attempt, using a
        budget of at least 10 attempts (≈ 225 s total at default retry_delay
        = 3 s) regardless of the user-configured max_retries — that knob
        governs general HTTP retry, not the longer stats build wait.

        Returns the parsed JSON list, or None if the endpoint never finished
        computing or returned an error.
        """
        # Earlier versions used `delay = retry_delay * attempt` with the
        # general max_retries (=5 by default), giving a 45 s budget that was
        # too short on the May 2026 crawl: GitHub returned 202 for ≥45 s on
        # 32 of 37 repos, so weekly_commits was cached as [] and burstiness
        # could not be computed. The longer budget here restores the March
        # 2026 baseline coverage (29/29 populated).
        url = f"/repos/{slug}/stats/{endpoint}"
        attempts = max(self._max_retries, 10)
        max_backoff = 30.0
        for attempt in range(1, attempts + 1):
            self._rate_limiter.wait_if_needed()
            try:
                resp = self._httpx.get(url)
            except httpx.HTTPError as e:
                logger.warning("stats/%s for %s transport error: %s", endpoint, slug, e)
                return None
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 202:
                delay = min(self._retry_delay * (2 ** (attempt - 1)), max_backoff)
                logger.info(
                    "stats/%s for %s computing (attempt %d/%d), waiting %.1fs...",
                    endpoint, slug, attempt, attempts, delay,
                )
                time.sleep(delay)
                continue
            logger.warning(
                "stats/%s for %s returned HTTP %d", endpoint, slug, resp.status_code
            )
            return None
        logger.warning("stats/%s for %s still 202 after %d attempts", endpoint, slug, attempts)
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

    def _request_with_retry(
        self, method: str, url: str, params: dict | None = None, max_retries: int = 3
    ) -> httpx.Response | None:
        """Issue an httpx request, retrying transient failures with backoff.

        Mirrors the retry policy of ``execute_graphql``: retries on transport
        errors and HTTP 429/500/502/503/504. Returns the response (which may be
        a non-transient non-200 such as 404 — callers decide), or None if all
        attempts fail. Without this, a transient blip during the detection scan
        silently became a false-negative ("not detected").
        """
        for attempt in range(1, max_retries + 1):
            self._rate_limiter.wait_if_needed()
            try:
                resp = self._httpx.request(method, url, params=params)
            except httpx.HTTPError as e:
                if attempt < max_retries:
                    delay = min(2 ** (attempt - 1) * self._retry_delay, 30.0)
                    logger.warning(
                        "%s %s transport error (attempt %d/%d): %s — retrying in %.1fs",
                        method, url, attempt, max_retries, e, delay,
                    )
                    time.sleep(delay)
                    continue
                logger.warning("%s %s transport error after %d attempts: %s", method, url, attempt, e)
                return None
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < max_retries:
                delay = min(2 ** (attempt - 1) * self._retry_delay, 30.0)
                logger.warning(
                    "%s %s HTTP %d (attempt %d/%d) — retrying in %.1fs",
                    method, url, resp.status_code, attempt, max_retries, delay,
                )
                time.sleep(delay)
                continue
            return resp
        return None

    def get_repo_contents_names(self, slug: str, path: str = "") -> list[str]:
        """List file/directory names at a path in the repo."""
        resp = self._request_with_retry("GET", f"/repos/{slug}/contents/{path}")
        if resp is not None and resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                return [item["name"] for item in data]
        return []

    def get_file_content(self, slug: str, path: str) -> str | None:
        """Get decoded file content from the repository."""
        resp = self._request_with_retry("GET", f"/repos/{slug}/contents/{path}")
        if resp is not None and resp.status_code == 200:
            data = resp.json()
            if data.get("encoding") == "base64":
                import base64

                return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
            return data.get("content", "")
        return None

    def file_exists(self, slug: str, path: str) -> bool:
        """Check if a file exists in the repo (HEAD request)."""
        resp = self._request_with_retry("HEAD", f"/repos/{slug}/contents/{path}")
        return resp is not None and resp.status_code == 200

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
        resp = self._request_with_retry(
            "GET", f"/repos/{slug}/commits", params={"path": path, "per_page": 1}
        )
        if resp is not None and resp.status_code == 200:
            data = resp.json()
            if data and len(data) > 0:
                return data[0].get("commit", {}).get("author", {}).get("date")
        return None

    def get_first_commit_date_for_path(self, slug: str, path: str) -> str | None:
        """Get ISO date string of the *oldest* commit touching a file path.

        Commits come back newest-first, so the oldest commit is on the last
        page. We fetch one commit per page and follow the ``Link: rel="last"``
        header to jump straight to it — used to date when a file (e.g.
        ``CLAUDE.md``) was first introduced.
        """
        resp = self._request_with_retry(
            "GET", f"/repos/{slug}/commits", params={"path": path, "per_page": 1}
        )
        if resp is None or resp.status_code != 200:
            return None
        data = resp.json()
        if not data:
            return None

        link = resp.headers.get("Link", "")
        has_more_pages = 'rel="next"' in link or 'rel="last"' in link
        if not has_more_pages:
            # Single page: the only commit is also the oldest one.
            return data[0].get("commit", {}).get("author", {}).get("date")

        # Multiple pages exist; the oldest commit is on the last page. If we
        # can't resolve and fetch that page, return None rather than the
        # page-1 (newest) commit, which would be a wrong "first seen" date.
        last_page = self._parse_last_page(link)
        if not last_page or last_page <= 1:
            return None
        resp = self._request_with_retry(
            "GET",
            f"/repos/{slug}/commits",
            params={"path": path, "per_page": 1, "page": last_page},
        )
        if resp is None or resp.status_code != 200:
            return None
        data = resp.json()
        if not data:
            return None
        return data[0].get("commit", {}).get("author", {}).get("date")

    @staticmethod
    def _parse_last_page(link_header: str) -> int | None:
        """Extract the page number of the rel="last" URL from a Link header."""
        for part in link_header.split(","):
            if 'rel="last"' in part:
                match = re.search(r"[?&]page=(\d+)", part)
                if match:
                    return int(match.group(1))
        return None

    def iter_recent_prs_with_meta(
        self, slug: str, limit: int = 200
    ) -> list[dict]:
        """Return up to *limit* most-recent PRs with author, body and the logins
        of their comment/review authors — for AI body-marker and review-bot
        detection. One GraphQL call per 50 PRs.

        Each dict: ``{number, created_at, author, body, participant_logins}``.
        """
        try:
            owner, name = slug.split("/", 1)
        except ValueError:
            return []

        query = """
        query ($owner: String!, $name: String!, $cursor: String) {
          repository(owner: $owner, name: $name) {
            pullRequests(first: 50, after: $cursor,
                         orderBy: {field: CREATED_AT, direction: DESC}) {
              pageInfo { hasNextPage endCursor }
              nodes {
                number
                createdAt
                author { login }
                bodyText
                comments(first: 20) { nodes { author { login } } }
                reviews(first: 20) { nodes { author { login } } }
              }
            }
          }
        }
        """
        results: list[dict] = []
        cursor: str | None = None
        truncated = False
        while len(results) < limit:
            data = self.execute_graphql(
                query, {"owner": owner, "name": name, "cursor": cursor}
            )
            if data is None:
                break
            repo_data = data.get("repository") or {}
            prs = repo_data.get("pullRequests") or {}
            nodes = prs.get("nodes") or []
            page_info = prs.get("pageInfo") or {}
            hit_limit = False
            for idx, node in enumerate(nodes):
                if not node:
                    continue
                participants: list[str] = []
                for section in ("comments", "reviews"):
                    for sub in ((node.get(section) or {}).get("nodes") or []):
                        login = ((sub or {}).get("author") or {}).get("login")
                        if login:
                            participants.append(login)
                results.append(
                    {
                        "number": node.get("number"),
                        "created_at": node.get("createdAt"),
                        "author": ((node.get("author") or {}).get("login")),
                        "body": node.get("bodyText") or "",
                        "participant_logins": participants,
                    }
                )
                if len(results) >= limit:
                    # More PRs exist if there are unprocessed nodes in this page
                    # or further pages — i.e. we are leaving data unscanned.
                    truncated = idx < len(nodes) - 1 or bool(page_info.get("hasNextPage"))
                    hit_limit = True
                    break
            if hit_limit:
                break
            if not page_info.get("hasNextPage"):
                break
            cursor = page_info.get("endCursor")
            if not cursor:
                break
        if truncated:
            logger.info(
                "PR meta scan for %s capped at %d most-recent PRs — older PR "
                "bodies / review-bot comments are not scanned",
                slug, limit,
            )
        return results

    def execute_graphql(
        self,
        query: str,
        variables: dict | None = None,
        max_retries: int = 5,
    ) -> dict | None:
        """Execute a GraphQL query. Returns the 'data' payload or None on error.

        Retries up to max_retries times on transient HTTP errors (502/503/504
        Gateway Timeout / Service Unavailable, and 429 rate-limit). Earlier
        versions returned None on the first transient error, which silently
        truncated commit-history iterators when GitHub's GraphQL gateway had
        a brief blip — the iter_commits_graphql caller stops on None.
        """
        self._rate_limiter.wait_if_needed()
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        for attempt in range(1, max_retries + 1):
            try:
                resp = self._httpx.post("/graphql", json=payload)
            except httpx.HTTPError as e:
                if attempt < max_retries:
                    delay = min(2 ** (attempt - 1) * self._retry_delay, 30.0)
                    logger.warning(
                        "GraphQL transport error (attempt %d/%d): %s — retrying in %.1fs",
                        attempt, max_retries, e, delay,
                    )
                    time.sleep(delay)
                    continue
                logger.warning("GraphQL transport error after %d attempts: %s", attempt, e)
                return None

            if resp.status_code == 200:
                body = resp.json()
                if body.get("errors"):
                    logger.warning("GraphQL errors: %s", body["errors"])
                return body.get("data")

            if resp.status_code in (429, 502, 503, 504) and attempt < max_retries:
                delay = min(2 ** (attempt - 1) * self._retry_delay, 30.0)
                logger.warning(
                    "GraphQL HTTP %d (attempt %d/%d): %s — retrying in %.1fs",
                    resp.status_code, attempt, max_retries, resp.text[:200], delay,
                )
                time.sleep(delay)
                continue

            logger.warning(
                "GraphQL returned HTTP %d: %s", resp.status_code, resp.text[:200]
            )
            return None

        return None

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
                      message
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
                    message=node.get("message") or "",
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
