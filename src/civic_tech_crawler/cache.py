"""Per-repository JSON cache for incremental and crash-resilient crawling.

Each crawled repository is immediately persisted as a JSON file in the output
directory. On subsequent runs, the tool loads cached results instead of
re-crawling, saving API calls and enabling resume after interruptions.
"""

import dataclasses
import json
import logging
from datetime import datetime
from pathlib import Path

from civic_tech_crawler.models import (
    ChaossMetrics,
    CorePeripheryContributor,
    PersonMetrics,
    PRRecord,
    ReleaseRecord,
    RepoMetrics,
    RepositoryData,
    TagRecord,
    TemporalMetrics,
)

logger = logging.getLogger(__name__)


class _DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def _slug_to_filename(slug: str) -> str:
    """Convert 'owner/repo' to 'owner_repo_data.json'."""
    return slug.replace("/", "_") + "_data.json"


def _parse_datetime(value: str | None) -> datetime | None:
    """Parse an ISO 8601 datetime string."""
    if value is None:
        return None
    return datetime.fromisoformat(value)


def _dict_to_repo_metrics(d: dict) -> RepoMetrics:
    return RepoMetrics(
        full_name=d["full_name"],
        name=d["name"],
        description=d.get("description"),
        num_developers=d["num_developers"],
        total_commits=d["total_commits"],
        languages=d["languages"],
        primary_language=d.get("primary_language"),
        first_commit_date=_parse_datetime(d.get("first_commit_date")),
        last_commit_date=_parse_datetime(d.get("last_commit_date")),
        license_spdx=d.get("license_spdx"),
        license_name=d.get("license_name"),
        is_osi_approved=d["is_osi_approved"],
        topics=d["topics"],
        has_contributing=d["has_contributing"],
        has_code_of_conduct=d["has_code_of_conduct"],
        has_governance=d["has_governance"],
        has_readme=d["has_readme"],
        has_issue_template=d["has_issue_template"],
        has_pr_template=d["has_pr_template"],
        health_percentage=d["health_percentage"],
        stars=d["stars"],
        watchers=d["watchers"],
        forks=d["forks"],
        cloud_detected=d["cloud_detected"],
        cloud_signals=d["cloud_signals"],
        ai_ml_detected=d["ai_ml_detected"],
        ai_ml_signals=d["ai_ml_signals"],
        has_ci_cd=d["has_ci_cd"],
        ci_cd_workflows=d["ci_cd_workflows"],
        deployments_count=d["deployments_count"],
        created_at=_parse_datetime(d["created_at"]),
        updated_at=_parse_datetime(d["updated_at"]),
        size_kb=d["size_kb"],
    )


def _dict_to_person_metrics(d: dict) -> PersonMetrics:
    return PersonMetrics(
        repo_full_name=d["repo_full_name"],
        login=d.get("login"),
        name=d.get("name"),
        num_commits=d["num_commits"],
        additions=d["additions"],
        deletions=d["deletions"],
        avg_additions_per_commit=d["avg_additions_per_commit"],
        avg_deletions_per_commit=d["avg_deletions_per_commit"],
    )


def _dict_to_temporal_metrics(d: dict | None) -> TemporalMetrics | None:
    if d is None:
        return None
    return TemporalMetrics(
        repo_full_name=d["repo_full_name"],
        pr_count_total=d["pr_count_total"],
        pr_count_merged=d["pr_count_merged"],
        pr_count_open=d["pr_count_open"],
        pr_count_closed_unmerged=d["pr_count_closed_unmerged"],
        prs=[
            PRRecord(
                number=p["number"],
                title=p["title"],
                state=p["state"],
                author_login=p.get("author_login"),
                created_at=_parse_datetime(p["created_at"]),
                merged_at=_parse_datetime(p.get("merged_at")),
                closed_at=_parse_datetime(p.get("closed_at")),
            )
            for p in d["prs"]
        ],
        tag_count=d["tag_count"],
        tags=[
            TagRecord(
                name=t["name"],
                commit_sha=t["commit_sha"],
                date=_parse_datetime(t.get("date")),
            )
            for t in d["tags"]
        ],
        release_count=d["release_count"],
        releases=[
            ReleaseRecord(
                tag_name=r["tag_name"],
                name=r.get("name"),
                created_at=_parse_datetime(r["created_at"]),
                is_prerelease=r["is_prerelease"],
            )
            for r in d["releases"]
        ],
    )


def _dict_to_chaoss_metrics(d: dict | None) -> ChaossMetrics | None:
    if d is None:
        return None
    return ChaossMetrics(
        repo_full_name=d["repo_full_name"],
        weekly_commits=d["weekly_commits"],
        change_request_acceptance_ratio=d.get("change_request_acceptance_ratio"),
        bus_factor=d.get("bus_factor"),
        contribution_types=d["contribution_types"],
        organizational_diversity=d["organizational_diversity"],
        newcomer_friendly_labels=d["newcomer_friendly_labels"],
        total_labels=d["total_labels"],
        release_frequency_per_month=d.get("release_frequency_per_month"),
        fork_count=d["fork_count"],
        burstiness_cv=d.get("burstiness_cv"),
        burstiness_mean=d.get("burstiness_mean"),
        burstiness_std=d.get("burstiness_std"),
        defect_resolution_durations_days=d["defect_resolution_durations_days"],
        median_defect_resolution_days=d.get("median_defect_resolution_days"),
        osi_approved_license=d["osi_approved_license"],
        # New fields (with defaults for backward compatibility with old cache)
        elephant_factor=d.get("elephant_factor"),
        contributor_new_count=d.get("contributor_new_count", 0),
        contributor_casual_count=d.get("contributor_casual_count", 0),
        contributor_regular_count=d.get("contributor_regular_count", 0),
        median_time_to_first_response_issues_hours=d.get("median_time_to_first_response_issues_hours"),
        median_time_to_first_response_prs_hours=d.get("median_time_to_first_response_prs_hours"),
        time_to_first_response_issues_sample_size=d.get("time_to_first_response_issues_sample_size", 0),
        time_to_first_response_prs_sample_size=d.get("time_to_first_response_prs_sample_size", 0),
        readme_last_updated=_parse_datetime(d.get("readme_last_updated")),
        contributing_last_updated=_parse_datetime(d.get("contributing_last_updated")),
        stale_issue_ratio=d.get("stale_issue_ratio"),
        stale_issue_count=d.get("stale_issue_count", 0),
        open_issue_count=d.get("open_issue_count", 0),
        median_pr_review_turnaround_hours=d.get("median_pr_review_turnaround_hours"),
        avg_review_comments_per_pr=d.get("avg_review_comments_per_pr"),
        # HHI, Institutional Types, DORA (added in add_future_metrics branch)
        herfindahl_hirschman_index=d.get("herfindahl_hirschman_index"),
        contributor_org_types=d.get("contributor_org_types", {}),
        dora_deployment_frequency_per_month=d.get("dora_deployment_frequency_per_month"),
        dora_median_lead_time_days=d.get("dora_median_lead_time_days"),
        dora_change_failure_rate=d.get("dora_change_failure_rate"),
        # Core-Periphery Network Analysis
        core_contributor_count=d.get("core_contributor_count", 0),
        periphery_contributor_count=d.get("periphery_contributor_count", 0),
        core_periphery_ratio=d.get("core_periphery_ratio"),
        network_density=d.get("network_density"),
        avg_degree_centrality=d.get("avg_degree_centrality"),
        pr_review_edges=d.get("pr_review_edges", []),
    )


def _dict_to_repository_data(d: dict) -> RepositoryData:
    """Reconstruct a RepositoryData dataclass from a JSON-loaded dict."""
    return RepositoryData(
        repo_metrics=_dict_to_repo_metrics(d["repo_metrics"]),
        person_metrics=[_dict_to_person_metrics(p) for p in d["person_metrics"]],
        temporal_metrics=_dict_to_temporal_metrics(d.get("temporal_metrics")),
        chaoss_metrics=_dict_to_chaoss_metrics(d.get("chaoss_metrics")),
        crawled_at=_parse_datetime(d.get("crawled_at")),
        core_periphery_contributors=[
            CorePeripheryContributor(
                repo_full_name=c["repo_full_name"],
                login=c["login"],
                degree_centrality=c["degree_centrality"],
                betweenness_centrality=c["betweenness_centrality"],
                classification=c["classification"],
                num_collaborators=c["num_collaborators"],
            )
            for c in d.get("core_periphery_contributors", [])
        ],
    )


# --- Public API ---


def is_cached(slug: str, output_dir: str) -> bool:
    """Check if a cached result exists for the given repository slug."""
    path = Path(output_dir) / _slug_to_filename(slug)
    return path.exists()


def save_repo_cache(data: RepositoryData, output_dir: str) -> None:
    """Save a single repository's data as a JSON cache file."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    filename = _slug_to_filename(data.repo_metrics.full_name)
    filepath = out / filename

    payload = dataclasses.asdict(data)
    with open(filepath, "w") as f:
        json.dump(payload, f, indent=2, cls=_DateTimeEncoder)
    logger.info("Cached %s → %s", data.repo_metrics.full_name, filename)


def load_repo_cache(slug: str, output_dir: str) -> RepositoryData | None:
    """Load a single repository's data from the JSON cache file."""
    filepath = Path(output_dir) / _slug_to_filename(slug)
    if not filepath.exists():
        return None
    try:
        with open(filepath) as f:
            raw = json.load(f)
        return _dict_to_repository_data(raw)
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.warning("Corrupt cache file %s, will re-crawl: %s", filepath.name, e)
        return None


def load_all_cached(output_dir: str) -> list[RepositoryData]:
    """Load all cached repository data files from the output directory."""
    out = Path(output_dir)
    if not out.exists():
        return []

    results: list[RepositoryData] = []
    for filepath in sorted(out.glob("*_data.json")):
        if filepath.name == "full_results.json":
            continue
        try:
            with open(filepath) as f:
                raw = json.load(f)
            results.append(_dict_to_repository_data(raw))
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning("Skipping corrupt cache file %s: %s", filepath.name, e)
    return results
