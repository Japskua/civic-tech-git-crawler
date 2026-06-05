"""Analyze CHAOSS summary metrics for a dataset snapshot.

Usage:
    uv run python scripts/analyse_chaoss_summary.py [chaoss-summary-csv]
    uv run python scripts/analyse_chaoss_summary.py --export-contributors [snapshot-dir]
    uv run python scripts/analyse_chaoss_summary.py --export-unclassified [snapshot-dir]
    uv run python scripts/analyse_chaoss_summary.py --analyze-project-size [snapshot-dir]
    uv run python scripts/analyse_chaoss_summary.py --analyze-theme-clusters [snapshot-dir]
    uv run python scripts/analyse_chaoss_summary.py --analyze-theme-kmodes [snapshot-dir]
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SNAPSHOT = ROOT / "datasets" / "2026_05"
DEFAULT_CSV = DEFAULT_SNAPSHOT / "chaoss_summary.csv"
CRAWL_DATE = pd.Timestamp("2026-05-24", tz="UTC")
CONTRIBUTOR_RELATIONSHIP_PAIRS = [
    ("total_commits", "active_weeks"),
    ("total_commits", "degree_centrality"),
    ("active_weeks", "duration_days"),
    ("activity_ratio", "avg_commits_per_active_week"),
    ("repos_contributed_to", "total_commits"),
    ("repos_contributed_to", "active_weeks"),
    ("num_collaborators", "degree_centrality"),
    ("duration_days", "degree_centrality"),
]
CONTRIBUTOR_COLUMNS = [
    "repo_full_name",
    "contributor_id",
    "login",
    "name",
    "email",
    "first_commit_date",
    "last_commit_date",
    "duration_days",
    "total_commits",
    "active_weeks",
    "total_weeks_span",
    "activity_ratio",
    "status",
    "departed_weeks_ago",
    "avg_commits_per_active_week",
]
PROJECT_SIZE_METRICS = [
    "num_developers",
    "total_commits",
    "age_years",
    "mean_weekly_commits",
    "median_weekly_commits",
    "active_weeks",
    "bus_factor_no_bots",
    "hhi_no_bots",
    "top_10_percent_contributors",
    "burstiness_cv",
    "stale_issue_ratio",
    "health_percentage",
    "stars",
]
PROJECT_SIZE_SENSITIVITY_METRICS = [
    "num_developers",
    "age_years",
    "mean_weekly_commits",
    "bus_factor_no_bots",
    "hhi_no_bots",
    "burstiness_cv",
    "stale_issue_ratio",
]
THEME_CLUSTER_METRICS = [
    "num_developers",
    "total_commits",
    "age_years",
    "mean_weekly_commits",
    "median_weekly_commits",
    "active_weeks",
    "bus_factor_no_bots",
    "hhi_no_bots",
    "top_10_percent_contributors",
    "burstiness_cv",
    "stale_issue_ratio",
    "health_percentage",
    "stars",
    "forks",
    "size_kb",
    "deployments_count",
    "core_periphery_ratio",
    "network_density",
    "avg_degree_centrality",
]
LOG_CLUSTER_METRICS = {
    "num_developers",
    "total_commits",
    "mean_weekly_commits",
    "median_weekly_commits",
    "active_weeks",
    "stars",
    "forks",
    "size_kb",
    "deployments_count",
}
KMODES_CATEGORICAL_COLUMNS = [
    "primary_language",
    "license_spdx",
    "is_osi_approved",
    "has_contributing",
    "has_code_of_conduct",
    "has_governance",
    "has_issue_template",
    "has_pr_template",
    "cloud_detected",
    "ai_ml_detected",
    "has_ci_cd",
]
KMODES_BIN_METRICS = [
    "num_developers",
    "total_commits",
    "age_years",
    "median_weekly_commits",
    "bus_factor_no_bots",
    "hhi_no_bots",
    "burstiness_cv",
    "stale_issue_ratio",
    "health_percentage",
    "stars",
    "size_kb",
    "deployments_count",
]


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Clean column names that may come from UTF-8-BOM spreadsheet exports."""
    df = df.copy()
    df.columns = [str(col).lstrip("\ufeff").strip() for col in df.columns]
    return df


def _load_theme_project_metrics(
    snapshot: Path,
    theme_csv: Path | None = None,
) -> tuple[pd.DataFrame, str, Path]:
    theme_csv = theme_csv or snapshot / "repo_metrics_with_theme.csv"
    base_repo_metrics = _normalise_columns(pd.read_csv(snapshot / "repo_metrics.csv"))
    theme_data = _normalise_columns(pd.read_csv(theme_csv))
    chaoss = _normalise_columns(pd.read_csv(snapshot / "chaoss_summary.csv")).rename(
        columns={"repo_full_name": "full_name"}
    )
    weekly = pd.read_csv(snapshot / "contributor_weekly_activity.csv")

    theme_columns = [col for col in theme_data.columns if col.lower() == "theme"]
    if not theme_columns:
        raise ValueError(f"No Theme column found in {theme_csv}")
    theme_col = theme_columns[0]
    if "full_name" not in theme_data.columns:
        raise ValueError(f"No full_name column found in {theme_csv}")

    repo_metrics = base_repo_metrics.merge(
        theme_data[["full_name", theme_col]],
        on="full_name",
        how="left",
    )
    df = repo_metrics.merge(chaoss, on="full_name", how="left")
    df["first_commit_date"] = pd.to_datetime(df["first_commit_date"], utc=True)
    df["age_years"] = (CRAWL_DATE - df["first_commit_date"]).dt.days / 365.25

    repo_week = (
        weekly.groupby(["repo_full_name", "week_start"], as_index=False)["commits"]
        .sum()
        .rename(columns={"repo_full_name": "full_name"})
    )
    weekly_summary = (
        repo_week.groupby("full_name", as_index=False)
        .agg(
            mean_weekly_commits=("commits", "mean"),
            median_weekly_commits=("commits", "median"),
            active_weeks=("week_start", "nunique"),
        )
    )
    df = df.merge(weekly_summary, on="full_name", how="left")
    df[theme_col] = df[theme_col].fillna("Unclassified").astype(str).str.strip()
    df.loc[df[theme_col].eq(""), theme_col] = "Unclassified"
    return df, theme_col, theme_csv


def export_contributor_lifecycles_from_json(snapshot: Path, output_csv: Path) -> pd.DataFrame:
    """Export contributor first/last commit records from per-project data.json files."""
    rows = []
    for data_json in sorted(snapshot.glob("*/data.json")):
        with data_json.open(encoding="utf-8") as f:
            data = json.load(f)
        commit_history = data.get("commit_history") or {}
        repo = commit_history.get("repo_full_name")
        for lifecycle in commit_history.get("contributor_lifecycles") or []:
            row = {col: lifecycle.get(col) for col in CONTRIBUTOR_COLUMNS}
            row["repo_full_name"] = row["repo_full_name"] or repo
            rows.append(row)

    df = pd.DataFrame(rows, columns=CONTRIBUTOR_COLUMNS)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    return df


def export_unclassified_contributors(snapshot: Path, output_csv: Path) -> pd.DataFrame:
    """Export lifecycle contributors that have no matching is_bot value in person_metrics."""
    lifecycles_path = snapshot / "contributors_from_data_json.csv"
    if lifecycles_path.exists():
        lifecycles = pd.read_csv(lifecycles_path)
    else:
        lifecycles = export_contributor_lifecycles_from_json(snapshot, lifecycles_path)

    person_metrics = pd.read_csv(
        snapshot / "person_metrics.csv",
        usecols=["repo_full_name", "login", "is_bot"],
    ).drop_duplicates(subset=["repo_full_name", "login"])

    merged = lifecycles.merge(
        person_metrics,
        on=["repo_full_name", "login"],
        how="left",
        indicator=True,
    )
    unclassified = merged[merged["is_bot"].isna()].drop(columns=["is_bot", "_merge"])
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    unclassified.to_csv(output_csv, index=False)
    return unclassified


def analyze_contributor_relationships(snapshot: Path, include_bots: bool = False) -> pd.DataFrame:
    """Analyze links between contributor lifecycle, effort, and network attributes."""
    lifecycles = pd.read_csv(snapshot / "contributor_lifecycles.csv")
    person_metrics = pd.read_csv(snapshot / "person_metrics.csv")
    core_periphery = pd.read_csv(snapshot / "core_periphery.csv")
    cross_project_overlap = pd.read_csv(snapshot / "cross_project_overlap.csv")

    person_cols = [
        "repo_full_name",
        "login",
        "is_bot",
        "additions",
        "deletions",
        "avg_additions_per_commit",
        "avg_deletions_per_commit",
    ]
    network_cols = [
        "repo_full_name",
        "login",
        "degree_centrality",
        "betweenness_centrality",
        "classification",
        "num_collaborators",
    ]

    df = lifecycles.merge(
        person_metrics[person_cols].drop_duplicates(subset=["repo_full_name", "login"]),
        on=["repo_full_name", "login"],
        how="left",
    )
    df = df.merge(
        core_periphery[network_cols].drop_duplicates(subset=["repo_full_name", "login"]),
        on=["repo_full_name", "login"],
        how="left",
    )
    df = df.merge(cross_project_overlap, on="login", how="left")

    analyzed = df if include_bots else df[df["is_bot"].eq(False)].copy()
    label = "all classified contributors" if include_bots else "known human contributors"

    print(f"Contributor relationship analysis: {snapshot}")
    print(f"Rows: {len(analyzed)} {label}")
    print(f"Repositories: {analyzed['repo_full_name'].nunique() if not analyzed.empty else 0}")
    print(f"Unique contributors: {analyzed['login'].nunique() if not analyzed.empty else 0}")

    if analyzed.empty:
        return analyzed

    print("\nStatus counts:")
    print(analyzed["status"].value_counts(dropna=False).to_string())

    if {"classification", "status"}.issubset(analyzed.columns):
        table = pd.crosstab(
            analyzed["classification"],
            analyzed["status"],
            normalize="index",
        ).round(3)
        print("\nNetwork classification by lifecycle status (row proportions):")
        print(table.to_string())

    median_columns = [
        "total_commits",
        "duration_days",
        "active_weeks",
        "activity_ratio",
        "degree_centrality",
        "num_collaborators",
        "repos_contributed_to",
    ]
    available_medians = [col for col in median_columns if col in analyzed.columns]

    if "status" in analyzed.columns:
        print("\nMedian attributes by lifecycle status:")
        print(
            analyzed.groupby("status")[available_medians]
            .median(numeric_only=True)
            .round(3)
            .to_string()
        )

    if "classification" in analyzed.columns:
        print("\nMedian attributes by network classification:")
        print(
            analyzed.groupby("classification")[available_medians]
            .median(numeric_only=True)
            .round(3)
            .to_string()
        )

    print("\nSpearman correlations:")
    for left, right in CONTRIBUTOR_RELATIONSHIP_PAIRS:
        if left not in analyzed.columns or right not in analyzed.columns:
            continue
        subset = analyzed[[left, right]].dropna()
        if len(subset) < 3:
            continue
        rho, p_value = stats.spearmanr(subset[left], subset[right])
        print(f"{left} vs {right}: n={len(subset)} rho={rho:.3f} p={p_value:.2g}")

    return analyzed


def analyze_project_size_split(snapshot: Path) -> pd.DataFrame:
    """Compare small and big projects across activity and sustainability metrics."""
    repo_metrics = pd.read_csv(snapshot / "repo_metrics.csv")
    chaoss = pd.read_csv(snapshot / "chaoss_summary.csv").rename(
        columns={"repo_full_name": "full_name"}
    )
    weekly = pd.read_csv(snapshot / "contributor_weekly_activity.csv")

    df = repo_metrics.merge(chaoss, on="full_name", how="left")
    df["first_commit_date"] = pd.to_datetime(df["first_commit_date"], utc=True)
    df["age_years"] = (CRAWL_DATE - df["first_commit_date"]).dt.days / 365.25

    repo_week = (
        weekly.groupby(["repo_full_name", "week_start"], as_index=False)["commits"]
        .sum()
        .rename(columns={"repo_full_name": "full_name"})
    )
    weekly_summary = (
        repo_week.groupby("full_name", as_index=False)
        .agg(
            mean_weekly_commits=("commits", "mean"),
            median_weekly_commits=("commits", "median"),
            active_weeks=("week_start", "nunique"),
        )
    )
    df = df.merge(weekly_summary, on="full_name", how="left")

    median_developers = df["num_developers"].median()
    df["size_group"] = "big"
    df.loc[df["num_developers"] <= median_developers, "size_group"] = "small"

    metrics = [metric for metric in PROJECT_SIZE_METRICS if metric in df.columns]
    print(f"Project size analysis: {snapshot}")
    print(
        f"Split: small <= median num_developers ({median_developers:.0f}); "
        "big > median"
    )
    print(df["size_group"].value_counts().to_string())

    print("\nMedians by group:")
    print(
        df.groupby("size_group")[metrics]
        .median(numeric_only=True)
        .round(3)
        .T.to_string()
    )

    print("\nMann-Whitney tests:")
    for metric in metrics:
        small = df[df["size_group"] == "small"][metric].dropna()
        big = df[df["size_group"] == "big"][metric].dropna()
        if len(small) < 2 or len(big) < 2:
            continue
        _, p_value = stats.mannwhitneyu(small, big, alternative="two-sided")
        print(
            f"{metric}: small_n={len(small)} big_n={len(big)} "
            f"p={p_value:.4g} small_med={small.median():.3g} "
            f"big_med={big.median():.3g}"
        )

    median_commits = df["total_commits"].median()
    df["commit_size_group"] = "big_commit"
    df.loc[df["total_commits"] <= median_commits, "commit_size_group"] = "small_commit"
    sensitivity_metrics = [
        metric for metric in PROJECT_SIZE_SENSITIVITY_METRICS if metric in df.columns
    ]

    print(
        f"\nSensitivity split: small <= median total_commits "
        f"({median_commits:.0f}); big > median"
    )
    for metric in sensitivity_metrics:
        small = df[df["commit_size_group"] == "small_commit"][metric].dropna()
        big = df[df["commit_size_group"] == "big_commit"][metric].dropna()
        if len(small) < 2 or len(big) < 2:
            continue
        _, p_value = stats.mannwhitneyu(small, big, alternative="two-sided")
        print(
            f"{metric}: p={p_value:.4g} small_med={small.median():.3g} "
            f"big_med={big.median():.3g}"
        )

    return df


def analyze_theme_metric_clusters(
    snapshot: Path,
    theme_csv: Path | None = None,
    n_clusters: int = 4,
    output_csv: Path | None = None,
) -> pd.DataFrame:
    """Cluster repositories by metrics and summarize how clusters relate to themes."""
    df, theme_col, theme_csv = _load_theme_project_metrics(snapshot, theme_csv)

    metrics = [metric for metric in THEME_CLUSTER_METRICS if metric in df.columns]
    numeric = df[metrics].apply(pd.to_numeric, errors="coerce")
    usable_metrics = [
        metric for metric in metrics
        if numeric[metric].notna().sum() >= 3 and numeric[metric].nunique(dropna=True) > 1
    ]
    if len(usable_metrics) < 2:
        raise ValueError("Need at least two numeric metrics with variation for clustering.")

    cluster_source = numeric[usable_metrics].copy()
    for metric in usable_metrics:
        if metric in LOG_CLUSTER_METRICS:
            values = cluster_source[metric]
            if values.dropna().ge(0).all():
                cluster_source[metric] = np.log1p(values)

    cluster_source = cluster_source.fillna(cluster_source.median(numeric_only=True))
    std = cluster_source.std(ddof=0).replace(0, np.nan)
    scaled = ((cluster_source - cluster_source.mean()) / std).dropna(axis=1)
    if scaled.shape[1] < 2:
        raise ValueError("Need at least two standardizable metrics for clustering.")

    n_clusters = max(2, min(n_clusters, len(df)))
    linked = linkage(scaled.to_numpy(), method="ward")
    df["metric_cluster"] = fcluster(linked, t=n_clusters, criterion="maxclust")

    print(f"Theme/metric clustering analysis: {snapshot}")
    print(f"Theme file: {theme_csv}")
    print(f"Rows: {len(df)} repositories")
    print(f"Clusters: {n_clusters}")
    print("Metrics used:")
    print(", ".join(scaled.columns))

    print("\nTheme counts:")
    print(df[theme_col].value_counts(dropna=False).to_string())

    print("\nCluster sizes:")
    print(df["metric_cluster"].value_counts().sort_index().to_string())

    print("\nThemes by metric cluster (counts):")
    print(pd.crosstab(df["metric_cluster"], df[theme_col]).to_string())

    print("\nThemes by metric cluster (row proportions):")
    print(pd.crosstab(df["metric_cluster"], df[theme_col], normalize="index").round(3).to_string())

    print("\nCluster metric medians:")
    print(
        df.groupby("metric_cluster")[usable_metrics]
        .median(numeric_only=True)
        .round(3)
        .T.to_string()
    )

    print("\nTheme metric medians:")
    print(
        df.groupby(theme_col)[usable_metrics]
        .median(numeric_only=True)
        .round(3)
        .T.to_string()
    )

    print("\nTheme differences across metrics (Kruskal-Wallis, themes with n>=2):")
    for metric in usable_metrics:
        groups = [
            group[metric].dropna()
            for _, group in df.groupby(theme_col)
            if group[metric].dropna().size >= 2
        ]
        if len(groups) < 2:
            continue
        _, p_value = stats.kruskal(*groups)
        print(f"{metric}: groups={len(groups)} p={p_value:.4g}")

    if output_csv:
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_csv, index=False)
        print(f"\nWrote clustered dataset to {output_csv}")

    return df


def _categorical_mode(values: list[str]) -> str:
    counts = Counter(values)
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _fit_k_modes(
    data: np.ndarray,
    n_clusters: int,
    max_iter: int = 100,
    n_init: int = 20,
    random_state: int = 42,
) -> tuple[np.ndarray, np.ndarray, int]:
    rng = np.random.default_rng(random_state)
    n_rows = data.shape[0]
    best_labels = None
    best_modes = None
    best_cost = np.inf

    for _ in range(n_init):
        initial_idx = rng.choice(n_rows, size=n_clusters, replace=False)
        modes = data[initial_idx].copy()
        labels = np.zeros(n_rows, dtype=int)

        for _ in range(max_iter):
            distances = (data[:, None, :] != modes[None, :, :]).sum(axis=2)
            new_labels = distances.argmin(axis=1)

            for cluster_id in range(n_clusters):
                if np.any(new_labels == cluster_id):
                    continue
                farthest_idx = distances.min(axis=1).argmax()
                new_labels[farthest_idx] = cluster_id

            new_modes = modes.copy()
            for cluster_id in range(n_clusters):
                cluster_data = data[new_labels == cluster_id]
                for col_idx in range(data.shape[1]):
                    new_modes[cluster_id, col_idx] = _categorical_mode(
                        cluster_data[:, col_idx].tolist()
                    )

            if np.array_equal(labels, new_labels) and np.array_equal(modes, new_modes):
                labels = new_labels
                modes = new_modes
                break
            labels = new_labels
            modes = new_modes

        cost = int((data != modes[labels]).sum())
        if cost < best_cost:
            best_cost = cost
            best_labels = labels.copy()
            best_modes = modes.copy()

    return best_labels + 1, best_modes, int(best_cost)


def _binned_metric(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    labels = ["low", "medium", "high"]
    result = pd.Series("missing", index=series.index, dtype=object)
    valid = numeric.dropna()
    if valid.nunique() < 2:
        result.loc[valid.index] = "constant"
        return result

    bins = min(3, valid.nunique())
    ranked = valid.rank(method="first")
    binned = pd.qcut(ranked, q=bins, labels=labels[:bins])
    result.loc[valid.index] = binned.astype(str)
    return result


def analyze_theme_k_modes(
    snapshot: Path,
    theme_csv: Path | None = None,
    n_clusters: int = 4,
    output_csv: Path | None = None,
) -> pd.DataFrame:
    """Cluster categorical and discretized metric attributes, then compare to themes."""
    df, theme_col, theme_csv = _load_theme_project_metrics(snapshot, theme_csv)
    feature_frame = pd.DataFrame(index=df.index)

    categorical_columns = [
        col for col in KMODES_CATEGORICAL_COLUMNS
        if col in df.columns and df[col].nunique(dropna=True) > 1
    ]
    for col in categorical_columns:
        feature_frame[col] = df[col].fillna("missing").astype(str)

    metric_columns = [
        col for col in KMODES_BIN_METRICS
        if col in df.columns and pd.to_numeric(df[col], errors="coerce").nunique(dropna=True) > 1
    ]
    for col in metric_columns:
        feature_frame[f"{col}_bin"] = _binned_metric(df[col])

    if feature_frame.shape[1] < 2:
        raise ValueError("Need at least two categorical or binned metric features for k-modes.")

    n_clusters = max(2, min(n_clusters, len(df)))
    labels, modes, cost = _fit_k_modes(
        feature_frame.to_numpy(dtype=str),
        n_clusters=n_clusters,
    )
    df["kmodes_cluster"] = labels

    modes_df = pd.DataFrame(modes, columns=feature_frame.columns)
    modes_df.insert(0, "kmodes_cluster", range(1, n_clusters + 1))

    print(f"Theme k-modes analysis: {snapshot}")
    print(f"Theme file: {theme_csv}")
    print(f"Rows: {len(df)} repositories")
    print(f"Clusters: {n_clusters}")
    print(f"K-modes cost: {cost}")
    print("Features used:")
    print(", ".join(feature_frame.columns))

    print("\nCluster sizes:")
    print(df["kmodes_cluster"].value_counts().sort_index().to_string())

    print("\nThemes by k-modes cluster (counts):")
    theme_cluster_counts = pd.crosstab(df["kmodes_cluster"], df[theme_col])
    print(theme_cluster_counts.to_string())

    print("\nThemes by k-modes cluster (row proportions):")
    print(pd.crosstab(df["kmodes_cluster"], df[theme_col], normalize="index").round(3).to_string())

    if theme_cluster_counts.shape[0] > 1 and theme_cluster_counts.shape[1] > 1:
        chi2, p_value, _, _ = stats.chi2_contingency(theme_cluster_counts)
        print(f"\nTheme vs k-modes cluster chi-square: chi2={chi2:.3f} p={p_value:.4g}")

    print("\nCluster modes:")
    print(modes_df.to_string(index=False))

    print("\nNumeric metric medians by k-modes cluster:")
    available_metrics = [col for col in KMODES_BIN_METRICS if col in df.columns]
    print(
        df.groupby("kmodes_cluster")[available_metrics]
        .median(numeric_only=True)
        .round(3)
        .T.to_string()
    )

    if output_csv:
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_csv, index=False)
        print(f"\nWrote k-modes clustered dataset to {output_csv}")

    return df


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=str(DEFAULT_CSV))
    parser.add_argument(
        "--export-contributors",
        action="store_true",
        help="Walk snapshot project folders and export contributor lifecycle records.",
    )
    parser.add_argument(
        "--export-unclassified",
        action="store_true",
        help="Export lifecycle contributors with no matching is_bot value in person_metrics.",
    )
    parser.add_argument(
        "--analyze-contributors",
        action="store_true",
        help="Analyze links between contributor lifecycle, effort, and network attributes.",
    )
    parser.add_argument(
        "--analyze-project-size",
        action="store_true",
        help="Compare small and big projects by activity and sustainability metrics.",
    )
    parser.add_argument(
        "--analyze-theme-clusters",
        action="store_true",
        help="Cluster repositories by metrics and compare the clusters with project themes.",
    )
    parser.add_argument(
        "--analyze-theme-kmodes",
        action="store_true",
        help="Run k-modes on categorical and binned metric features, then compare clusters with themes.",
    )
    parser.add_argument(
        "--theme-csv",
        default=None,
        help="CSV with full_name and Theme columns. Defaults to snapshot/repo_metrics_with_theme.csv.",
    )
    parser.add_argument(
        "--clusters",
        type=int,
        default=4,
        help="Number of metric clusters for --analyze-theme-clusters.",
    )
    parser.add_argument(
        "--include-bots",
        action="store_true",
        help="Include bot contributors in --analyze-contributors output.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output CSV path for --export-contributors.",
    )
    args = parser.parse_args()

    if args.export_contributors:
        snapshot = Path(args.path).resolve()
        if snapshot.is_file():
            snapshot = snapshot.parent
        output_csv = (
            Path(args.output).resolve()
            if args.output
            else snapshot / "contributors_from_data_json.csv"
        )
        df = export_contributor_lifecycles_from_json(snapshot, output_csv)
        print(f"Exported {len(df)} contributor lifecycle records to {output_csv}")
        print(f"Repositories: {df['repo_full_name'].nunique() if not df.empty else 0}")
        return 0

    if args.export_unclassified:
        snapshot = Path(args.path).resolve()
        if snapshot.is_file():
            snapshot = snapshot.parent
        output_csv = (
            Path(args.output).resolve()
            if args.output
            else snapshot / "unclassified_contributors.csv"
        )
        df = export_unclassified_contributors(snapshot, output_csv)
        commits = pd.to_numeric(df["total_commits"], errors="coerce").fillna(0)
        print(f"Exported {len(df)} unclassified contributor lifecycle records to {output_csv}")
        print(f"Repositories: {df['repo_full_name'].nunique() if not df.empty else 0}")
        print(f"Total commits: {int(commits.sum())}")
        return 0

    if args.analyze_contributors:
        snapshot = Path(args.path).resolve()
        if snapshot.is_file():
            snapshot = snapshot.parent
        analyze_contributor_relationships(snapshot, include_bots=args.include_bots)
        return 0

    if args.analyze_project_size:
        snapshot = Path(args.path).resolve()
        if snapshot.is_file():
            snapshot = snapshot.parent
        analyze_project_size_split(snapshot)
        return 0

    if args.analyze_theme_clusters:
        snapshot = Path(args.path).resolve()
        if snapshot.is_file():
            snapshot = snapshot.parent
        output_csv = Path(args.output).resolve() if args.output else None
        theme_csv = Path(args.theme_csv).resolve() if args.theme_csv else None
        analyze_theme_metric_clusters(
            snapshot,
            theme_csv=theme_csv,
            n_clusters=args.clusters,
            output_csv=output_csv,
        )
        return 0

    if args.analyze_theme_kmodes:
        snapshot = Path(args.path).resolve()
        if snapshot.is_file():
            snapshot = snapshot.parent
        output_csv = Path(args.output).resolve() if args.output else None
        theme_csv = Path(args.theme_csv).resolve() if args.theme_csv else None
        analyze_theme_k_modes(
            snapshot,
            theme_csv=theme_csv,
            n_clusters=args.clusters,
            output_csv=output_csv,
        )
        return 0

    csv_path = Path(args.path).resolve()
    df = pd.read_csv(csv_path)

    hhi = df["herfindahl_hirschman_index"].dropna()
    hhi_no_bots = df["hhi_no_bots"].dropna()

    print(f"CHAOSS summary: {csv_path}")
    print(f"Repositories: {len(df)}")
    print(f"Median HHI: {hhi.median():.0f} (n={len(hhi)})")
    print(f"Median HHI, no bots: {hhi_no_bots.median():.0f} (n={len(hhi_no_bots)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
