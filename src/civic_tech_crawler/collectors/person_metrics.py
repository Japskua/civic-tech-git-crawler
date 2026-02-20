import logging

from github import Repository

from civic_tech_crawler.client import GitHubClient
from civic_tech_crawler.models import PersonMetrics

logger = logging.getLogger(__name__)


def collect_person_metrics(
    client: GitHubClient,
    repo: Repository.Repository,
) -> list[PersonMetrics]:
    """Collect per-contributor metrics using stats/contributors endpoint."""
    slug = repo.full_name
    logger.info("Collecting person metrics for %s", slug)

    stats = client.get_stats_contributors(repo)
    if stats is None:
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
            )
        )

    logger.info("Collected metrics for %d contributors in %s", len(results), slug)
    return results
