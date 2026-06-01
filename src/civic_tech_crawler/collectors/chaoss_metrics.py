import logging
import math
import re
from datetime import datetime, timedelta, timezone

import networkx as nx
from github import GithubException, Repository

from civic_tech_crawler.client import GitHubClient
from civic_tech_crawler.models import (
    ChaossMetrics,
    CorePeripheryContributor,
    PersonMetrics,
    RepoMetrics,
    TemporalMetrics,
)
from civic_tech_crawler.utils.osi_licenses import is_osi_approved

logger = logging.getLogger(__name__)

FIRST_RESPONSE_SAMPLE_SIZE = 100
PR_REVIEW_SAMPLE_SIZE = 100
STALE_ISSUE_CAP = 1000
STALE_THRESHOLD_DAYS = 90

# --- Institutional Type Classification patterns ---
_GOV_PATTERNS = re.compile(
    r"\b(gov|government|federal|state|county|city|municipal|ministry|"
    r"parliament|cabinet|department|agency|public.?sector|"
    r"gob|gobierno|kommun|kommune|regierung)\b",
    re.IGNORECASE,
)
_ACADEMIC_PATTERNS = re.compile(
    r"\b(university|universit[äéy]|college|institute|"
    r"research|academia|school|faculty|lab|"
    r"polytechnic|hochschule)\b|\.edu\b",
    re.IGNORECASE,
)
_NONPROFIT_PATTERNS = re.compile(
    r"\b(nonprofit|non.?profit|ngo|foundation|charity|"
    r"association|civic|community|open.?source|"
    r"free.?software|mozilla|apache|linux|"
    r"humanitarian|volunteer)\b|\.org\b",
    re.IGNORECASE,
)

# Known GitHub org names mapped to institutional types
_KNOWN_ORG_TYPES: dict[str, str] = {
    # Civic tech NGOs / nonprofits
    "DemocracyClub": "nonprofit",
    "codeforamerica": "nonprofit",
    "CodeForAfrica": "nonprofit",
    "codeforjapan": "nonprofit",
    "codeforall": "nonprofit",
    "mysociety": "nonprofit",
    "fvialibre": "nonprofit",
    "okfn": "nonprofit",
    "openaustralia": "nonprofit",
    "civiform": "nonprofit",
    "iiab": "nonprofit",
    "meshtastic": "nonprofit",
    "luftdata": "nonprofit",
    # Government
    "alphagov": "government",
    "18F": "government",
    "usds": "government",
    "gsa": "government",
    # Academic / research
    "markov-root": "academic",
}

# Email domain to institutional type mapping
_EMAIL_DOMAIN_TYPES: dict[str, str] = {
    ".gov": "government",
    ".gov.uk": "government",
    ".gov.au": "government",
    ".edu": "academic",
    ".ac.uk": "academic",
    ".ac.jp": "academic",
}

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


def _compute_elephant_factor(org_commits: dict[str, int]) -> int | None:
    """Minimum number of organisations responsible for 50% of commits."""
    if not org_commits:
        return None
    total = sum(org_commits.values())
    if total == 0:
        return None
    sorted_counts = sorted(org_commits.values(), reverse=True)
    running_sum = 0
    for i, commits in enumerate(sorted_counts):
        running_sum += commits
        if running_sum >= total * 0.5:
            return i + 1
    return len(sorted_counts)


def _compute_contributor_retention(
    client: GitHubClient,
    repo: Repository.Repository,
) -> tuple[int, int, int]:
    """Classify contributors into new/casual/regular based on active weeks.

    Returns (new_count, casual_count, regular_count).
    - new: contributed in only 1 week
    - casual: contributed in 2-12 weeks
    - regular: contributed in 13+ weeks
    """
    stats = client.get_stats_contributors(repo)
    if stats is None:
        return 0, 0, 0

    new_count = 0
    casual_count = 0
    regular_count = 0

    for contributor in stats:
        active_weeks = sum(1 for w in contributor.weeks if w.c > 0)
        if active_weeks <= 1:
            new_count += 1
        elif active_weeks <= 12:
            casual_count += 1
        else:
            regular_count += 1

    return new_count, casual_count, regular_count


def _compute_median(values: list[float]) -> float | None:
    """Compute the median of a list of floats."""
    if not values:
        return None
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n % 2 == 0:
        return round((sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2, 1)
    return round(sorted_vals[n // 2], 1)


def _compute_median_first_response(
    repo: Repository.Repository,
    item_type: str,
    sample_size: int = FIRST_RESPONSE_SAMPLE_SIZE,
) -> tuple[float | None, int]:
    """Compute median time to first non-author comment on issues or PRs.

    Args:
        repo: The GitHub repository object.
        item_type: Either "issues" or "pulls".
        sample_size: Maximum number of items to sample.

    Returns:
        (median_hours, actual_sample_size)
    """
    deltas_hours: list[float] = []
    count = 0

    try:
        if item_type == "issues":
            items = repo.get_issues(state="all", sort="created", direction="desc")
        else:
            items = repo.get_pulls(state="all", sort="created", direction="desc")

        for item in items:
            if count >= sample_size:
                break

            # When iterating issues, skip PRs (GitHub API returns both)
            if item_type == "issues" and hasattr(item, "pull_request") and item.pull_request is not None:
                continue

            author_login = item.user.login if item.user else None
            try:
                comments = item.get_comments()
                for comment in comments:
                    commenter = comment.user.login if comment.user else None
                    if commenter != author_login:
                        delta = (comment.created_at - item.created_at).total_seconds() / 3600
                        deltas_hours.append(delta)
                        break  # only first non-author comment
            except GithubException:
                pass
            count += 1
    except GithubException:
        pass

    return _compute_median(deltas_hours), count


def _compute_pr_review_metrics(
    repo: Repository.Repository,
    sample_size: int = PR_REVIEW_SAMPLE_SIZE,
) -> tuple[float | None, float | None, list[tuple[str, str]]]:
    """Compute median review turnaround, average review comments per PR,
    and PR author-reviewer collaboration edges.

    Samples the most recently merged PRs.

    Returns:
        (median_turnaround_hours, avg_comments_per_pr, edges)
        where edges is a list of (author_login, reviewer_login) tuples.
    """
    turnaround_hours: list[float] = []
    review_comment_counts: list[int] = []
    edges: list[tuple[str, str]] = []

    try:
        closed_prs = repo.get_pulls(state="closed", sort="updated", direction="desc")
        count = 0
        for pr in closed_prs:
            if count >= sample_size:
                break
            if pr.merged_at is None:
                continue  # skip closed-but-not-merged

            pr_author = pr.user.login if pr.user else None

            try:
                reviews = list(pr.get_reviews())
                # Capture author-reviewer edges for core-periphery analysis
                if pr_author and reviews:
                    for review in reviews:
                        reviewer_login = review.user.login if review.user else None
                        if reviewer_login and reviewer_login != pr_author:
                            edges.append((pr_author, reviewer_login))
                if reviews:
                    # First review turnaround
                    first_review = min(reviews, key=lambda r: r.submitted_at)
                    delta = (first_review.submitted_at - pr.created_at).total_seconds() / 3600
                    turnaround_hours.append(delta)
                    # Count review comments (reviews with non-empty body)
                    comment_count = sum(1 for r in reviews if r.body and r.body.strip())
                    review_comment_counts.append(comment_count)
                else:
                    review_comment_counts.append(0)
            except GithubException:
                pass
            count += 1
    except GithubException:
        pass

    median_turnaround = _compute_median(turnaround_hours)

    avg_comments: float | None = None
    if review_comment_counts:
        avg_comments = round(sum(review_comment_counts) / len(review_comment_counts), 2)

    return median_turnaround, avg_comments, edges


def _compute_hhi(org_commits: dict[str, int]) -> float | None:
    """Compute Herfindahl-Hirschman Index for organizational concentration.

    HHI ranges from near 0 (perfect competition) to 10,000 (monopoly).
    A single-org project has HHI = 10,000. Lower values indicate more
    diverse organizational participation.

    Uses commit shares: HHI = Σ(share_i * 100)² where share_i = org_commits_i / total.
    """
    if not org_commits:
        return None
    total = sum(org_commits.values())
    if total == 0:
        return None
    hhi = sum(((commits / total) * 100) ** 2 for commits in org_commits.values())
    return round(hhi, 1)


def _classify_org_type(company: str) -> str:
    """Classify an organization string into institutional type.

    Returns one of: "government", "academic", "nonprofit", "company", "unknown".
    """
    if not company or company == "Unknown":
        return "unknown"
    if _GOV_PATTERNS.search(company):
        return "government"
    if _ACADEMIC_PATTERNS.search(company):
        return "academic"
    if _NONPROFIT_PATTERNS.search(company):
        return "nonprofit"
    # If the company field is non-empty and doesn't match other patterns,
    # it's likely a private company
    return "company"


def _classify_email_domain(email: str | None) -> str | None:
    """Classify institutional type from email domain."""
    if not email:
        return None
    email_lower = email.lower()
    for suffix, org_type in _EMAIL_DOMAIN_TYPES.items():
        if email_lower.endswith(suffix):
            return org_type
    return None


def _classify_contributor(
    login: str,
    client: GitHubClient,
) -> str:
    """Classify a contributor using multiple signals.

    Priority: company field > known org membership > bio field > email domain.
    Returns one of: "government", "academic", "nonprofit", "company", "unknown".
    """
    user_info = client.get_user_info(login)
    company = (user_info.get("company") or "").strip().lstrip("@")

    # 1. Company field (existing approach)
    if company and company != "Unknown":
        result = _classify_org_type(company)
        if result != "unknown":
            return result

    # 2. Check known org membership
    orgs = client.get_user_orgs(login)
    for org_login in orgs:
        if org_login in _KNOWN_ORG_TYPES:
            return _KNOWN_ORG_TYPES[org_login]

    # 3. Bio field scanning
    bio = user_info.get("bio") or ""
    if bio:
        bio_type = _classify_org_type(bio)
        if bio_type != "unknown":
            return bio_type

    # 4. Email domain heuristic
    email = user_info.get("email")
    email_type = _classify_email_domain(email)
    if email_type:
        return email_type

    # 5. If company field was non-empty but didn't match patterns, it's a company
    if company:
        return "company"

    return "unknown"


def _compute_institutional_types(
    person_metrics: list[PersonMetrics],
    client: GitHubClient,
) -> dict[str, int]:
    """Classify contributors by their organizational affiliation type.

    Uses multiple signals: company field, org membership, bio, email domain.
    Returns {type: count}.
    """
    types: dict[str, int] = {
        "government": 0,
        "academic": 0,
        "nonprofit": 0,
        "company": 0,
        "unknown": 0,
    }
    for p in person_metrics:
        if p.login and not p.is_bot:
            org_type = _classify_contributor(p.login, client)
            types[org_type] += 1
        elif p.is_bot:
            pass  # Skip bots from institutional classification
        else:
            types["unknown"] += 1
    return types


def _compute_dora_metrics(
    repo_metrics: RepoMetrics,
    temporal_metrics: TemporalMetrics | None,
) -> tuple[float | None, float | None, float | None]:
    """Compute DORA-inspired metrics from existing data.

    Returns:
        (deployment_frequency_per_month, median_lead_time_days, change_failure_rate)

    - Deployment frequency: releases per month over the repo's lifetime.
    - Lead time: median days between consecutive releases (proxy for
      time from code change to production).
    - Change failure rate: ratio of reverted/hotfix PRs to total merged PRs
      (heuristic based on PR title patterns).
    """
    deployment_freq: float | None = None
    median_lead_time: float | None = None
    change_failure_rate: float | None = None

    # --- Deployment frequency ---
    if temporal_metrics and temporal_metrics.release_count > 0:
        repo_age_months = (
            (repo_metrics.updated_at - repo_metrics.created_at).days / 30.44
        )
        if repo_age_months > 0:
            deployment_freq = round(
                temporal_metrics.release_count / repo_age_months, 2
            )

    # --- Lead time (median days between consecutive releases) ---
    if temporal_metrics and temporal_metrics.release_count >= 2:
        sorted_releases = sorted(
            temporal_metrics.releases, key=lambda r: r.created_at
        )
        intervals_days: list[float] = []
        for i in range(1, len(sorted_releases)):
            delta = (
                sorted_releases[i].created_at - sorted_releases[i - 1].created_at
            ).total_seconds() / 86400
            intervals_days.append(delta)
        if intervals_days:
            sorted_intervals = sorted(intervals_days)
            n = len(sorted_intervals)
            if n % 2 == 0:
                median_lead_time = round(
                    (sorted_intervals[n // 2 - 1] + sorted_intervals[n // 2]) / 2, 1
                )
            else:
                median_lead_time = round(sorted_intervals[n // 2], 1)

    # --- Change failure rate (heuristic from PR titles) ---
    if temporal_metrics and temporal_metrics.pr_count_merged > 0:
        failure_pattern = re.compile(
            r"\b(revert|hotfix|hot.?fix|rollback|roll.?back|"
            r"fix.?deploy|emergency|patch|bugfix|bug.?fix)\b",
            re.IGNORECASE,
        )
        failure_count = 0
        for pr in temporal_metrics.prs:
            if pr.merged_at and failure_pattern.search(pr.title):
                failure_count += 1
        change_failure_rate = round(
            failure_count / temporal_metrics.pr_count_merged, 4
        )

    return deployment_freq, median_lead_time, change_failure_rate


def _compute_core_periphery(
    edges: list[tuple[str, str]],
) -> tuple[int, int, float | None, float | None, float | None, list[dict]]:
    """Compute core-periphery classification from PR author-reviewer edges.

    Uses degree centrality and betweenness centrality on an undirected
    collaboration graph. Contributors with degree centrality strictly above
    the median are classified as "core"; the rest as "periphery".

    Args:
        edges: List of (author_login, reviewer_login) tuples.

    Returns:
        (core_count, periphery_count, core_periphery_ratio,
         network_density, avg_degree_centrality, contributor_details)
    """
    if not edges:
        return 0, 0, None, None, None, []

    G = nx.Graph()
    for author, reviewer in edges:
        if G.has_edge(author, reviewer):
            G[author][reviewer]["weight"] += 1
        else:
            G.add_edge(author, reviewer, weight=1)

    if G.number_of_nodes() < 2:
        return 0, 0, None, None, None, []

    degree_cent = nx.degree_centrality(G)
    betweenness_cent = nx.betweenness_centrality(G)
    density = nx.density(G)

    # Classification threshold: median degree centrality
    centrality_values = sorted(degree_cent.values())
    n = len(centrality_values)
    if n % 2 == 0:
        median_cent = (centrality_values[n // 2 - 1] + centrality_values[n // 2]) / 2
    else:
        median_cent = centrality_values[n // 2]

    contributor_details: list[dict] = []
    core_count = 0
    periphery_count = 0

    for node in G.nodes():
        dc = degree_cent[node]
        bc = betweenness_cent[node]
        classification = "core" if dc > median_cent else "periphery"
        if classification == "core":
            core_count += 1
        else:
            periphery_count += 1
        contributor_details.append({
            "login": node,
            "degree_centrality": round(dc, 4),
            "betweenness_centrality": round(bc, 4),
            "classification": classification,
            "num_collaborators": G.degree(node),
        })

    total = core_count + periphery_count
    ratio = round(core_count / total, 4) if total > 0 else None
    avg_dc = round(sum(degree_cent.values()) / len(degree_cent), 4)

    return core_count, periphery_count, ratio, round(density, 4), avg_dc, contributor_details


def collect_chaoss_metrics(
    client: GitHubClient,
    repo: Repository.Repository,
    person_metrics: list[PersonMetrics],
    temporal_metrics: TemporalMetrics | None,
    repo_metrics: RepoMetrics | None = None,
    commit_history=None,
) -> tuple[ChaossMetrics, list[CorePeripheryContributor]]:
    """Collect CHAOSS framework metrics and core-periphery classification.

    If commit_history is provided and GitHub's /stats/commit_activity endpoint
    is unavailable (typical for active repos whose async build exceeds the
    retry budget), weekly_commits falls back to the last 52 weekly_snapshots
    from commit_history so burstiness_cv can still be computed.
    """
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
    elif commit_history is not None and getattr(commit_history, "weekly_snapshots", None):
        # Fallback: derive trailing-52-week commit counts from commit_history's
        # GraphQL-derived weekly snapshots. Same metric, more reliable source.
        snaps = list(commit_history.weekly_snapshots)[-52:]
        weekly_commits = [
            {"week_start": s.week_start, "commits": int(s.total_commits)}
            for s in snaps
        ]
        logger.info(
            "%s: stats/commit_activity unavailable, derived %d weekly commit "
            "buckets from commit_history fallback",
            slug, len(weekly_commits),
        )

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

    # --- Bot-filtered metrics ---
    humans = [p for p in person_metrics if not p.is_bot]
    bots = [p for p in person_metrics if p.is_bot]
    bot_contributor_count = len(bots)
    bot_commit_count = sum(p.num_commits for p in bots)
    bus_factor_no_bots = _compute_bus_factor(humans) if humans else None

    # --- Organizational Diversity + Elephant Factor data ---
    org_diversity: dict[str, int] = {}
    org_commits: dict[str, int] = {}
    # For HHI fix: track per-unknown-contributor org commits separately
    org_commits_unknown_split: dict[str, int] = {}
    org_commits_known_only: dict[str, int] = {}
    unknown_org_count = 0
    for p in person_metrics:
        if p.is_bot:
            continue  # Exclude bots from org diversity
        if p.login:
            user_info = client.get_user_info(p.login)
            company = user_info.get("company") or "Unknown"
            company = company.strip().lstrip("@")
            if not company or company == "Unknown":
                company = "Unknown"
            org_diversity[company] = org_diversity.get(company, 0) + 1
            org_commits[company] = org_commits.get(company, 0) + p.num_commits
            # For HHI fix: split unknown contributors into individuals
            if company == "Unknown":
                unknown_org_count += 1
                ind_key = f"_unknown_{p.login}"
                org_commits_unknown_split[ind_key] = p.num_commits
            else:
                org_commits_unknown_split[company] = (
                    org_commits_unknown_split.get(company, 0) + p.num_commits
                )
                org_commits_known_only[company] = (
                    org_commits_known_only.get(company, 0) + p.num_commits
                )

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

    # --- Elephant Factor (org-level bus factor) ---
    elephant_factor = _compute_elephant_factor(org_commits)
    # Bot-filtered: use org_commits which already excludes bots
    elephant_factor_no_bots = elephant_factor  # already bot-filtered above

    # --- Contributor Retention Cohorts ---
    logger.info("Computing contributor retention cohorts for %s", slug)
    new_count, casual_count, regular_count = _compute_contributor_retention(client, repo)

    # --- Time to First Response (Issues) ---
    logger.info("Computing time to first response (issues) for %s", slug)
    ttfr_issues, ttfr_issues_n = _compute_median_first_response(repo, "issues")

    # --- Time to First Response (PRs) ---
    logger.info("Computing time to first response (PRs) for %s", slug)
    ttfr_prs, ttfr_prs_n = _compute_median_first_response(repo, "pulls")

    # --- Documentation Freshness ---
    logger.info("Computing documentation freshness for %s", slug)
    readme_updated_str = client.get_last_commit_date_for_path(slug, "README.md")
    readme_last_updated = datetime.fromisoformat(readme_updated_str) if readme_updated_str else None
    contributing_updated_str = client.get_last_commit_date_for_path(slug, "CONTRIBUTING.md")
    contributing_last_updated = datetime.fromisoformat(contributing_updated_str) if contributing_updated_str else None

    # --- Stale Issue Ratio ---
    logger.info("Computing stale issue ratio for %s", slug)
    stale_count = 0
    open_count = 0
    stale_ratio: float | None = None
    stale_threshold = datetime.now(timezone.utc) - timedelta(days=STALE_THRESHOLD_DAYS)
    try:
        open_issues = repo.get_issues(state="open")
        for issue in open_issues:
            if issue.pull_request is not None:
                continue  # skip PRs
            open_count += 1
            if issue.updated_at.replace(tzinfo=timezone.utc) < stale_threshold:
                stale_count += 1
            if open_count >= STALE_ISSUE_CAP:
                break
        if open_count > 0:
            stale_ratio = round(stale_count / open_count, 4)
    except GithubException:
        pass

    # --- PR Review Depth & Turnaround + Collaboration Edges ---
    logger.info("Computing PR review metrics for %s", slug)
    pr_review_turnaround, pr_review_depth, pr_review_edges = _compute_pr_review_metrics(repo)

    # --- Core-Periphery Network Analysis ---
    logger.info("Computing core-periphery network analysis for %s", slug)
    (
        core_count, periphery_count, cp_ratio,
        net_density, avg_dc, cp_contributor_details,
    ) = _compute_core_periphery(pr_review_edges)

    # --- Herfindahl-Hirschman Index ---
    hhi = _compute_hhi(org_commits)
    # HHI with unknown contributors split into individuals (reduces phantom concentration)
    hhi_no_bots = _compute_hhi(org_commits_unknown_split)
    # HHI using only known-org contributors (cleanest signal, but may have small N)
    hhi_known_orgs_only = _compute_hhi(org_commits_known_only) if org_commits_known_only else None

    # --- Institutional Type Classification ---
    logger.info("Computing institutional type classification for %s", slug)
    contributor_org_types = _compute_institutional_types(person_metrics, client)

    # --- DORA Metrics ---
    logger.info("Computing DORA metrics for %s", slug)
    dora_deploy_freq, dora_lead_time, dora_cfr = _compute_dora_metrics(
        repo_metrics, temporal_metrics
    ) if repo_metrics else (None, None, None)

    chaoss = ChaossMetrics(
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
        bus_factor_no_bots=bus_factor_no_bots,
        bot_contributor_count=bot_contributor_count,
        bot_commit_count=bot_commit_count,
        elephant_factor=elephant_factor,
        elephant_factor_no_bots=elephant_factor_no_bots,
        contributor_new_count=new_count,
        contributor_casual_count=casual_count,
        contributor_regular_count=regular_count,
        median_time_to_first_response_issues_hours=ttfr_issues,
        median_time_to_first_response_prs_hours=ttfr_prs,
        time_to_first_response_issues_sample_size=ttfr_issues_n,
        time_to_first_response_prs_sample_size=ttfr_prs_n,
        readme_last_updated=readme_last_updated,
        contributing_last_updated=contributing_last_updated,
        stale_issue_ratio=stale_ratio,
        stale_issue_count=stale_count,
        open_issue_count=open_count,
        median_pr_review_turnaround_hours=pr_review_turnaround,
        avg_review_comments_per_pr=pr_review_depth,
        herfindahl_hirschman_index=hhi,
        hhi_no_bots=hhi_no_bots,
        hhi_known_orgs_only=hhi_known_orgs_only,
        unknown_org_contributor_count=unknown_org_count,
        contributor_org_types=contributor_org_types,
        dora_deployment_frequency_per_month=dora_deploy_freq,
        dora_median_lead_time_days=dora_lead_time,
        dora_change_failure_rate=dora_cfr,
        core_contributor_count=core_count,
        periphery_contributor_count=periphery_count,
        core_periphery_ratio=cp_ratio,
        network_density=net_density,
        avg_degree_centrality=avg_dc,
        pr_review_edges=[{"author": a, "reviewer": r} for a, r in pr_review_edges],
    )

    cp_contributors = [
        CorePeripheryContributor(
            repo_full_name=slug,
            login=d["login"],
            degree_centrality=d["degree_centrality"],
            betweenness_centrality=d["betweenness_centrality"],
            classification=d["classification"],
            num_collaborators=d["num_collaborators"],
        )
        for d in cp_contributor_details
    ]

    return chaoss, cp_contributors
