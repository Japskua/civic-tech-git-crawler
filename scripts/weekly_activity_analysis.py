"""Weekly contributor activity — new analyses unlocked by lines_added/lines_removed.

Reads output/contributor_weekly_activity.csv and writes three CSVs plus a
summary text report into output/weekly_activity_analysis/:

  A. weekly_elephant_factor.csv — per repo, fraction of each week's code
     change done by the single busiest contributor; flags weeks where one
     person did ≥50% ("elephant weeks") or 100% ("single-point weeks").
  B. churn_ratio.csv — per repo, deletions / (additions+deletions) and the
     share of weeks that are deletion-heavy (>0.5).
  D. effort_gini.csv — per repo, Gini coefficient of lines_changed per
     contributor, alongside contributor count and total commits.
  summary.md — short human-readable rundown of the most striking findings.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "output" / "contributor_weekly_activity.csv"
OUT_DIR = REPO_ROOT / "output" / "weekly_activity_analysis"


def gini(values: np.ndarray) -> float:
    """Gini coefficient of a non-negative array (0=equal, 1=one person has all)."""
    v = np.asarray(values, dtype=float)
    v = v[v > 0]
    n = v.size
    if n <= 1:
        return 0.0
    v = np.sort(v)
    idx = np.arange(1, n + 1)
    return float((2 * np.sum(idx * v) / (n * np.sum(v))) - (n + 1) / n)


def weekly_elephant(df: pd.DataFrame) -> pd.DataFrame:
    """A. Per repo: how often does a single contributor dominate a week's code changes?"""
    df = df.copy()
    df["lines_changed"] = df["lines_added"] + df["lines_removed"]
    # per (repo, week): total lines and the top contributor's share
    per_week = df.groupby(["repo_full_name", "week_start"]).agg(
        week_total=("lines_changed", "sum"),
        week_top=("lines_changed", "max"),
        contributors_in_week=("contributor_id", "nunique"),
    ).reset_index()
    # Only weeks with at least 1 line of change — a week of zero-LOC merges is noise
    per_week = per_week[per_week["week_total"] > 0].copy()
    per_week["top_share"] = per_week["week_top"] / per_week["week_total"]

    rows = []
    for repo, g in per_week.groupby("repo_full_name"):
        n_weeks = len(g)
        elephant = (g["top_share"] >= 0.5).sum()
        single_point = (g["top_share"] >= 0.999).sum()
        solo_weeks = (g["contributors_in_week"] == 1).sum()
        rows.append({
            "repo_full_name": repo,
            "weeks_with_activity": n_weeks,
            "mean_top_share": round(g["top_share"].mean(), 3),
            "median_top_share": round(g["top_share"].median(), 3),
            "elephant_weeks_pct": round(100 * elephant / n_weeks, 1) if n_weeks else 0.0,
            "single_contributor_weeks_pct": round(100 * single_point / n_weeks, 1) if n_weeks else 0.0,
            "solo_weeks_pct": round(100 * solo_weeks / n_weeks, 1) if n_weeks else 0.0,
        })
    return pd.DataFrame(rows).sort_values("mean_top_share", ascending=False)


def churn_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """B. Per repo: deletion share (deletions / (adds+dels)). High = maintenance/rewrite mode."""
    df = df.copy()
    # Per-week aggregates (sum across contributors in the same week)
    per_week = df.groupby(["repo_full_name", "week_start"]).agg(
        added=("lines_added", "sum"),
        removed=("lines_removed", "sum"),
    ).reset_index()
    per_week = per_week[(per_week["added"] + per_week["removed"]) > 0].copy()
    per_week["churn"] = per_week["removed"] / (per_week["added"] + per_week["removed"])

    rows = []
    for repo, g in per_week.groupby("repo_full_name"):
        total_added = g["added"].sum()
        total_removed = g["removed"].sum()
        overall_churn = total_removed / (total_added + total_removed) if (total_added + total_removed) else 0.0
        rows.append({
            "repo_full_name": repo,
            "active_weeks": len(g),
            "total_added": int(total_added),
            "total_removed": int(total_removed),
            "net_loc_delta": int(total_added - total_removed),
            "overall_churn_ratio": round(overall_churn, 3),
            "mean_weekly_churn": round(g["churn"].mean(), 3),
            "median_weekly_churn": round(g["churn"].median(), 3),
            "deletion_heavy_weeks_pct": round(100 * (g["churn"] > 0.5).mean(), 1),
        })
    return pd.DataFrame(rows).sort_values("overall_churn_ratio", ascending=False)


def effort_gini(df: pd.DataFrame) -> pd.DataFrame:
    """D. Per repo: Gini coefficient of total lines_changed per contributor."""
    df = df.copy()
    df["lines_changed"] = df["lines_added"] + df["lines_removed"]
    per_contrib = df.groupby(["repo_full_name", "contributor_id"]).agg(
        commits=("commits", "sum"),
        lines_changed=("lines_changed", "sum"),
    ).reset_index()

    rows = []
    for repo, g in per_contrib.groupby("repo_full_name"):
        active = g[g["lines_changed"] > 0]
        n = len(active)
        if n == 0:
            continue
        top1 = active.sort_values("lines_changed", ascending=False).iloc[0]
        top1_share = top1["lines_changed"] / active["lines_changed"].sum()
        rows.append({
            "repo_full_name": repo,
            "contributors": n,
            "total_commits": int(g["commits"].sum()),
            "effort_gini_lines": round(gini(active["lines_changed"].values), 3),
            "effort_gini_commits": round(gini(active["commits"].astype(float).values), 3),
            "top1_lines_share": round(top1_share, 3),
            "top1_contributor": top1["contributor_id"],
        })
    return pd.DataFrame(rows).sort_values("effort_gini_lines", ascending=False)


def summary(elephant: pd.DataFrame, churn: pd.DataFrame, gini_df: pd.DataFrame, *, total_rows: int, total_contributors: int) -> str:
    lines: list[str] = []
    n_repos = elephant["repo_full_name"].nunique()
    lines.append("# Weekly Activity Analysis — New Findings\n")
    lines.append(
        f"Derived from `output/contributor_weekly_activity.csv` "
        f"({total_rows:,} rows, {n_repos} repos, {total_contributors:,} contributors).\n"
    )

    lines.append("## A. Weekly Elephant Factor (sustainability risk, time-resolved)\n")
    lines.append(
        "For each *week* a repo had any code change, we compute the share of lines "
        "added+removed that came from the single busiest contributor. 'Elephant weeks' "
        "are weeks where ≥50% of the LOC moved through one person. 'Single-contributor "
        "weeks' are weeks where ≥99.9% came from one person (effectively solo).\n"
    )
    most_elephant = elephant.head(5)
    least_elephant = elephant.tail(5).iloc[::-1]
    lines.append("**Most elephant-dominated repos** (highest share of weeks dominated by one contributor):\n")
    for _, r in most_elephant.iterrows():
        lines.append(
            f"- `{r.repo_full_name}`: mean top-share {r.mean_top_share:.1%}, "
            f"{r.elephant_weeks_pct:.0f}% of weeks ≥50%, {r.single_contributor_weeks_pct:.0f}% solo\n"
        )
    lines.append("\n**Most collaborative repos** (lowest top-share — effort spread across people):\n")
    for _, r in least_elephant.iterrows():
        lines.append(
            f"- `{r.repo_full_name}`: mean top-share {r.mean_top_share:.1%}, "
            f"{r.elephant_weeks_pct:.0f}% of weeks ≥50%, {r.single_contributor_weeks_pct:.0f}% solo\n"
        )
    overall_elephant_pct = (elephant["elephant_weeks_pct"] * elephant["weeks_with_activity"]).sum() / elephant["weeks_with_activity"].sum()
    lines.append(f"\n**Dataset-wide**: weighted by weeks, {overall_elephant_pct:.0f}% of active weeks "
                 "had a single contributor responsible for ≥50% of the code change.\n")

    lines.append("\n## B. Churn Ratio (maintenance vs. growth phase)\n")
    lines.append(
        "`churn = deletions / (additions + deletions)`. Close to 0 = pure growth. Close "
        "to 1 = pure cleanup. 0.5 = balanced. We report both the repo-wide aggregate "
        "(across the full history) and the weekly mean.\n"
    )
    net_negative = churn[churn["net_loc_delta"] < 0]
    lines.append(f"\n**{len(net_negative)} repos have net-negative LOC growth** "
                 "(more cumulative deletions than additions across their default-branch history):\n")
    for _, r in net_negative.sort_values("net_loc_delta").iterrows():
        lines.append(
            f"- `{r.repo_full_name}`: +{r.total_added:,} / −{r.total_removed:,} → "
            f"net {r.net_loc_delta:+,} lines, overall churn {r.overall_churn_ratio:.2f}\n"
        )
    most_churn = churn.head(5)
    lines.append("\n**Highest-churn repos** (most deletion-heavy):\n")
    for _, r in most_churn.iterrows():
        lines.append(
            f"- `{r.repo_full_name}`: overall churn {r.overall_churn_ratio:.2f}, "
            f"{r.deletion_heavy_weeks_pct:.0f}% weeks deletion-heavy\n"
        )
    least_churn = churn.tail(5).iloc[::-1]
    lines.append("\n**Lowest-churn repos** (pure growth, little cleanup):\n")
    for _, r in least_churn.iterrows():
        lines.append(
            f"- `{r.repo_full_name}`: overall churn {r.overall_churn_ratio:.2f}, "
            f"+{r.total_added:,} / −{r.total_removed:,}\n"
        )

    lines.append("\n## D. Effort Gini Coefficient (inequality of contribution)\n")
    lines.append(
        "Gini of `lines_changed` per contributor per repo. 0 = everyone contributed equally. "
        "1 = one person did everything. This is the **effort-weighted** complement to the "
        "existing count-based bus factor / Elephant Factor metrics.\n"
    )
    most_unequal = gini_df.head(5)
    lines.append("**Most unequal repos** (Gini closest to 1):\n")
    for _, r in most_unequal.iterrows():
        lines.append(
            f"- `{r.repo_full_name}`: Gini(lines) {r.effort_gini_lines:.2f}, "
            f"Gini(commits) {r.effort_gini_commits:.2f}, top contributor "
            f"`{r.top1_contributor}` did {r.top1_lines_share:.0%}\n"
        )
    least_unequal = gini_df[gini_df["contributors"] >= 5].tail(5).iloc[::-1]
    lines.append("\n**Most equal repos** (Gini closest to 0, min 5 contributors):\n")
    for _, r in least_unequal.iterrows():
        lines.append(
            f"- `{r.repo_full_name}`: Gini(lines) {r.effort_gini_lines:.2f}, "
            f"{r.contributors} contributors, top1 share {r.top1_lines_share:.0%}\n"
        )

    gap = gini_df["effort_gini_lines"] - gini_df["effort_gini_commits"]
    lines.append(
        "\n**Lines-vs-commits Gini gap** (how much more unequal is effort than activity?):\n"
    )
    lines.append(f"- Mean gap across {len(gini_df)} repos: {gap.mean():+.3f}\n")
    lines.append(f"- Max gap (effort much more concentrated than commits): "
                 f"`{gini_df.loc[gap.idxmax(), 'repo_full_name']}` at {gap.max():+.3f}\n")
    lines.append(f"- Min gap (commits more concentrated than effort): "
                 f"`{gini_df.loc[gap.idxmin(), 'repo_full_name']}` at {gap.min():+.3f}\n")
    lines.append(
        "\nA positive gap means one contributor's commits are unusually large (mega-commits, "
        "possibly bots or bulk imports). A negative gap means they commit often but with "
        "small changes.\n"
    )
    return "".join(lines)


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Weekly activity analysis")
    parser.add_argument(
        "output_dir", nargs="?", default=str(REPO_ROOT / "output"),
        help="Crawler output directory containing contributor_weekly_activity.csv",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    csv_path = output_dir / "contributor_weekly_activity.csv"
    out_dir = output_dir / "weekly_activity_analysis"

    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found", file=sys.stderr)
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df):,} rows from {csv_path}")

    print("Computing A: Weekly Elephant Factor...")
    elephant = weekly_elephant(df)
    elephant.to_csv(out_dir / "weekly_elephant_factor.csv", index=False)

    print("Computing B: Churn ratio...")
    churn = churn_ratio(df)
    churn.to_csv(out_dir / "churn_ratio.csv", index=False)

    print("Computing D: Effort Gini...")
    gini_df = effort_gini(df)
    gini_df.to_csv(out_dir / "effort_gini.csv", index=False)

    print("Writing summary.md...")
    (out_dir / "summary.md").write_text(
        summary(
            elephant, churn, gini_df,
            total_rows=len(df),
            total_contributors=df["contributor_id"].nunique(),
        )
    )

    print(f"\nAll artifacts written to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
