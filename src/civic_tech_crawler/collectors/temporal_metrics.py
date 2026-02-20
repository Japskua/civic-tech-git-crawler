import logging

from github import GithubException, Repository

from civic_tech_crawler.client import GitHubClient
from civic_tech_crawler.models import PRRecord, ReleaseRecord, TagRecord, TemporalMetrics

logger = logging.getLogger(__name__)


def collect_temporal_metrics(
    client: GitHubClient,
    repo: Repository.Repository,
) -> TemporalMetrics:
    """Collect PRs, tags, and releases with timestamps."""
    slug = repo.full_name
    logger.info("Collecting temporal metrics for %s", slug)

    # Pull Requests
    prs: list[PRRecord] = []
    pr_merged = 0
    pr_open = 0
    pr_closed_unmerged = 0
    try:
        for pr in repo.get_pulls(state="all", sort="created", direction="asc"):
            author_login = pr.user.login if pr.user else None
            prs.append(
                PRRecord(
                    number=pr.number,
                    title=pr.title,
                    state=pr.state,
                    author_login=author_login,
                    created_at=pr.created_at,
                    merged_at=pr.merged_at,
                    closed_at=pr.closed_at,
                )
            )
            if pr.merged_at is not None:
                pr_merged += 1
            elif pr.state == "open":
                pr_open += 1
            else:
                pr_closed_unmerged += 1
    except GithubException as e:
        logger.warning("Could not fetch PRs for %s: %s", slug, e)

    # Tags
    tags: list[TagRecord] = []
    try:
        for tag in repo.get_tags():
            tag_date = None
            try:
                tag_date = tag.commit.commit.author.date
            except (GithubException, AttributeError):
                pass
            tags.append(
                TagRecord(
                    name=tag.name,
                    commit_sha=tag.commit.sha,
                    date=tag_date,
                )
            )
    except GithubException as e:
        logger.warning("Could not fetch tags for %s: %s", slug, e)

    # Releases
    releases: list[ReleaseRecord] = []
    try:
        for release in repo.get_releases():
            releases.append(
                ReleaseRecord(
                    tag_name=release.tag_name,
                    name=release.title,
                    created_at=release.created_at,
                    is_prerelease=release.prerelease,
                )
            )
    except GithubException as e:
        logger.warning("Could not fetch releases for %s: %s", slug, e)

    return TemporalMetrics(
        repo_full_name=slug,
        pr_count_total=len(prs),
        pr_count_merged=pr_merged,
        pr_count_open=pr_open,
        pr_count_closed_unmerged=pr_closed_unmerged,
        prs=prs,
        tag_count=len(tags),
        tags=tags,
        release_count=len(releases),
        releases=releases,
    )
