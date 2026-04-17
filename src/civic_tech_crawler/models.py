from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CrawlerConfig:
    token: str
    repositories: list[str]
    output_dir: str = "./output"
    max_retries: int = 5
    retry_delay: float = 3.0
    rate_limit_buffer: int = 100
    cloud_keywords: dict = field(default_factory=dict)
    ai_ml_keywords: dict = field(default_factory=dict)
    skip_chaoss: bool = False
    skip_temporal: bool = False
    skip_detection: bool = False
    skip_commit_history: bool = False
    skip_issue_analytics: bool = False


@dataclass
class RepoMetrics:
    full_name: str
    name: str
    description: str | None
    num_developers: int
    total_commits: int
    languages: dict[str, int]
    primary_language: str | None
    first_commit_date: datetime | None
    last_commit_date: datetime | None
    license_spdx: str | None
    license_name: str | None
    is_osi_approved: bool
    topics: list[str]
    has_contributing: bool
    has_code_of_conduct: bool
    has_governance: bool
    has_readme: bool
    has_issue_template: bool
    has_pr_template: bool
    health_percentage: int
    stars: int
    watchers: int
    forks: int
    cloud_detected: bool
    cloud_signals: list[str]
    ai_ml_detected: bool
    ai_ml_signals: list[str]
    has_ci_cd: bool
    ci_cd_workflows: list[str]
    deployments_count: int
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime | None = None
    size_kb: int = 0


@dataclass
class PersonMetrics:
    repo_full_name: str
    login: str | None
    name: str | None
    num_commits: int
    additions: int
    deletions: int
    avg_additions_per_commit: float
    avg_deletions_per_commit: float
    is_bot: bool = False


@dataclass
class PRRecord:
    number: int
    title: str
    state: str
    author_login: str | None
    created_at: datetime
    merged_at: datetime | None
    closed_at: datetime | None


@dataclass
class TagRecord:
    name: str
    commit_sha: str
    date: datetime | None


@dataclass
class ReleaseRecord:
    tag_name: str
    name: str | None
    created_at: datetime
    is_prerelease: bool


@dataclass
class TemporalMetrics:
    repo_full_name: str
    pr_count_total: int
    pr_count_merged: int
    pr_count_open: int
    pr_count_closed_unmerged: int
    prs: list[PRRecord]
    tag_count: int
    tags: list[TagRecord]
    release_count: int
    releases: list[ReleaseRecord]


@dataclass
class ChaossMetrics:
    repo_full_name: str
    # Common
    weekly_commits: list[dict]  # [{week_start: str, commits: int}, ...]
    change_request_acceptance_ratio: float | None
    bus_factor: int | None
    contribution_types: dict[str, int]  # {code: N, issues: N, prs: N}
    # DEI
    organizational_diversity: dict[str, int]  # {org_name: contributor_count}
    newcomer_friendly_labels: list[str]
    total_labels: int
    # Evolution
    release_frequency_per_month: float | None
    fork_count: int
    burstiness_cv: float | None  # coefficient of variation
    burstiness_mean: float | None
    burstiness_std: float | None
    # Risk
    defect_resolution_durations_days: list[dict]  # [{issue_number, days}]
    median_defect_resolution_days: float | None
    osi_approved_license: bool
    # Bot-filtered variants
    bus_factor_no_bots: int | None = None
    bot_contributor_count: int = 0
    bot_commit_count: int = 0
    # Elephant Factor (org-level bus factor)
    elephant_factor: int | None = None
    elephant_factor_no_bots: int | None = None
    # Contributor Retention Cohorts
    contributor_new_count: int = 0  # 1 active week
    contributor_casual_count: int = 0  # 2-12 active weeks
    contributor_regular_count: int = 0  # 13+ active weeks
    # Time to First Response
    median_time_to_first_response_issues_hours: float | None = None
    median_time_to_first_response_prs_hours: float | None = None
    time_to_first_response_issues_sample_size: int = 0
    time_to_first_response_prs_sample_size: int = 0
    # Documentation Freshness
    readme_last_updated: datetime | None = None
    contributing_last_updated: datetime | None = None
    # Stale Issue Ratio
    stale_issue_ratio: float | None = None
    stale_issue_count: int = 0
    open_issue_count: int = 0
    # PR Review Depth & Turnaround
    median_pr_review_turnaround_hours: float | None = None
    avg_review_comments_per_pr: float | None = None
    # Herfindahl-Hirschman Index (org concentration)
    herfindahl_hirschman_index: float | None = None
    hhi_no_bots: float | None = None
    hhi_known_orgs_only: float | None = None
    unknown_org_contributor_count: int = 0
    # Institutional Type Classification
    contributor_org_types: dict[str, int] = field(
        default_factory=lambda: {}
    )  # {government: N, nonprofit: N, academic: N, company: N, unknown: N}
    # DORA Metrics
    dora_deployment_frequency_per_month: float | None = None
    dora_median_lead_time_days: float | None = None
    dora_change_failure_rate: float | None = None
    # Core-Periphery Network Analysis
    core_contributor_count: int = 0
    periphery_contributor_count: int = 0
    core_periphery_ratio: float | None = None
    network_density: float | None = None
    avg_degree_centrality: float | None = None
    pr_review_edges: list[dict] = field(
        default_factory=list
    )  # [{author: str, reviewer: str}, ...] — cached for re-computation


@dataclass
class CrossProjectOverlap:
    """Cross-project contributor overlap metrics (computed post-crawl)."""
    total_unique_contributors: int
    multi_repo_contributors: int  # contributors appearing in 2+ repos
    multi_repo_ratio: float  # multi_repo_contributors / total_unique
    contributor_repo_counts: dict[str, int] = field(
        default_factory=dict
    )  # {login: number_of_repos}
    per_repo_overlap: dict[str, int] = field(
        default_factory=dict
    )  # {repo_full_name: count_of_shared_contributors}


@dataclass
class CorePeripheryContributor:
    """Per-contributor core-periphery network analysis metrics."""
    repo_full_name: str
    login: str
    degree_centrality: float
    betweenness_centrality: float
    classification: str  # "core" or "periphery"
    num_collaborators: int


@dataclass
class WeeklySnapshot:
    """Weekly project-level commit/contributor aggregation."""
    week_start: str  # ISO date (Monday of the week)
    total_commits: int
    unique_contributors: int
    new_contributors: int  # first-time contributors this week
    cumulative_commits: int
    cumulative_contributors: int


@dataclass
class ContributorWeek:
    """Per-person weekly commit activity."""
    contributor_id: str  # login or email (unique key)
    week_start: str
    commits: int
    lines_added: int = 0
    lines_removed: int = 0


@dataclass
class ContributorLifecycle:
    """Contributor lifecycle: appearance, departure, duration."""
    repo_full_name: str
    contributor_id: str  # login or email
    login: str | None
    name: str | None
    email: str
    first_commit_date: datetime
    last_commit_date: datetime
    duration_days: int
    total_commits: int
    active_weeks: int  # weeks with >= 1 commit
    total_weeks_span: int  # weeks from first to last commit
    activity_ratio: float  # active_weeks / total_weeks_span
    status: str  # "active" or "departed" (no commits in 90 days)
    departed_weeks_ago: int | None
    avg_commits_per_active_week: float


@dataclass
class CommitHistoryMetrics:
    """Full commit history parsed into weekly snapshots + contributor lifecycles."""
    repo_full_name: str
    weekly_snapshots: list[WeeklySnapshot]
    contributor_lifecycles: list[ContributorLifecycle]
    contributor_weeks: list[ContributorWeek]
    total_weeks: int
    total_unique_contributors: int
    new_contributor_rate_per_month: float | None


@dataclass
class IssueRecord:
    """Per-issue detailed record."""
    number: int
    title: str
    state: str  # "open" or "closed"
    author_login: str | None
    closed_by_login: str | None
    created_at: datetime
    closed_at: datetime | None
    updated_at: datetime
    comment_count: int
    labels: list[str]
    time_to_close_days: float | None


@dataclass
class IssueAnalytics:
    """Container for all issue analytics."""
    repo_full_name: str
    issues: list[IssueRecord]
    total_issues: int
    open_issues: int
    closed_issues: int
    avg_comments_per_issue: float | None
    median_time_to_close_days: float | None
    unique_openers: int
    unique_closers: int
    top_openers: dict[str, int] = field(default_factory=dict)
    top_closers: dict[str, int] = field(default_factory=dict)


@dataclass
class RepositoryData:
    repo_metrics: RepoMetrics
    person_metrics: list[PersonMetrics]
    temporal_metrics: TemporalMetrics | None
    chaoss_metrics: ChaossMetrics | None
    crawled_at: datetime | None = None
    core_periphery_contributors: list[CorePeripheryContributor] = field(
        default_factory=list
    )
    commit_history: CommitHistoryMetrics | None = None
    issue_analytics: IssueAnalytics | None = None
