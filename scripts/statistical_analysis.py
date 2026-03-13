#!/usr/bin/env python3
"""Statistical analysis of civic tech crawler output.

Reads CSV files from the crawler's output directory and computes:
- Descriptive statistics for key metrics
- Spearman rank correlations between metrics
- Normality tests (Shapiro-Wilk)
- Group comparisons (Mann-Whitney U)
- Effect sizes (Cliff's delta)

Usage:
    python scripts/statistical_analysis.py [output_dir]

Default output_dir is ./output/
Results are written to output_dir/statistical_analysis/
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


def cliffs_delta(x: np.ndarray, y: np.ndarray) -> tuple[float, str]:
    """Compute Cliff's delta effect size (non-parametric).

    Returns (delta, magnitude) where magnitude is one of:
    negligible, small, medium, large.
    """
    n_x, n_y = len(x), len(y)
    if n_x == 0 or n_y == 0:
        return 0.0, "negligible"
    more = sum(1 for xi in x for yi in y if xi > yi)
    less = sum(1 for xi in x for yi in y if xi < yi)
    delta = (more - less) / (n_x * n_y)
    # Thresholds from Romano et al. (2006)
    abs_d = abs(delta)
    if abs_d < 0.147:
        magnitude = "negligible"
    elif abs_d < 0.33:
        magnitude = "small"
    elif abs_d < 0.474:
        magnitude = "medium"
    else:
        magnitude = "large"
    return round(delta, 4), magnitude


def load_data(output_dir: Path) -> dict[str, pd.DataFrame]:
    """Load all CSV files from the output directory."""
    dfs = {}
    for csv_file in sorted(output_dir.glob("*.csv")):
        dfs[csv_file.stem] = pd.read_csv(csv_file)
    return dfs


def compute_descriptive_stats(repo_metrics: pd.DataFrame, chaoss: pd.DataFrame) -> pd.DataFrame:
    """Compute descriptive statistics for key metrics."""
    # Merge repo and chaoss metrics
    merged = repo_metrics.merge(chaoss, left_on="full_name", right_on="repo_full_name", how="inner")

    numeric_cols = [
        "total_commits", "num_developers", "stars", "forks", "health_percentage",
        "bus_factor", "bus_factor_no_bots", "burstiness_cv",
        "elephant_factor", "elephant_factor_no_bots",
        "herfindahl_hirschman_index", "hhi_no_bots", "hhi_known_orgs_only",
        "stale_issue_ratio", "change_request_acceptance_ratio",
        "median_time_to_first_response_issues_hours",
        "median_time_to_first_response_prs_hours",
        "median_pr_review_turnaround_hours", "avg_review_comments_per_pr",
        "core_contributor_count", "periphery_contributor_count",
        "network_density", "bot_contributor_count", "bot_commit_count",
        "unknown_org_contributor_count",
    ]

    available_cols = [c for c in numeric_cols if c in merged.columns]
    desc = merged[available_cols].describe()
    # Add IQR
    q1 = merged[available_cols].quantile(0.25)
    q3 = merged[available_cols].quantile(0.75)
    iqr = q3 - q1
    desc.loc["IQR"] = iqr
    return desc.T


def compute_correlations(repo_metrics: pd.DataFrame, chaoss: pd.DataFrame) -> pd.DataFrame:
    """Compute Spearman rank correlations between key metrics."""
    merged = repo_metrics.merge(chaoss, left_on="full_name", right_on="repo_full_name", how="inner")

    # Compute project age in years
    if "created_at" in merged.columns:
        merged["age_years"] = (
            pd.to_datetime("now", utc=True) - pd.to_datetime(merged["created_at"], utc=True)
        ).dt.days / 365.25

    correlation_vars = [
        "age_years", "num_developers", "total_commits", "stars", "forks",
        "bus_factor", "bus_factor_no_bots", "burstiness_cv",
        "herfindahl_hirschman_index", "hhi_no_bots",
        "stale_issue_ratio", "health_percentage",
        "change_request_acceptance_ratio",
        "median_time_to_first_response_issues_hours",
        "median_pr_review_turnaround_hours",
        "core_contributor_count", "network_density",
    ]
    available = [c for c in correlation_vars if c in merged.columns]
    subset = merged[available].dropna(axis=1, how="all")

    n = len(subset.columns)
    corr_matrix = pd.DataFrame(np.zeros((n, n)), index=subset.columns, columns=subset.columns)
    p_matrix = pd.DataFrame(np.ones((n, n)), index=subset.columns, columns=subset.columns)

    for i, col_a in enumerate(subset.columns):
        for j, col_b in enumerate(subset.columns):
            if i == j:
                corr_matrix.iloc[i, j] = 1.0
                p_matrix.iloc[i, j] = 0.0
            elif i < j:
                valid = subset[[col_a, col_b]].dropna()
                if len(valid) >= 3:
                    rho, p = stats.spearmanr(valid[col_a], valid[col_b])
                    corr_matrix.iloc[i, j] = round(rho, 4)
                    corr_matrix.iloc[j, i] = round(rho, 4)
                    p_matrix.iloc[i, j] = round(p, 4)
                    p_matrix.iloc[j, i] = round(p, 4)

    return corr_matrix, p_matrix


def compute_normality_tests(repo_metrics: pd.DataFrame, chaoss: pd.DataFrame) -> pd.DataFrame:
    """Run Shapiro-Wilk normality tests on key metrics."""
    merged = repo_metrics.merge(chaoss, left_on="full_name", right_on="repo_full_name", how="inner")

    test_vars = [
        "total_commits", "num_developers", "bus_factor", "bus_factor_no_bots",
        "burstiness_cv", "herfindahl_hirschman_index", "hhi_no_bots",
        "stale_issue_ratio", "health_percentage",
    ]
    available = [c for c in test_vars if c in merged.columns]

    results = []
    for col in available:
        values = merged[col].dropna()
        if len(values) >= 3:
            stat, p = stats.shapiro(values)
            results.append({
                "metric": col,
                "n": len(values),
                "W_statistic": round(stat, 4),
                "p_value": round(p, 4),
                "normal": p > 0.05,
            })

    return pd.DataFrame(results)


def compute_group_comparisons(
    repo_metrics: pd.DataFrame,
    chaoss: pd.DataFrame,
) -> pd.DataFrame:
    """Compare metrics across groups using Mann-Whitney U."""
    merged = repo_metrics.merge(chaoss, left_on="full_name", right_on="repo_full_name", how="inner")

    comparisons = []

    # CI/CD vs no CI/CD
    if "has_ci_cd" in merged.columns:
        ci_group = merged[merged["has_ci_cd"] == True]  # noqa: E712
        no_ci_group = merged[merged["has_ci_cd"] == False]  # noqa: E712
        for metric in ["bus_factor", "bus_factor_no_bots", "stale_issue_ratio", "health_percentage"]:
            if metric in merged.columns:
                a = ci_group[metric].dropna().values
                b = no_ci_group[metric].dropna().values
                if len(a) >= 2 and len(b) >= 2:
                    u_stat, p = stats.mannwhitneyu(a, b, alternative="two-sided")
                    delta, mag = cliffs_delta(a, b)
                    comparisons.append({
                        "comparison": "CI/CD vs No CI/CD",
                        "metric": metric,
                        "group_a_n": len(a),
                        "group_b_n": len(b),
                        "group_a_median": round(np.median(a), 4),
                        "group_b_median": round(np.median(b), 4),
                        "U_statistic": round(u_stat, 4),
                        "p_value": round(p, 4),
                        "cliffs_delta": delta,
                        "effect_magnitude": mag,
                    })

    # Cloud vs no cloud
    if "cloud_detected" in merged.columns:
        cloud_group = merged[merged["cloud_detected"] == True]  # noqa: E712
        no_cloud_group = merged[merged["cloud_detected"] == False]  # noqa: E712
        for metric in ["total_commits", "num_developers", "bus_factor_no_bots"]:
            if metric in merged.columns:
                a = cloud_group[metric].dropna().values
                b = no_cloud_group[metric].dropna().values
                if len(a) >= 2 and len(b) >= 2:
                    u_stat, p = stats.mannwhitneyu(a, b, alternative="two-sided")
                    delta, mag = cliffs_delta(a, b)
                    comparisons.append({
                        "comparison": "Cloud vs No Cloud",
                        "metric": metric,
                        "group_a_n": len(a),
                        "group_b_n": len(b),
                        "group_a_median": round(np.median(a), 4),
                        "group_b_median": round(np.median(b), 4),
                        "U_statistic": round(u_stat, 4),
                        "p_value": round(p, 4),
                        "cliffs_delta": delta,
                        "effect_magnitude": mag,
                    })

    # AI/ML vs no AI/ML
    if "ai_ml_detected" in merged.columns:
        ai_group = merged[merged["ai_ml_detected"] == True]  # noqa: E712
        no_ai_group = merged[merged["ai_ml_detected"] == False]  # noqa: E712
        for metric in ["num_developers", "bus_factor_no_bots", "health_percentage"]:
            if metric in merged.columns:
                a = ai_group[metric].dropna().values
                b = no_ai_group[metric].dropna().values
                if len(a) >= 2 and len(b) >= 2:
                    u_stat, p = stats.mannwhitneyu(a, b, alternative="two-sided")
                    delta, mag = cliffs_delta(a, b)
                    comparisons.append({
                        "comparison": "AI/ML vs No AI/ML",
                        "metric": metric,
                        "group_a_n": len(a),
                        "group_b_n": len(b),
                        "group_a_median": round(np.median(a), 4),
                        "group_b_median": round(np.median(b), 4),
                        "U_statistic": round(u_stat, 4),
                        "p_value": round(p, 4),
                        "cliffs_delta": delta,
                        "effect_magnitude": mag,
                    })

    return pd.DataFrame(comparisons)


def compute_bot_impact(person_metrics: pd.DataFrame, chaoss: pd.DataFrame) -> pd.DataFrame:
    """Analyze the impact of bot filtering on metrics."""
    if "is_bot" not in person_metrics.columns:
        return pd.DataFrame()

    results = []
    for repo in chaoss["repo_full_name"].unique():
        pm = person_metrics[person_metrics["repo_full_name"] == repo]
        cm = chaoss[chaoss["repo_full_name"] == repo]
        if cm.empty:
            continue
        cm_row = cm.iloc[0]

        total_contributors = len(pm)
        bot_contributors = pm["is_bot"].sum() if "is_bot" in pm.columns else 0
        total_commits = pm["num_commits"].sum()
        bot_commits = pm[pm["is_bot"] == True]["num_commits"].sum() if "is_bot" in pm.columns else 0  # noqa: E712

        results.append({
            "repo_full_name": repo,
            "total_contributors": total_contributors,
            "bot_contributors": int(bot_contributors),
            "human_contributors": total_contributors - int(bot_contributors),
            "bot_commit_pct": round(bot_commits / total_commits * 100, 1) if total_commits > 0 else 0,
            "bus_factor": cm_row.get("bus_factor"),
            "bus_factor_no_bots": cm_row.get("bus_factor_no_bots"),
            "hhi": cm_row.get("herfindahl_hirschman_index"),
            "hhi_no_bots": cm_row.get("hhi_no_bots"),
            "hhi_known_orgs_only": cm_row.get("hhi_known_orgs_only"),
        })

    return pd.DataFrame(results)


def main():
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("./output")

    if not output_dir.exists():
        print(f"Error: output directory '{output_dir}' does not exist")
        sys.exit(1)

    print(f"Loading data from {output_dir}...")
    dfs = load_data(output_dir)

    repo_metrics = dfs.get("repo_metrics")
    chaoss = dfs.get("chaoss_summary")
    person_metrics = dfs.get("person_metrics")

    if repo_metrics is None or chaoss is None:
        print("Error: repo_metrics.csv and chaoss_summary.csv are required")
        sys.exit(1)

    results_dir = output_dir / "statistical_analysis"
    results_dir.mkdir(exist_ok=True)

    print(f"\nAnalyzing {len(repo_metrics)} repositories...\n")

    # 1. Descriptive statistics
    print("1. Computing descriptive statistics...")
    desc = compute_descriptive_stats(repo_metrics, chaoss)
    desc.to_csv(results_dir / "descriptive_statistics.csv")
    print(f"   Saved to {results_dir / 'descriptive_statistics.csv'}")
    print(desc[["count", "mean", "50%", "std", "IQR"]].to_string())
    print()

    # 2. Normality tests
    print("2. Running Shapiro-Wilk normality tests...")
    normality = compute_normality_tests(repo_metrics, chaoss)
    normality.to_csv(results_dir / "normality_tests.csv", index=False)
    print(f"   Saved to {results_dir / 'normality_tests.csv'}")
    print(normality.to_string(index=False))
    print()

    # 3. Spearman correlations
    print("3. Computing Spearman rank correlations...")
    corr_matrix, p_matrix = compute_correlations(repo_metrics, chaoss)
    corr_matrix.to_csv(results_dir / "spearman_correlations.csv")
    p_matrix.to_csv(results_dir / "spearman_p_values.csv")
    print(f"   Saved to {results_dir / 'spearman_correlations.csv'}")

    # Print significant correlations (p < 0.05)
    sig_pairs = []
    for i in range(len(corr_matrix)):
        for j in range(i + 1, len(corr_matrix)):
            p = p_matrix.iloc[i, j]
            rho = corr_matrix.iloc[i, j]
            if p < 0.05:
                sig_pairs.append({
                    "var_a": corr_matrix.index[i],
                    "var_b": corr_matrix.columns[j],
                    "rho": rho,
                    "p": p,
                })
    if sig_pairs:
        print("   Significant correlations (p < 0.05):")
        for sp in sorted(sig_pairs, key=lambda x: abs(x["rho"]), reverse=True):
            print(f"     {sp['var_a']} ~ {sp['var_b']}: ρ={sp['rho']:.3f}, p={sp['p']:.4f}")
    else:
        print("   No significant correlations found at p < 0.05")
    print()

    # 4. Group comparisons
    print("4. Running group comparisons (Mann-Whitney U)...")
    comparisons = compute_group_comparisons(repo_metrics, chaoss)
    if not comparisons.empty:
        comparisons.to_csv(results_dir / "group_comparisons.csv", index=False)
        print(f"   Saved to {results_dir / 'group_comparisons.csv'}")
        print(comparisons.to_string(index=False))
    else:
        print("   Insufficient data for group comparisons")
    print()

    # 5. Bot impact analysis
    if person_metrics is not None:
        print("5. Analyzing bot impact on metrics...")
        bot_impact = compute_bot_impact(person_metrics, chaoss)
        if not bot_impact.empty:
            bot_impact.to_csv(results_dir / "bot_impact.csv", index=False)
            print(f"   Saved to {results_dir / 'bot_impact.csv'}")
            print(bot_impact.to_string(index=False))
        print()

    print(f"All results saved to {results_dir}/")


if __name__ == "__main__":
    main()
