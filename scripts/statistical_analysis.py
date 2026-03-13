#!/usr/bin/env python3
"""Statistical analysis of civic tech crawler output.

Reads CSV files from the crawler's output directory and computes:
- Descriptive statistics for key metrics
- Spearman rank correlations between metrics (with FDR correction)
- Normality tests (Shapiro-Wilk)
- Group comparisons (Mann-Whitney U)
- Effect sizes (Cliff's delta)
- Wilcoxon signed-rank tests for bot impact (paired before/after)
- Project maturity analysis (median-split by age)
- Organisation-level Kruskal-Wallis comparisons
- Partial Spearman correlations controlling for project size

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


# ─────────────────────────────────────────────────────────────────────────────
# Utility functions
# ─────────────────────────────────────────────────────────────────────────────


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


def benjamini_hochberg(p_values: list[float], alpha: float = 0.05) -> list[bool]:
    """Apply Benjamini-Hochberg FDR correction.

    Returns a list of booleans indicating which hypotheses are significant.
    """
    n = len(p_values)
    if n == 0:
        return []
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    significant = [False] * n
    # Find the largest k such that p_(k) <= k/n * alpha
    max_k = -1
    for rank, (orig_idx, p) in enumerate(indexed, start=1):
        threshold = (rank / n) * alpha
        if p <= threshold:
            max_k = rank
    # All hypotheses with rank <= max_k are significant
    if max_k > 0:
        for rank, (orig_idx, p) in enumerate(indexed, start=1):
            if rank <= max_k:
                significant[orig_idx] = True
    return significant


def load_data(output_dir: Path) -> dict[str, pd.DataFrame]:
    """Load all CSV files from the output directory."""
    dfs = {}
    for csv_file in sorted(output_dir.glob("*.csv")):
        dfs[csv_file.stem] = pd.read_csv(csv_file)
    return dfs


def _merge_repo_chaoss(
    repo_metrics: pd.DataFrame, chaoss: pd.DataFrame,
) -> pd.DataFrame:
    """Merge repo_metrics and chaoss_summary into a single DataFrame."""
    return repo_metrics.merge(
        chaoss, left_on="full_name", right_on="repo_full_name", how="inner",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 1. Descriptive statistics
# ─────────────────────────────────────────────────────────────────────────────


def compute_descriptive_stats(
    repo_metrics: pd.DataFrame, chaoss: pd.DataFrame,
) -> pd.DataFrame:
    """Compute descriptive statistics for key metrics."""
    merged = _merge_repo_chaoss(repo_metrics, chaoss)

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


# ─────────────────────────────────────────────────────────────────────────────
# 2. Normality tests
# ─────────────────────────────────────────────────────────────────────────────


def compute_normality_tests(
    repo_metrics: pd.DataFrame, chaoss: pd.DataFrame,
) -> pd.DataFrame:
    """Run Shapiro-Wilk normality tests on key metrics."""
    merged = _merge_repo_chaoss(repo_metrics, chaoss)

    test_vars = [
        "total_commits", "num_developers", "bus_factor", "bus_factor_no_bots",
        "burstiness_cv", "herfindahl_hirschman_index", "hhi_no_bots",
        "stale_issue_ratio", "health_percentage",
        "change_request_acceptance_ratio",
        "core_contributor_count", "network_density",
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
                "p_value": round(p, 6),
                "normal_at_0.05": p > 0.05,
            })

    return pd.DataFrame(results)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Spearman correlations with FDR correction
# ─────────────────────────────────────────────────────────────────────────────


def compute_correlations(
    repo_metrics: pd.DataFrame, chaoss: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Compute Spearman rank correlations between key metrics.

    Returns (corr_matrix, p_matrix, significant_pairs_df).
    The significant_pairs_df includes Benjamini-Hochberg FDR correction.
    """
    merged = _merge_repo_chaoss(repo_metrics, chaoss)

    # Compute project age in years
    if "created_at" in merged.columns:
        merged["age_years"] = (
            pd.to_datetime("now", utc=True)
            - pd.to_datetime(merged["created_at"], utc=True)
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
    corr_matrix = pd.DataFrame(
        np.zeros((n, n)), index=subset.columns, columns=subset.columns,
    )
    p_matrix = pd.DataFrame(
        np.ones((n, n)), index=subset.columns, columns=subset.columns,
    )

    # Collect all pairs for FDR
    pair_info: list[dict] = []

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
                    p_matrix.iloc[i, j] = round(p, 6)
                    p_matrix.iloc[j, i] = round(p, 6)
                    pair_info.append({
                        "var_a": col_a,
                        "var_b": col_b,
                        "rho": round(rho, 4),
                        "p_value": round(p, 6),
                        "n_pairs": len(valid),
                    })

    # Apply BH FDR correction
    if pair_info:
        raw_p = [pi["p_value"] for pi in pair_info]
        sig_flags = benjamini_hochberg(raw_p, alpha=0.05)
        for pi, sig in zip(pair_info, sig_flags):
            pi["significant_uncorrected"] = pi["p_value"] < 0.05
            pi["significant_fdr"] = sig

    sig_df = pd.DataFrame(pair_info)
    if not sig_df.empty:
        sig_df = sig_df.sort_values("p_value")

    return corr_matrix, p_matrix, sig_df


# ─────────────────────────────────────────────────────────────────────────────
# 4. Group comparisons (Mann-Whitney U)
# ─────────────────────────────────────────────────────────────────────────────


def _mann_whitney_comparison(
    merged: pd.DataFrame,
    group_col: str,
    comparison_name: str,
    metrics: list[str],
) -> list[dict]:
    """Run Mann-Whitney U on a boolean grouping column."""
    results = []
    if group_col not in merged.columns:
        return results

    group_a = merged[merged[group_col] == True]   # noqa: E712
    group_b = merged[merged[group_col] == False]   # noqa: E712

    for metric in metrics:
        if metric not in merged.columns:
            continue
        a = group_a[metric].dropna().values
        b = group_b[metric].dropna().values
        if len(a) >= 2 and len(b) >= 2:
            u_stat, p = stats.mannwhitneyu(a, b, alternative="two-sided")
            delta, mag = cliffs_delta(a, b)
            results.append({
                "comparison": comparison_name,
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
    return results


def compute_group_comparisons(
    repo_metrics: pd.DataFrame,
    chaoss: pd.DataFrame,
) -> pd.DataFrame:
    """Compare metrics across groups using Mann-Whitney U."""
    merged = _merge_repo_chaoss(repo_metrics, chaoss)

    comparisons = []

    # CI/CD vs no CI/CD
    comparisons.extend(_mann_whitney_comparison(
        merged, "has_ci_cd", "CI/CD vs No CI/CD",
        ["bus_factor", "bus_factor_no_bots", "stale_issue_ratio",
         "health_percentage", "num_developers", "total_commits"],
    ))

    # Cloud vs no cloud
    comparisons.extend(_mann_whitney_comparison(
        merged, "cloud_detected", "Cloud vs No Cloud",
        ["total_commits", "num_developers", "bus_factor_no_bots",
         "health_percentage", "hhi_no_bots"],
    ))

    # AI/ML vs no AI/ML
    comparisons.extend(_mann_whitney_comparison(
        merged, "ai_ml_detected", "AI/ML vs No AI/ML",
        ["num_developers", "bus_factor_no_bots", "health_percentage"],
    ))

    # OSI license vs no OSI license
    comparisons.extend(_mann_whitney_comparison(
        merged, "is_osi_approved", "OSI License vs No License",
        ["health_percentage", "num_developers", "bus_factor_no_bots",
         "stars", "forks"],
    ))

    return pd.DataFrame(comparisons)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Bot impact analysis
# ─────────────────────────────────────────────────────────────────────────────


def compute_bot_impact(
    person_metrics: pd.DataFrame, chaoss: pd.DataFrame,
) -> pd.DataFrame:
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
        bot_commits = (
            pm[pm["is_bot"] == True]["num_commits"].sum()  # noqa: E712
            if "is_bot" in pm.columns else 0
        )

        results.append({
            "repo_full_name": repo,
            "total_contributors": total_contributors,
            "bot_contributors": int(bot_contributors),
            "human_contributors": total_contributors - int(bot_contributors),
            "bot_commit_pct": (
                round(bot_commits / total_commits * 100, 1)
                if total_commits > 0 else 0
            ),
            "bus_factor": cm_row.get("bus_factor"),
            "bus_factor_no_bots": cm_row.get("bus_factor_no_bots"),
            "hhi": cm_row.get("herfindahl_hirschman_index"),
            "hhi_no_bots": cm_row.get("hhi_no_bots"),
            "hhi_known_orgs_only": cm_row.get("hhi_known_orgs_only"),
        })

    return pd.DataFrame(results)


# ─────────────────────────────────────────────────────────────────────────────
# 6. Wilcoxon signed-rank tests for bot impact (paired before/after)
# ─────────────────────────────────────────────────────────────────────────────


def compute_wilcoxon_bot_impact(chaoss: pd.DataFrame) -> pd.DataFrame:
    """Wilcoxon signed-rank tests comparing metrics with/without bot filtering.

    Tests paired differences: HHI vs HHI_no_bots, bus_factor vs bus_factor_no_bots.
    """
    results = []

    paired_tests = [
        ("herfindahl_hirschman_index", "hhi_no_bots", "HHI with bots vs without bots"),
        ("bus_factor", "bus_factor_no_bots", "Bus factor with bots vs without bots"),
        (
            "elephant_factor", "elephant_factor_no_bots",
            "Elephant factor with bots vs without bots",
        ),
    ]

    for col_with, col_without, label in paired_tests:
        if col_with not in chaoss.columns or col_without not in chaoss.columns:
            continue
        valid = chaoss[[col_with, col_without]].dropna()
        if len(valid) < 5:
            continue

        a = valid[col_with].values
        b = valid[col_without].values
        diff = a - b

        # Count how many repos changed
        n_changed = np.sum(diff != 0)
        n_total = len(diff)
        mean_diff = np.mean(diff)
        median_diff = np.median(diff)

        if n_changed >= 2:
            # Wilcoxon only on non-zero differences
            try:
                stat, p = stats.wilcoxon(
                    a, b, alternative="two-sided", zero_method="wilcox",
                )
            except ValueError:
                stat, p = np.nan, np.nan
        else:
            stat, p = np.nan, np.nan

        results.append({
            "comparison": label,
            "metric_with_bots": col_with,
            "metric_without_bots": col_without,
            "n_repos": n_total,
            "n_changed": int(n_changed),
            "mean_with": round(np.mean(a), 2),
            "mean_without": round(np.mean(b), 2),
            "median_with": round(np.median(a), 2),
            "median_without": round(np.median(b), 2),
            "mean_difference": round(mean_diff, 2),
            "median_difference": round(median_diff, 2),
            "W_statistic": round(stat, 4) if not np.isnan(stat) else None,
            "p_value": round(p, 6) if not np.isnan(p) else None,
            "significant": p < 0.05 if not np.isnan(p) else None,
        })

    return pd.DataFrame(results)


# ─────────────────────────────────────────────────────────────────────────────
# 7. Project maturity analysis (median-split by age)
# ─────────────────────────────────────────────────────────────────────────────


def compute_maturity_analysis(
    repo_metrics: pd.DataFrame, chaoss: pd.DataFrame,
) -> pd.DataFrame:
    """Compare metrics between mature and young projects (median age split)."""
    merged = _merge_repo_chaoss(repo_metrics, chaoss)

    if "created_at" not in merged.columns:
        return pd.DataFrame()

    merged["age_years"] = (
        pd.to_datetime("now", utc=True)
        - pd.to_datetime(merged["created_at"], utc=True)
    ).dt.days / 365.25

    median_age = merged["age_years"].median()

    mature = merged[merged["age_years"] >= median_age]
    young = merged[merged["age_years"] < median_age]

    comparison_metrics = [
        "num_developers", "total_commits", "bus_factor", "bus_factor_no_bots",
        "burstiness_cv", "hhi_no_bots", "stale_issue_ratio",
        "health_percentage", "core_contributor_count", "network_density",
        "change_request_acceptance_ratio",
        "median_pr_review_turnaround_hours",
    ]

    results = []
    for metric in comparison_metrics:
        if metric not in merged.columns:
            continue
        a = mature[metric].dropna().values
        b = young[metric].dropna().values
        if len(a) >= 2 and len(b) >= 2:
            u_stat, p = stats.mannwhitneyu(a, b, alternative="two-sided")
            delta, mag = cliffs_delta(a, b)
            results.append({
                "comparison": f"Mature (≥{median_age:.1f}y) vs Young (<{median_age:.1f}y)",
                "metric": metric,
                "mature_n": len(a),
                "young_n": len(b),
                "mature_median": round(np.median(a), 4),
                "young_median": round(np.median(b), 4),
                "U_statistic": round(u_stat, 4),
                "p_value": round(p, 4),
                "cliffs_delta": delta,
                "effect_magnitude": mag,
            })

    return pd.DataFrame(results)


# ─────────────────────────────────────────────────────────────────────────────
# 8. Organisation-level Kruskal-Wallis comparisons
# ─────────────────────────────────────────────────────────────────────────────


def compute_org_kruskal_wallis(
    repo_metrics: pd.DataFrame, chaoss: pd.DataFrame,
) -> pd.DataFrame:
    """Compare metrics across parent organisations using Kruskal-Wallis.

    Groups repos by the owner/org part of the full_name.
    Only compares organisations with ≥3 repos.
    """
    merged = _merge_repo_chaoss(repo_metrics, chaoss)

    # Extract organisation from full_name (e.g. "CodeForAfrica/ui" → "CodeForAfrica")
    merged["organisation"] = merged["full_name"].str.split("/").str[0]

    # Only include orgs with 3+ repos
    org_counts = merged["organisation"].value_counts()
    multi_orgs = org_counts[org_counts >= 3].index.tolist()

    if len(multi_orgs) < 2:
        return pd.DataFrame()

    subset = merged[merged["organisation"].isin(multi_orgs)]

    comparison_metrics = [
        "bus_factor_no_bots", "hhi_no_bots", "health_percentage",
        "num_developers", "total_commits", "burstiness_cv",
        "stale_issue_ratio", "core_contributor_count",
    ]

    results = []
    for metric in comparison_metrics:
        if metric not in subset.columns:
            continue
        groups = []
        group_info = []
        for org in multi_orgs:
            org_data = subset[subset["organisation"] == org][metric].dropna().values
            if len(org_data) >= 2:
                groups.append(org_data)
                group_info.append({
                    "org": org,
                    "n": len(org_data),
                    "median": round(np.median(org_data), 4),
                })

        if len(groups) >= 2:
            try:
                h_stat, p = stats.kruskal(*groups)
                # Epsilon-squared effect size: η²_H = (H - k + 1) / (n - k)
                k = len(groups)
                n_total = sum(len(g) for g in groups)
                epsilon_sq = (h_stat - k + 1) / (n_total - k) if n_total > k else 0
                epsilon_sq = max(0, epsilon_sq)
            except ValueError:
                h_stat, p, epsilon_sq = np.nan, np.nan, np.nan

            results.append({
                "metric": metric,
                "organisations": ", ".join(gi["org"] for gi in group_info),
                "org_details": "; ".join(
                    f"{gi['org']}(n={gi['n']},med={gi['median']})"
                    for gi in group_info
                ),
                "n_groups": len(groups),
                "n_total": sum(len(g) for g in groups),
                "H_statistic": round(h_stat, 4) if not np.isnan(h_stat) else None,
                "p_value": round(p, 4) if not np.isnan(p) else None,
                "epsilon_squared": (
                    round(epsilon_sq, 4) if not np.isnan(epsilon_sq) else None
                ),
                "significant": p < 0.05 if not np.isnan(p) else None,
            })

    return pd.DataFrame(results)


# ─────────────────────────────────────────────────────────────────────────────
# 9. Partial Spearman correlations (controlling for project size)
# ─────────────────────────────────────────────────────────────────────────────


def _partial_spearman(
    x: np.ndarray, y: np.ndarray, z: np.ndarray,
) -> tuple[float, float]:
    """Compute partial Spearman correlation between x and y, controlling for z.

    Uses the standard formula for partial correlation from residuals of
    rank-transformed variables.
    """
    # Rank-transform all variables
    from scipy.stats import rankdata
    rx = rankdata(x)
    ry = rankdata(y)
    rz = rankdata(z)

    # Residuals of rx ~ rz and ry ~ rz (simple OLS residuals)
    # rx_resid = rx - (a + b*rz)
    def _residuals(target: np.ndarray, predictor: np.ndarray) -> np.ndarray:
        n = len(target)
        x_mean = predictor.mean()
        y_mean = target.mean()
        b = np.sum((predictor - x_mean) * (target - y_mean)) / np.sum(
            (predictor - x_mean) ** 2,
        )
        a = y_mean - b * x_mean
        return target - (a + b * predictor)

    rx_resid = _residuals(rx, rz)
    ry_resid = _residuals(ry, rz)

    # Pearson correlation of residuals = partial Spearman correlation
    rho, p = stats.pearsonr(rx_resid, ry_resid)
    return round(rho, 4), round(p, 6)


def compute_partial_correlations(
    repo_metrics: pd.DataFrame, chaoss: pd.DataFrame,
) -> pd.DataFrame:
    """Compute partial Spearman correlations controlling for num_developers.

    This helps disentangle size-driven correlations from genuine relationships.
    """
    merged = _merge_repo_chaoss(repo_metrics, chaoss)

    control_var = "num_developers"
    if control_var not in merged.columns:
        return pd.DataFrame()

    # Pairs to test (controlling for project size)
    test_pairs = [
        ("bus_factor_no_bots", "hhi_no_bots"),
        ("burstiness_cv", "stale_issue_ratio"),
        ("bus_factor_no_bots", "health_percentage"),
        ("core_contributor_count", "network_density"),
        ("bus_factor_no_bots", "core_contributor_count"),
        ("hhi_no_bots", "health_percentage"),
        ("burstiness_cv", "health_percentage"),
        ("bus_factor_no_bots", "burstiness_cv"),
        ("hhi_no_bots", "stale_issue_ratio"),
        ("change_request_acceptance_ratio", "median_pr_review_turnaround_hours"),
    ]

    results = []
    for var_a, var_b in test_pairs:
        if var_a not in merged.columns or var_b not in merged.columns:
            continue
        valid = merged[[var_a, var_b, control_var]].dropna()
        if len(valid) < 5:
            continue

        # Zero-order (unconditional) Spearman
        rho_zero, p_zero = stats.spearmanr(valid[var_a], valid[var_b])

        # Partial Spearman controlling for num_developers
        rho_partial, p_partial = _partial_spearman(
            valid[var_a].values, valid[var_b].values, valid[control_var].values,
        )

        results.append({
            "var_a": var_a,
            "var_b": var_b,
            "control": control_var,
            "n": len(valid),
            "rho_zero_order": round(rho_zero, 4),
            "p_zero_order": round(p_zero, 6),
            "rho_partial": rho_partial,
            "p_partial": p_partial,
            "rho_change": round(abs(rho_zero) - abs(rho_partial), 4),
            "interpretation": (
                "confounded"
                if abs(rho_zero) - abs(rho_partial) > 0.15
                else "robust"
            ),
        })

    return pd.DataFrame(results)


# ─────────────────────────────────────────────────────────────────────────────
# 10. Dataset summary
# ─────────────────────────────────────────────────────────────────────────────


def compute_dataset_summary(
    repo_metrics: pd.DataFrame,
    person_metrics: pd.DataFrame | None,
    chaoss: pd.DataFrame,
) -> pd.DataFrame:
    """Compute a high-level summary of the dataset."""
    merged = _merge_repo_chaoss(repo_metrics, chaoss)

    orgs = merged["full_name"].str.split("/").str[0].nunique()
    languages = set()
    for lang_str in repo_metrics["primary_language"].dropna():
        languages.add(lang_str)

    total_bots = 0
    total_humans = 0
    if person_metrics is not None and "is_bot" in person_metrics.columns:
        total_bots = int(person_metrics["is_bot"].sum())
        total_humans = int((~person_metrics["is_bot"]).sum())

    summary = {
        "total_repositories": len(repo_metrics),
        "unique_organisations": orgs,
        "unique_primary_languages": len(languages),
        "primary_languages": ", ".join(sorted(languages)),
        "total_contributors": total_humans + total_bots,
        "human_contributors": total_humans,
        "bot_contributors": total_bots,
        "total_commits": int(repo_metrics["total_commits"].sum()),
        "total_stars": int(repo_metrics["stars"].sum()),
        "total_forks": int(repo_metrics["forks"].sum()),
        "repos_with_ci_cd": int(repo_metrics["has_ci_cd"].sum()),
        "repos_with_cloud": int(repo_metrics["cloud_detected"].sum()),
        "repos_with_ai_ml": int(repo_metrics["ai_ml_detected"].sum()),
        "repos_with_osi_license": int(repo_metrics["is_osi_approved"].sum()),
        "median_age_years": round(
            (
                pd.to_datetime("now", utc=True)
                - pd.to_datetime(repo_metrics["created_at"], utc=True)
            ).dt.days.median() / 365.25,
            1,
        ),
    }

    return pd.DataFrame([summary])


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


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

    # ── 0. Dataset summary ──────────────────────────────────────────────
    print("0. Computing dataset summary...")
    summary = compute_dataset_summary(repo_metrics, person_metrics, chaoss)
    summary.to_csv(results_dir / "dataset_summary.csv", index=False)
    print(f"   Saved to {results_dir / 'dataset_summary.csv'}")
    for col in summary.columns:
        print(f"   {col}: {summary[col].iloc[0]}")
    print()

    # ── 1. Descriptive statistics ───────────────────────────────────────
    print("1. Computing descriptive statistics...")
    desc = compute_descriptive_stats(repo_metrics, chaoss)
    desc.to_csv(results_dir / "descriptive_statistics.csv")
    print(f"   Saved to {results_dir / 'descriptive_statistics.csv'}")
    print(desc[["count", "mean", "50%", "std", "IQR"]].to_string())
    print()

    # ── 2. Normality tests ──────────────────────────────────────────────
    print("2. Running Shapiro-Wilk normality tests...")
    normality = compute_normality_tests(repo_metrics, chaoss)
    normality.to_csv(results_dir / "normality_tests.csv", index=False)
    print(f"   Saved to {results_dir / 'normality_tests.csv'}")
    print(normality.to_string(index=False))
    print()

    # ── 3. Spearman correlations with FDR ───────────────────────────────
    print("3. Computing Spearman rank correlations (with BH-FDR correction)...")
    corr_matrix, p_matrix, sig_pairs_df = compute_correlations(repo_metrics, chaoss)
    corr_matrix.to_csv(results_dir / "spearman_correlations.csv")
    p_matrix.to_csv(results_dir / "spearman_p_values.csv")
    sig_pairs_df.to_csv(results_dir / "correlation_pairs_fdr.csv", index=False)
    print(f"   Saved to {results_dir / 'spearman_correlations.csv'}")
    print(f"   Saved to {results_dir / 'correlation_pairs_fdr.csv'}")

    if not sig_pairs_df.empty:
        fdr_sig = sig_pairs_df[sig_pairs_df["significant_fdr"] == True]  # noqa: E712
        uncorr_sig = sig_pairs_df[sig_pairs_df["significant_uncorrected"] == True]  # noqa: E712
        print(
            f"   {len(uncorr_sig)} pairs significant at p<0.05 uncorrected, "
            f"{len(fdr_sig)} survive BH-FDR correction",
        )
        if not fdr_sig.empty:
            print("   FDR-significant correlations:")
            for _, row in fdr_sig.iterrows():
                print(
                    f"     {row['var_a']} ~ {row['var_b']}: "
                    f"ρ={row['rho']:.3f}, p={row['p_value']:.4f} (n={row['n_pairs']})",
                )
    print()

    # ── 4. Group comparisons (Mann-Whitney U) ──────────────────────────
    print("4. Running group comparisons (Mann-Whitney U)...")
    comparisons = compute_group_comparisons(repo_metrics, chaoss)
    if not comparisons.empty:
        comparisons.to_csv(results_dir / "group_comparisons.csv", index=False)
        print(f"   Saved to {results_dir / 'group_comparisons.csv'}")
        print(comparisons.to_string(index=False))
    else:
        print("   Insufficient data for group comparisons")
    print()

    # ── 5. Bot impact analysis ──────────────────────────────────────────
    if person_metrics is not None:
        print("5. Analyzing bot impact on metrics...")
        bot_impact = compute_bot_impact(person_metrics, chaoss)
        if not bot_impact.empty:
            bot_impact.to_csv(results_dir / "bot_impact.csv", index=False)
            print(f"   Saved to {results_dir / 'bot_impact.csv'}")
            print(bot_impact.to_string(index=False))
        print()

    # ── 6. Wilcoxon signed-rank tests (paired bot impact) ──────────────
    print("6. Running Wilcoxon signed-rank tests (paired bot impact)...")
    wilcoxon = compute_wilcoxon_bot_impact(chaoss)
    if not wilcoxon.empty:
        wilcoxon.to_csv(results_dir / "wilcoxon_bot_impact.csv", index=False)
        print(f"   Saved to {results_dir / 'wilcoxon_bot_impact.csv'}")
        print(wilcoxon.to_string(index=False))
    else:
        print("   Insufficient paired data for Wilcoxon tests")
    print()

    # ── 7. Project maturity analysis ────────────────────────────────────
    print("7. Running project maturity analysis (age median split)...")
    maturity = compute_maturity_analysis(repo_metrics, chaoss)
    if not maturity.empty:
        maturity.to_csv(results_dir / "maturity_analysis.csv", index=False)
        print(f"   Saved to {results_dir / 'maturity_analysis.csv'}")
        print(maturity.to_string(index=False))
    else:
        print("   Insufficient data for maturity analysis")
    print()

    # ── 8. Organisation-level Kruskal-Wallis ────────────────────────────
    print("8. Running organisation-level Kruskal-Wallis comparisons...")
    org_kw = compute_org_kruskal_wallis(repo_metrics, chaoss)
    if not org_kw.empty:
        org_kw.to_csv(results_dir / "org_kruskal_wallis.csv", index=False)
        print(f"   Saved to {results_dir / 'org_kruskal_wallis.csv'}")
        print(org_kw.to_string(index=False))
    else:
        print("   Need ≥2 organisations with ≥3 repos each for Kruskal-Wallis")
    print()

    # ── 9. Partial correlations (controlling for project size) ──────────
    print("9. Computing partial Spearman correlations (controlling for num_developers)...")
    partial = compute_partial_correlations(repo_metrics, chaoss)
    if not partial.empty:
        partial.to_csv(results_dir / "partial_correlations.csv", index=False)
        print(f"   Saved to {results_dir / 'partial_correlations.csv'}")
        print(partial.to_string(index=False))
    else:
        print("   Insufficient data for partial correlations")
    print()

    print(f"All results saved to {results_dir}/")


if __name__ == "__main__":
    main()
