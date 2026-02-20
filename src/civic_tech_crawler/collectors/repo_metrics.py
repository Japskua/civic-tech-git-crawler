import logging
from datetime import datetime, timezone

from github import GithubException, Repository

from civic_tech_crawler.client import GitHubClient
from civic_tech_crawler.models import RepoMetrics
from civic_tech_crawler.utils.osi_licenses import is_osi_approved

logger = logging.getLogger(__name__)


def collect_repo_metrics(
    client: GitHubClient,
    repo: Repository.Repository,
) -> RepoMetrics:
    """Collect repository-level metrics."""
    slug = repo.full_name
    logger.info("Collecting repo metrics for %s", slug)

    # Languages
    languages = repo.get_languages()

    # Contributors count
    try:
        num_developers = repo.get_contributors().totalCount
    except GithubException:
        logger.warning("Could not fetch contributors count for %s", slug)
        num_developers = 0

    # Commits: total count, first and last dates
    total_commits = 0
    first_commit_date: datetime | None = None
    last_commit_date: datetime | None = None
    try:
        commits = repo.get_commits()
        total_commits = commits.totalCount
        if total_commits > 0:
            last_commit = commits[0]
            last_commit_date = last_commit.commit.author.date
            # Get first commit by accessing the last page
            first_commit = commits.reversed[0]
            first_commit_date = first_commit.commit.author.date
    except GithubException as e:
        logger.warning("Could not fetch commits for %s: %s", slug, e)

    # License
    license_spdx: str | None = None
    license_name: str | None = None
    if repo.license:
        license_spdx = repo.license.spdx_id
        license_name = repo.license.name

    # Community profile (via httpx - not in PyGithub)
    community = client.get_community_profile(slug)
    community_files = community.get("files", {})
    has_contributing = community_files.get("contributing") is not None
    has_code_of_conduct = community_files.get("code_of_conduct") is not None
    has_readme = community_files.get("readme") is not None
    has_issue_template = community_files.get("issue_template") is not None
    has_pr_template = community_files.get("pull_request_template") is not None
    health_percentage = community.get("health_percentage", 0)

    # Governance file check
    has_governance = client.file_exists(slug, "GOVERNANCE.md") or client.file_exists(
        slug, "governance.md"
    )

    # CI/CD workflows
    workflows = client.get_workflows(slug)
    ci_cd_workflows = [w.get("name", "unknown") for w in workflows]
    has_ci_cd = len(ci_cd_workflows) > 0

    # Deployments
    try:
        deployments_count = repo.get_deployments().totalCount
    except GithubException:
        deployments_count = 0

    return RepoMetrics(
        full_name=repo.full_name,
        name=repo.name,
        description=repo.description,
        num_developers=num_developers,
        total_commits=total_commits,
        languages=dict(languages),
        primary_language=repo.language,
        first_commit_date=first_commit_date,
        last_commit_date=last_commit_date,
        license_spdx=license_spdx,
        license_name=license_name,
        is_osi_approved=is_osi_approved(license_spdx),
        topics=repo.get_topics(),
        has_contributing=has_contributing,
        has_code_of_conduct=has_code_of_conduct,
        has_governance=has_governance,
        has_readme=has_readme,
        has_issue_template=has_issue_template,
        has_pr_template=has_pr_template,
        health_percentage=health_percentage,
        stars=repo.stargazers_count,
        watchers=repo.subscribers_count,
        forks=repo.forks_count,
        cloud_detected=False,  # filled by detection collector
        cloud_signals=[],
        ai_ml_detected=False,
        ai_ml_signals=[],
        has_ci_cd=has_ci_cd,
        ci_cd_workflows=ci_cd_workflows,
        deployments_count=deployments_count,
        created_at=repo.created_at,
        updated_at=repo.updated_at,
        size_kb=repo.size,
    )
