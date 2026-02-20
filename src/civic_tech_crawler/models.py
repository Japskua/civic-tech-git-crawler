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
    size_kb: int


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
    # Elephant Factor (org-level bus factor)
    elephant_factor: int | None = None
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


@dataclass
class RepositoryData:
    repo_metrics: RepoMetrics
    person_metrics: list[PersonMetrics]
    temporal_metrics: TemporalMetrics | None
    chaoss_metrics: ChaossMetrics | None
    crawled_at: datetime | None = None
