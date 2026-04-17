from __future__ import annotations

import logging
import re

from github import GithubException, Repository

from civic_tech_crawler.client import GitHubClient
from civic_tech_crawler.models import PersonMetrics, RepoMetrics

logger = logging.getLogger(__name__)

# Maximum commits to iterate when falling back to the commits API
_FALLBACK_COMMIT_CAP = 500

# Bot detection patterns
_BOT_LOGIN_SUFFIX = re.compile(r"\[bot\]$", re.IGNORECASE)
_BOT_LOGIN_PATTERN = re.compile(
    r"(?:-bot$|-bot-|Bot$|^dependabot|^renovate|^greenkeeper|^snyk-bot"
    r"|^imgbot|^codecov|^stale|^allcontributors|^github-actions"
    r"|^pyup-bot|^transifex-integration|^weblate|^crowdin-bot"
    r"|^mergify|^semantic-release-bot|^release-drafter"
    r"|^pre-commit-ci|^netlify|^vercel|^railway-app"
    r"|^sonarcloud|^coveralls|^codeclimate)",
    re.IGNORECASE,
)


def is_bot_account(login: str | None) -> bool:
    """Detect whether a GitHub login belongs to a bot account."""
    if not login:
        return False
    if _BOT_LOGIN_SUFFIX.search(login):
        return True
    if _BOT_LOGIN_PATTERN.search(login):
        return True
    return False


def collect_person_metrics(
    client: GitHubClient,
    repo: Repository.Repository,
    repo_metrics: RepoMetrics | None = None,
) -> list[PersonMetrics]:
    """Collect per-contributor metrics using stats/contributors endpoint."""
    slug = repo.full_name
    logger.info("Collecting person metrics for %s", slug)

    stats = client.get_stats_contributors(repo)
    if stats is None or len(stats) == 0:
        total_commits = repo_metrics.total_commits if repo_metrics else 0
        if total_commits > 0:
            logger.info(
                "%s: stats/contributors empty, falling back to commits API", slug
            )
            return _fallback_person_metrics(client, repo, slug)
        logger.warning("Could not retrieve contributor stats for %s", slug)
        return []

    results: list[PersonMetrics] = []
    for contributor in stats:
        author = contributor.author
        login = author.login if author else None
        name = None
        if login:
            user_info = client.get_user_info(login)
            name = user_info.get("name")

        total_commits = contributor.total
        total_additions = sum(w.a for w in contributor.weeks)
        total_deletions = sum(w.d for w in contributor.weeks)

        avg_add = total_additions / total_commits if total_commits > 0 else 0.0
        avg_del = total_deletions / total_commits if total_commits > 0 else 0.0

        bot = is_bot_account(login)
        results.append(
            PersonMetrics(
                repo_full_name=slug,
                login=login,
                name=name,
                num_commits=total_commits,
                additions=total_additions,
                deletions=total_deletions,
                avg_additions_per_commit=round(avg_add, 2),
                avg_deletions_per_commit=round(avg_del, 2),
                is_bot=bot,
            )
        )

    bot_count = sum(1 for r in results if r.is_bot)
    logger.info(
        "Collected metrics for %d contributors in %s (%d bots detected)",
        len(results), slug, bot_count,
    )
    return results


def _fallback_person_metrics(
    client: GitHubClient,
    repo: Repository.Repository,
    slug: str,
) -> list[PersonMetrics]:
    """Build minimal person metrics from the commits API.

    Used when stats/contributors returns empty (e.g. all commit authors are
    anonymous / not linked to GitHub accounts).  Iterates up to
    _FALLBACK_COMMIT_CAP commits and groups by author email.
    """
    # email -> {name, login, commits, additions, deletions}
    authors: dict[str, dict] = {}

    try:
        commits = repo.get_commits()
        for i, commit in enumerate(commits):
            if i >= _FALLBACK_COMMIT_CAP:
                break
            git_commit = commit.commit
            email = git_commit.author.email or "unknown"
            name = git_commit.author.name

            # Use linked GitHub login if available
            login = commit.author.login if commit.author else None

            if email not in authors:
                authors[email] = {
                    "login": login,
                    "name": name,
                    "commits": 0,
                    "additions": 0,
                    "deletions": 0,
                }

            authors[email]["commits"] += 1
            # Use httpx-based stats to avoid PyGithub RecursionError on large repos
            stats = client.get_commit_stats(slug, commit.sha)
            if stats is not None:
                additions, deletions = stats
                authors[email]["additions"] += additions
                authors[email]["deletions"] += deletions
    except GithubException as e:
        logger.warning("Fallback commit iteration failed for %s: %s", slug, e)
        return []

    results: list[PersonMetrics] = []
    for email, data in authors.items():
        num = data["commits"]
        add = data["additions"]
        delete = data["deletions"]
        login = data["login"]
        results.append(
            PersonMetrics(
                repo_full_name=slug,
                login=login,
                name=data["name"],
                num_commits=num,
                additions=add,
                deletions=delete,
                avg_additions_per_commit=round(add / num, 2) if num > 0 else 0.0,
                avg_deletions_per_commit=round(delete / num, 2) if num > 0 else 0.0,
                is_bot=is_bot_account(login),
            )
        )

    logger.info(
        "%s: fallback found %d contributors from %d commits",
        slug,
        len(results),
        sum(d["commits"] for d in authors.values()),
    )
    return results
