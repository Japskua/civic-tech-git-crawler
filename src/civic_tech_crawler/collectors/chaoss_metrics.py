import logging
import math
from datetime import datetime, timezone

from github import GithubException, Repository

from civic_tech_crawler.client import GitHubClient
from civic_tech_crawler.models import ChaossMetrics, PersonMetrics, TemporalMetrics
from civic_tech_crawler.utils.osi_licenses import is_osi_approved

logger = logging.getLogger(__name__)

NEWCOMER_LABEL_PATTERNS = [
    "good first issue",
    "good-first-issue",
    "help wanted",
    "help-wanted",
    "beginner",
    "easy",
    "first-timers-only",
    "newcomer",
    "starter",
    "low-hanging-fruit",
    "up-for-grabs",
]


def _compute_bus_factor(person_metrics: list[PersonMetrics]) -> int | None:
    """Minimum number of contributors responsible for 50% of commits."""
    if not person_metrics:
        return None
    total = sum(p.num_commits for p in person_metrics)
    if total == 0:
        return None
    sorted_contribs = sorted(person_metrics, key=lambda p: p.num_commits, reverse=True)
    running_sum = 0
    for i, p in enumerate(sorted_contribs):
        running_sum += p.num_commits
        if running_sum >= total * 0.5:
            return i + 1
    return len(sorted_contribs)


def _compute_burstiness(weekly_commits: list[dict]) -> tuple[float | None, float | None, float | None]:
    """Compute mean, std, and coefficient of variation of weekly commit counts."""
    counts = [w["commits"] for w in weekly_commits]
    if not counts:
        return None, None, None
    mean = sum(counts) / len(counts)
    if mean == 0:
        return 0.0, 0.0, None
    variance = sum((c - mean) ** 2 for c in counts) / len(counts)
    std = math.sqrt(variance)
    cv = std / mean
    return round(mean, 2), round(std, 2), round(cv, 2)


def collect_chaoss_metrics(
    client: GitHubClient,
    repo: Repository.Repository,
    person_metrics: list[PersonMetrics],
    temporal_metrics: TemporalMetrics | None,
) -> ChaossMetrics:
    """Collect CHAOSS framework metrics."""
    slug = repo.full_name
    logger.info("Collecting CHAOSS metrics for %s", slug)

    # --- Code Changes Commits (weekly activity) ---
    weekly_commits: list[dict] = []
    commit_activity = client.get_stats_commit_activity(repo)
    if commit_activity:
        for week in commit_activity:
            # week.week is already a datetime in PyGithub
            week_start = week.week.isoformat() if isinstance(week.week, datetime) else datetime.fromtimestamp(week.week, tz=timezone.utc).isoformat()
            weekly_commits.append({
                "week_start": week_start,
                "commits": week.total,
            })

    # --- Change Request Acceptance Ratio ---
    acceptance_ratio: float | None = None
    if temporal_metrics and temporal_metrics.pr_count_total > 0:
        acceptance_ratio = round(
            temporal_metrics.pr_count_merged / temporal_metrics.pr_count_total, 4
        )

    # --- Bus Factor ---
    bus_factor = _compute_bus_factor(person_metrics)

    # --- Types of Contributions ---
    contribution_types: dict[str, int] = {
        "code_commits": sum(p.num_commits for p in person_metrics),
        "pull_requests": temporal_metrics.pr_count_total if temporal_metrics else 0,
    }
    # Issues (exclude PRs — GitHub counts PRs as issues)
    try:
        total_issues = repo.get_issues(state="all").totalCount
        total_prs = temporal_metrics.pr_count_total if temporal_metrics else 0
        contribution_types["issues"] = max(0, total_issues - total_prs)
    except GithubException:
        contribution_types["issues"] = 0

    # --- Organizational Diversity ---
    org_diversity: dict[str, int] = {}
    for p in person_metrics:
        if p.login:
            user_info = client.get_user_info(p.login)
            company = user_info.get("company") or "Unknown"
            company = company.strip().lstrip("@")
            org_diversity[company] = org_diversity.get(company, 0) + 1

    # --- Issue Label Inclusivity ---
    newcomer_labels: list[str] = []
    total_labels = 0
    try:
        labels = list(repo.get_labels())
        total_labels = len(labels)
        for label in labels:
            label_name = label.name.lower()
            if any(pattern in label_name for pattern in NEWCOMER_LABEL_PATTERNS):
                newcomer_labels.append(label.name)
    except GithubException:
        pass

    # --- Release Frequency ---
    release_freq: float | None = None
    if temporal_metrics and temporal_metrics.release_count >= 2:
        sorted_releases = sorted(temporal_metrics.releases, key=lambda r: r.created_at)
        first_release = sorted_releases[0].created_at
        last_release = sorted_releases[-1].created_at
        months_span = (last_release - first_release).days / 30.44
        if months_span > 0:
            release_freq = round(temporal_metrics.release_count / months_span, 2)

    # --- Technical Fork ---
    fork_count = repo.forks_count

    # --- Burstiness ---
    burst_mean, burst_std, burst_cv = _compute_burstiness(weekly_commits)

    # --- Defect Resolution Duration ---
    defect_durations: list[dict] = []
    try:
        # Try fetching issues with "bug" label
        bug_issues = repo.get_issues(state="closed", labels=["bug"])
        count = 0
        for issue in bug_issues:
            if issue.pull_request is not None:
                continue  # skip PRs
            if issue.closed_at and issue.created_at:
                days = (issue.closed_at - issue.created_at).total_seconds() / 86400
                defect_durations.append({
                    "issue_number": issue.number,
                    "days_to_close": round(days, 1),
                })
            count += 1
            if count >= 500:  # cap to avoid exhausting API
                break
    except GithubException:
        pass

    median_defect_days: float | None = None
    if defect_durations:
        sorted_days = sorted(d["days_to_close"] for d in defect_durations)
        n = len(sorted_days)
        if n % 2 == 0:
            median_defect_days = round((sorted_days[n // 2 - 1] + sorted_days[n // 2]) / 2, 1)
        else:
            median_defect_days = sorted_days[n // 2]

    # --- OSI Approved License ---
    license_spdx = repo.license.spdx_id if repo.license else None

    return ChaossMetrics(
        repo_full_name=slug,
        weekly_commits=weekly_commits,
        change_request_acceptance_ratio=acceptance_ratio,
        bus_factor=bus_factor,
        contribution_types=contribution_types,
        organizational_diversity=org_diversity,
        newcomer_friendly_labels=newcomer_labels,
        total_labels=total_labels,
        release_frequency_per_month=release_freq,
        fork_count=fork_count,
        burstiness_cv=burst_cv,
        burstiness_mean=burst_mean,
        burstiness_std=burst_std,
        defect_resolution_durations_days=defect_durations,
        median_defect_resolution_days=median_defect_days,
        osi_approved_license=is_osi_approved(license_spdx),
    )
