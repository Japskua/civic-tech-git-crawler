import csv
import logging
from datetime import datetime
from pathlib import Path

from civic_tech_crawler.models import CrossProjectOverlap, RepositoryData

logger = logging.getLogger(__name__)


def _fmt(value) -> str:
    """Format a value for CSV output."""
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, list):
        return ";".join(str(v) for v in value)
    if isinstance(value, dict):
        return ";".join(f"{k}={v}" for k, v in value.items())
    if isinstance(value, bool):
        return str(value)
    return str(value)


def export_csv(
    data: list[RepositoryData],
    output_dir: str,
    cross_project_overlap: CrossProjectOverlap | None = None,
) -> None:
    """Export all metrics to CSV files."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    _export_repo_metrics(data, out)
    _export_person_metrics(data, out)
    _export_temporal_summary(data, out)
    _export_chaoss_summary(data, out)
    _export_prs(data, out)
    _export_tags(data, out)
    if cross_project_overlap:
        _export_cross_project_overlap(cross_project_overlap, out)

    logger.info("CSV files written to %s", out)


def _export_repo_metrics(data: list[RepositoryData], out: Path) -> None:
    headers = [
        "full_name", "name", "description", "num_developers", "total_commits",
        "languages", "primary_language", "first_commit_date", "last_commit_date",
        "license_spdx", "license_name", "is_osi_approved", "topics",
        "has_contributing", "has_code_of_conduct", "has_governance",
        "has_readme", "has_issue_template", "has_pr_template", "health_percentage",
        "stars", "watchers", "forks",
        "cloud_detected", "cloud_signals", "ai_ml_detected", "ai_ml_signals",
        "has_ci_cd", "ci_cd_workflows", "deployments_count",
        "created_at", "updated_at", "size_kb",
    ]
    filepath = out / "repo_metrics.csv"
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for rd in data:
            m = rd.repo_metrics
            writer.writerow({h: _fmt(getattr(m, h)) for h in headers})
    logger.info("Wrote %s (%d rows)", filepath.name, len(data))


def _export_person_metrics(data: list[RepositoryData], out: Path) -> None:
    headers = [
        "repo_full_name", "login", "name", "num_commits",
        "additions", "deletions",
        "avg_additions_per_commit", "avg_deletions_per_commit",
    ]
    filepath = out / "person_metrics.csv"
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for rd in data:
            for p in rd.person_metrics:
                writer.writerow({h: _fmt(getattr(p, h)) for h in headers})
    total = sum(len(rd.person_metrics) for rd in data)
    logger.info("Wrote %s (%d rows)", filepath.name, total)


def _export_temporal_summary(data: list[RepositoryData], out: Path) -> None:
    headers = [
        "repo_full_name", "pr_count_total", "pr_count_merged",
        "pr_count_open", "pr_count_closed_unmerged",
        "tag_count", "release_count",
    ]
    filepath = out / "temporal_summary.csv"
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for rd in data:
            t = rd.temporal_metrics
            if t:
                writer.writerow({h: _fmt(getattr(t, h)) for h in headers})
    logger.info("Wrote %s", filepath.name)


def _export_chaoss_summary(data: list[RepositoryData], out: Path) -> None:
    headers = [
        "repo_full_name",
        "change_request_acceptance_ratio", "bus_factor",
        "contribution_types",
        "organizational_diversity", "newcomer_friendly_labels", "total_labels",
        "release_frequency_per_month", "fork_count",
        "burstiness_cv", "burstiness_mean", "burstiness_std",
        "median_defect_resolution_days", "osi_approved_license",
        "elephant_factor",
        "contributor_new_count", "contributor_casual_count", "contributor_regular_count",
        "median_time_to_first_response_issues_hours",
        "median_time_to_first_response_prs_hours",
        "time_to_first_response_issues_sample_size",
        "time_to_first_response_prs_sample_size",
        "readme_last_updated", "contributing_last_updated",
        "stale_issue_ratio", "stale_issue_count", "open_issue_count",
        "median_pr_review_turnaround_hours", "avg_review_comments_per_pr",
        "herfindahl_hirschman_index",
        "contributor_org_types",
        "dora_deployment_frequency_per_month",
        "dora_median_lead_time_days",
        "dora_change_failure_rate",
    ]
    filepath = out / "chaoss_summary.csv"
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for rd in data:
            c = rd.chaoss_metrics
            if c:
                writer.writerow({h: _fmt(getattr(c, h)) for h in headers})
    logger.info("Wrote %s", filepath.name)


def _export_prs(data: list[RepositoryData], out: Path) -> None:
    headers = [
        "repo_full_name", "number", "title", "state",
        "author_login", "created_at", "merged_at", "closed_at",
    ]
    filepath = out / "pull_requests.csv"
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for rd in data:
            t = rd.temporal_metrics
            if t:
                for pr in t.prs:
                    row = {
                        "repo_full_name": t.repo_full_name,
                        "number": pr.number,
                        "title": pr.title,
                        "state": pr.state,
                        "author_login": _fmt(pr.author_login),
                        "created_at": _fmt(pr.created_at),
                        "merged_at": _fmt(pr.merged_at),
                        "closed_at": _fmt(pr.closed_at),
                    }
                    writer.writerow(row)
    logger.info("Wrote %s", filepath.name)


def _export_tags(data: list[RepositoryData], out: Path) -> None:
    headers = ["repo_full_name", "name", "commit_sha", "date"]
    filepath = out / "tags.csv"
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for rd in data:
            t = rd.temporal_metrics
            if t:
                for tag in t.tags:
                    row = {
                        "repo_full_name": t.repo_full_name,
                        "name": tag.name,
                        "commit_sha": tag.commit_sha,
                        "date": _fmt(tag.date),
                    }
                    writer.writerow(row)
    logger.info("Wrote %s", filepath.name)


def _export_cross_project_overlap(
    overlap: CrossProjectOverlap, out: Path
) -> None:
    """Export cross-project contributor overlap as a CSV file."""
    # Summary row
    filepath = out / "cross_project_overlap.csv"
    headers = [
        "login", "repos_contributed_to",
    ]
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        # Sort by repo count descending, then by login
        sorted_contributors = sorted(
            overlap.contributor_repo_counts.items(),
            key=lambda x: (-x[1], x[0]),
        )
        for login, count in sorted_contributors:
            writer.writerow({"login": login, "repos_contributed_to": count})
    logger.info(
        "Wrote %s (%d contributors, %d in 2+ repos)",
        filepath.name,
        overlap.total_unique_contributors,
        overlap.multi_repo_contributors,
    )
