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
    _export_core_periphery(data, out)
    _export_weekly_snapshots(data, out)
    _export_contributor_lifecycles(data, out)
    _export_contributor_weekly_activity(data, out)
    _export_issue_records(data, out)
    _export_issue_summary(data, out)
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
        "created_at", "updated_at", "pushed_at", "size_kb",
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
        "is_bot",
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
        "change_request_acceptance_ratio", "bus_factor", "bus_factor_no_bots",
        "bot_contributor_count", "bot_commit_count",
        "contribution_types",
        "organizational_diversity", "newcomer_friendly_labels", "total_labels",
        "release_frequency_per_month", "fork_count",
        "burstiness_cv", "burstiness_mean", "burstiness_std",
        "median_defect_resolution_days", "osi_approved_license",
        "elephant_factor", "elephant_factor_no_bots",
        "contributor_new_count", "contributor_casual_count", "contributor_regular_count",
        "median_time_to_first_response_issues_hours",
        "median_time_to_first_response_prs_hours",
        "time_to_first_response_issues_sample_size",
        "time_to_first_response_prs_sample_size",
        "readme_last_updated", "contributing_last_updated",
        "stale_issue_ratio", "stale_issue_count", "open_issue_count",
        "median_pr_review_turnaround_hours", "avg_review_comments_per_pr",
        "herfindahl_hirschman_index", "hhi_no_bots", "hhi_known_orgs_only",
        "unknown_org_contributor_count",
        "contributor_org_types",
        "dora_deployment_frequency_per_month",
        "dora_median_lead_time_days",
        "dora_change_failure_rate",
        "core_contributor_count",
        "periphery_contributor_count",
        "core_periphery_ratio",
        "network_density",
        "avg_degree_centrality",
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


def _export_core_periphery(data: list[RepositoryData], out: Path) -> None:
    """Export per-contributor core-periphery network analysis."""
    headers = [
        "repo_full_name", "login", "degree_centrality",
        "betweenness_centrality", "classification", "num_collaborators",
    ]
    filepath = out / "core_periphery.csv"
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for rd in data:
            for c in rd.core_periphery_contributors:
                writer.writerow({h: _fmt(getattr(c, h)) for h in headers})
    total = sum(len(rd.core_periphery_contributors) for rd in data)
    logger.info("Wrote %s (%d rows)", filepath.name, total)


def _export_weekly_snapshots(data: list[RepositoryData], out: Path) -> None:
    """Export weekly project-level commit/contributor snapshots."""
    headers = [
        "repo_full_name", "week_start", "total_commits",
        "unique_contributors", "new_contributors",
        "cumulative_commits", "cumulative_contributors",
    ]
    filepath = out / "weekly_snapshots.csv"
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for rd in data:
            ch = rd.commit_history
            if ch:
                for s in ch.weekly_snapshots:
                    row = {"repo_full_name": ch.repo_full_name}
                    row.update({h: _fmt(getattr(s, h)) for h in headers[1:]})
                    writer.writerow(row)
    total = sum(
        len(rd.commit_history.weekly_snapshots)
        for rd in data
        if rd.commit_history
    )
    logger.info("Wrote %s (%d rows)", filepath.name, total)


def _export_contributor_lifecycles(data: list[RepositoryData], out: Path) -> None:
    """Export per-contributor lifecycle analysis."""
    headers = [
        "repo_full_name", "contributor_id", "login", "name", "email",
        "first_commit_date", "last_commit_date", "duration_days",
        "total_commits", "active_weeks", "total_weeks_span",
        "activity_ratio", "status", "departed_weeks_ago",
        "avg_commits_per_active_week",
    ]
    filepath = out / "contributor_lifecycles.csv"
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for rd in data:
            ch = rd.commit_history
            if ch:
                for lc in ch.contributor_lifecycles:
                    writer.writerow({h: _fmt(getattr(lc, h)) for h in headers})
    total = sum(
        len(rd.commit_history.contributor_lifecycles)
        for rd in data
        if rd.commit_history
    )
    logger.info("Wrote %s (%d rows)", filepath.name, total)


def _export_contributor_weekly_activity(data: list[RepositoryData], out: Path) -> None:
    """Export per-contributor weekly commit counts."""
    headers = [
        "repo_full_name",
        "contributor_id",
        "week_start",
        "commits",
        "lines_added",
        "lines_removed",
    ]
    filepath = out / "contributor_weekly_activity.csv"
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for rd in data:
            ch = rd.commit_history
            if ch:
                for cw in ch.contributor_weeks:
                    row = {
                        "repo_full_name": ch.repo_full_name,
                        "contributor_id": cw.contributor_id,
                        "week_start": cw.week_start,
                        "commits": cw.commits,
                        "lines_added": cw.lines_added,
                        "lines_removed": cw.lines_removed,
                    }
                    writer.writerow(row)
    total = sum(
        len(rd.commit_history.contributor_weeks)
        for rd in data
        if rd.commit_history
    )
    logger.info("Wrote %s (%d rows)", filepath.name, total)


def _export_issue_records(data: list[RepositoryData], out: Path) -> None:
    """Export per-issue detailed records."""
    headers = [
        "repo_full_name", "number", "title", "state",
        "author_login", "closed_by_login",
        "created_at", "closed_at", "updated_at",
        "comment_count", "labels", "time_to_close_days",
    ]
    filepath = out / "issue_records.csv"
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for rd in data:
            ia = rd.issue_analytics
            if ia:
                for issue in ia.issues:
                    row = {"repo_full_name": ia.repo_full_name}
                    row.update({h: _fmt(getattr(issue, h)) for h in headers[1:]})
                    writer.writerow(row)
    total = sum(
        len(rd.issue_analytics.issues)
        for rd in data
        if rd.issue_analytics
    )
    logger.info("Wrote %s (%d rows)", filepath.name, total)


def _export_issue_summary(data: list[RepositoryData], out: Path) -> None:
    """Export per-repo issue analytics summary."""
    headers = [
        "repo_full_name", "total_issues", "open_issues", "closed_issues",
        "avg_comments_per_issue", "median_time_to_close_days",
        "unique_openers", "unique_closers",
        "top_openers", "top_closers",
    ]
    filepath = out / "issue_summary.csv"
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for rd in data:
            ia = rd.issue_analytics
            if ia:
                writer.writerow({h: _fmt(getattr(ia, h)) for h in headers})
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
