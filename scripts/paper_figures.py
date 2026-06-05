"""Generate synthesis figures for paper_draft.md (2026-05 corpus, n=57).

Run after the canonical datasets/2026_05 snapshot has been built (crawl +
statistical_analysis + weekly_activity_analysis). Outputs PNG figures into
datasets/2026_05/figures/ and prints a paper-ready caption block to stdout.

Everything is computed from the dataset — no values are hard-coded — so the
figures and captions stay correct if the corpus is re-crawled.

Usage:
    uv run python scripts/paper_figures.py [snapshot-dir]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, PercentFormatter
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull, QhullError
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SNAPSHOT = ROOT / "datasets" / "2026_05"

# Reference date for age computation (crawl completion).
CRAWL_DATE = pd.Timestamp("2026-05-24", tz="UTC")

_BOT_ACCOUNT_PATTERN = re.compile(
    r"(^|\b)(dependabot|renovate|greenkeeper|snyk-bot|imgbot|codecov|stale"
    r"|allcontributors|github-actions|pyup-bot|transifex-integration|weblate"
    r"|crowdin-bot|mergify|semantic-release-bot|release-drafter|pre-commit-ci"
    r"|netlify|vercel|railway-app|sonarcloud|coveralls|codeclimate|lint-action)(\b|$)",
    re.IGNORECASE,
)
_BOT_ID_PATTERN = re.compile(r"(\[bot\]$|-bot$|-bot-)", re.IGNORECASE)
_BOT_TEXT_PATTERN = re.compile(
    r"(github-actions@github\.com|github\.context\.workflow|auto-committer"
    r"|robo-updater|robo-pusher|roboter@)",
    re.IGNORECASE,
)

# Per-figure styling — keep it monochromatic + reproducible
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "legend.fontsize": 10,
    "figure.dpi": 120,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def _load_repo_metrics(snap: Path) -> pd.DataFrame:
    """Load repository metrics from the canonical or theme-annotated snapshot file."""
    candidates = [
        snap / "repo_metrics.csv",
        # snap / "repo_metrics_with_theme.csv",
        # snap / "repo_metrics_5_theme.csv",
    ]
    for path in candidates:
        if path.exists():
            return pd.read_csv(path).drop(columns=["Theme"], errors="ignore")
    raise FileNotFoundError(f"No repository metrics CSV found in {snap}")


def _load_repo_chaoss(snap: Path) -> pd.DataFrame:
    rm = _load_repo_metrics(snap).rename(columns={"full_name": "repo"})
    ch = pd.read_csv(snap / "chaoss_summary.csv").rename(columns={"repo_full_name": "repo"})
    df = rm.merge(ch, on="repo")
    df["age_years"] = (
        CRAWL_DATE - pd.to_datetime(df["first_commit_date"], utc=True)
    ).dt.days / 365.25
    return df


def _format_int_space(value: float) -> str:
    return f"{value:,.0f}".replace(",", " ")


def _is_lifecycle_bot(row: pd.Series) -> bool:
    """Detect bot lifecycle records without relying on person_metrics.csv."""
    identity_parts = [
        row.get("contributor_id"),
        row.get("login"),
        row.get("name"),
        row.get("email"),
    ]
    values = [str(value) for value in identity_parts if pd.notna(value)]
    login = str(row.get("login")) if pd.notna(row.get("login")) else ""
    contributor_id = (
        str(row.get("contributor_id")) if pd.notna(row.get("contributor_id")) else ""
    )
    if _BOT_ID_PATTERN.search(login) or _BOT_ID_PATTERN.search(contributor_id):
        return True
    text = " ".join(values)
    return bool(_BOT_ACCOUNT_PATTERN.search(text) or _BOT_TEXT_PATTERN.search(text))


def fig1_busfactor_vs_hhi(snap: Path, out: Path) -> str:
    df = _load_repo_chaoss(snap)
    sub = df.dropna(subset=["hhi_no_bots", "bus_factor_no_bots"])
    n = len(sub)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(sub["hhi_no_bots"], sub["bus_factor_no_bots"],
               s=np.clip(sub["num_developers"] * 1.2, 30, 400),
               alpha=0.6, marker="o", edgecolors="black", linewidths=0.5,
               label="point size ∝ num_developers")
    for _, r in sub.nlargest(3, "hhi_no_bots").iterrows():
        ax.annotate(r["repo"].split("/")[-1], (r["hhi_no_bots"], r["bus_factor_no_bots"]),
                    xytext=(5, 4), textcoords="offset points", fontsize=8, alpha=0.7)
    for _, r in sub.nlargest(2, "bus_factor_no_bots").iterrows():
        ax.annotate(r["repo"].split("/")[-1], (r["hhi_no_bots"], r["bus_factor_no_bots"]),
                    xytext=(5, 4), textcoords="offset points", fontsize=8, alpha=0.7)

    rho, p = stats.spearmanr(sub["hhi_no_bots"], sub["bus_factor_no_bots"])
    ax.set_xlabel("HHI (humans only, 0–10,000 scale)")
    ax.set_ylabel("Bus factor (humans only)")
    ax.set_title(f"Bus factor vs. organisational concentration (n={n})\n"
                 f"Spearman ρ = {rho:.3f}, p = {p:.2g}")
    ax.legend(loc="upper right", framealpha=0.95)
    fig.savefig(out / "fig1_busfactor_vs_hhi.png")
    plt.close(fig)
    return (f"Figure 1. Bus factor vs. HHI (humans only) across the n={n} civic-tech "
            f"repositories with computable concentration metrics. Each point is a "
            f"repository; marker size encodes num_developers. The negative relationship "
            f"(Spearman ρ = {rho:.3f}, p = {p:.2g}) is the central concentration-of-effort "
            f"mechanism: as effort concentrates in fewer hands (higher HHI), the bus factor "
            f"falls.")


def fig2_effort_gini(snap: Path, out: Path) -> str:
    g = pd.read_csv(snap / "weekly_activity_analysis" / "effort_gini.csv")
    g = g.dropna(subset=["effort_gini_commits", "effort_gini_lines"])
    n = len(g)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(g["effort_gini_commits"], g["effort_gini_lines"],
               s=80, alpha=0.6, marker="o", edgecolors="black", linewidths=0.5,
               label="repository")
    ax.plot([0, 1], [0, 1], "k--", alpha=0.4, linewidth=1, label="y = x (equal Gini)")
    for _, r in g.nlargest(5, "effort_gini_lines").iterrows():
        ax.annotate(r["repo_full_name"].split("/")[-1],
                    (r["effort_gini_commits"], r["effort_gini_lines"]),
                    xytext=(6, 2), textcoords="offset points", fontsize=8, alpha=0.8)

    gap = g["effort_gini_lines"] - g["effort_gini_commits"]
    gap_mean = gap.mean()
    n_above = int((gap > 0).sum())
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Gini of commits per contributor")
    ax.set_ylabel("Gini of lines changed per contributor")
    ax.set_title(f"Effort Gini: lines vs. commits (n={n})\n"
                 f"Mean gap (lines − commits) = {gap_mean:+.3f}; "
                 f"lines-Gini ≥ commits-Gini in {n_above}/{n} repos")
    ax.legend(loc="lower right", framealpha=0.95)
    fig.savefig(out / "fig2_effort_gini.png")
    plt.close(fig)
    return (f"Figure 2. Effort Gini coefficients on lines-changed vs. commits per "
            f"contributor across n={n} repositories. Points above y=x indicate effort "
            f"concentration is more extreme than commit-count concentration alone suggests. "
            f"Mean gap {gap_mean:+.3f}; lines-Gini ≥ commits-Gini in {n_above}/{n} repos.")


def fig3_burstiness_vs_stale(snap: Path, out: Path) -> str:
    ch = pd.read_csv(snap / "chaoss_summary.csv")
    df = ch[["repo_full_name", "burstiness_cv", "stale_issue_ratio"]].dropna()
    n = len(df)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(df["burstiness_cv"], df["stale_issue_ratio"],
               s=80, alpha=0.6, marker="o", edgecolors="black", linewidths=0.5,
               label="repository")
    x, y = df["burstiness_cv"].values, df["stale_issue_ratio"].values
    slope, intercept, _, _, _ = stats.linregress(x, y)
    xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, slope * xs + intercept, "k-", alpha=0.4, linewidth=1.2, label="OLS fit")

    rho, p = stats.spearmanr(x, y)
    ax.set_xlabel("Burstiness CV")
    ax.set_ylabel("Stale issue ratio")
    ax.set_title(f"Burstiness vs. stale-issue-ratio (n={n} pairs)\n"
                 f"Spearman ρ = {rho:.3f}, p = {p:.3f}")
    ax.legend(loc="lower right", framealpha=0.95)
    fig.savefig(out / "fig3_burstiness_vs_stale.png")
    plt.close(fig)
    sig = "" if p < 0.05 else " (not statistically significant)"
    return (f"Figure 3. Burstiness (coefficient of variation of weekly commit counts) vs. "
            f"stale-issue-ratio across n={n} repositories with both metrics computable. "
            f"Spearman ρ = {rho:.3f}, p = {p:.3f}{sig}.")


def fig4_corpus_distributions(snap: Path, out: Path) -> str:
    """Characterise the shape of the n=57 corpus on its key metrics."""
    df = _load_repo_chaoss(snap)
    n = len(df)

    panels = [
        ("bus_factor_no_bots", "Bus factor (no bots)", False),
        ("hhi_no_bots", "HHI (no bots, 0–10 000)", False),
        ("num_developers", "Num developers (log10)", True),
        ("age_years", "Project age (years)", False),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(14, 4))
    for ax, (col, label, log) in zip(axes, panels):
        s = df[col].dropna()
        vals = np.log10(s.replace(0, 0.5)) if log else s
        ax.hist(vals, bins=12, color="0.6", edgecolor="black", linewidth=0.6)
        med = vals.median()
    
        ax.axvline(med, color="black", linestyle="--", linewidth=1.2,
                   label=f"median {_format_int_space(s.median())}")
        # ax.set_title(label, fontsize=10)
        ax.set_ylabel("repositories")
        ax.legend(fontsize=8)
    fig.suptitle(f"Distribution of key metrics across the n={n} civic-tech corpus", fontsize=12)
    fig.tight_layout()
    fig.savefig(out / "fig4_corpus_distributions.png")
    plt.close(fig)
    bf_med = df["bus_factor_no_bots"].median()
    hhi_med = df["hhi_no_bots"].median()
    return (f"Figure 4. Distribution of the four headline metrics across the n={n} corpus: "
            f"bus factor, HHI, number of developers (log10), and project age. The corpus is "
            f"dominated by highly concentrated projects — median bus factor {_format_int_space(bf_med)} and "
            f"median HHI {_format_int_space(hhi_med)} — with a long tail of larger, more collaborative repositories.")


def fig4_corpus_distributions_colored(snap: Path, out: Path) -> str:
    """Alternative Figure 4 as four separate colored distribution charts."""
    df = _load_repo_chaoss(snap)
    n = len(df)
    bar_color = "#6f8796"
    median_color = "#d97706"

    panels = [
        ("a", "bus_factor_no_bots", "(a) Bus factor (no bots)", "Bus factor", False),
        ("b", "hhi_no_bots", "(b) HHI (no bots, 0–10 000)", "HHI", False),
        ("c", "num_developers", "(c) Num developers (log scale)", "developers", True),
        ("d", "age_years", "(d) Project age (years)", "years", False),
    ]
    for suffix, col, label, xlabel, log in panels:
        s = df[col].dropna()
        vals = np.log10(s.replace(0, 0.5)) if log else s
        fig, ax = plt.subplots(figsize=(5.8, 4.2))
        if col == "bus_factor_no_bots":
            bins = np.arange(s.min() - 0.5, s.max() + 1.5, 1)
            ax.hist(s, bins=bins, color=bar_color, edgecolor="white", linewidth=0.8,
                    rwidth=0.9)
            ax.set_xticks(np.arange(s.min(), s.max() + 1, 1))
        else:
            ax.hist(vals, bins=12, color=bar_color, edgecolor="white", linewidth=0.8)

        med = vals.median()
        median_label = f"median={_format_int_space(s.median())}"
        # if col == "num_developers":
        #     median_label = f"median raw={_format_int_space(s.median())}"
        if col == "age_years":
            median_label = f"median={s.median():.1f}"
        ax.axvline(med, color=median_color, linestyle="--", linewidth=1.8,
                   label=median_label)

        # ax.set_title(label, fontsize=12, fontweight="bold")
        ax.set_xlabel(xlabel,fontsize=20)
        ax.set_ylabel("repositories",fontsize=20)
        ax.grid(axis="y", color="0.9", linewidth=0.8)
        ax.set_axisbelow(True)
        if col == "bus_factor_no_bots":
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        if col == "num_developers":
            raw_ticks = np.array([1, 3, 10, 30, 100, 300])
            raw_ticks = raw_ticks[(raw_ticks >= s.min()) & (raw_ticks <= s.max())]
            ax.set_xticks(np.log10(raw_ticks))
            ax.set_xticklabels([str(t) for t in raw_ticks])
        ax.legend(fontsize=12, framealpha=0.95)

        # fig.suptitle(
        #     f"Distribution of {xlabel.lower()} across the n={n} civic tech corpus",
        #     fontsize=12,
        #     fontweight="bold",
        # )
        fig.tight_layout()
        fig.savefig(out / f"fig4_corpus_distributions_colored_{suffix}.png")
        plt.close(fig)

    bf_med = df["bus_factor_no_bots"].median()
    hhi_med = df["hhi_no_bots"].median()
    return (f"Alternative Figure 4a-d. Separate colored distributions of the four "
            f"headline metrics across the n={n} corpus: bus factor, HHI, number of "
            f"developers (log-scaled), and project age. Bars use a single muted color "
            f"and orange dashed lines mark medians; median bus factor "
            f"{_format_int_space(bf_med)}, median HHI {_format_int_space(hhi_med)}.")


def fig5_maturity_split(snap: Path, out: Path) -> str:
    df = _load_repo_chaoss(snap)
    median_age = df["age_years"].median()
    df["maturity"] = np.where(df["age_years"] >= median_age, "Mature", "Young")
    n_mature = int((df["maturity"] == "Mature").sum())
    n_young = int((df["maturity"] == "Young").sum())

    metrics = [
        ("num_developers", "Num developers (log10)", True),
        ("total_commits", "Total commits (log10)", True),
        ("bus_factor_no_bots", "Bus factor (no bots)", False),
        ("hhi_no_bots", "HHI (no bots)", False),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(13, 4))
    caption_bits = []
    for ax, (col, label, log) in zip(axes, metrics):
        s_mature = df[df.maturity == "Mature"][col].dropna().pipe(
            lambda s: np.log10(s.replace(0, 0.5)) if log else s)
        s_young = df[df.maturity == "Young"][col].dropna().pipe(
            lambda s: np.log10(s.replace(0, 0.5)) if log else s)
        ax.boxplot([s_young, s_mature], tick_labels=["Young", "Mature"], showmeans=True,
                   widths=0.6, boxprops=dict(linewidth=1.2),
                   medianprops=dict(linewidth=1.5, color="black"))
        _, p = stats.mannwhitneyu(s_young, s_mature, alternative="two-sided")
        ax.set_title(f"{label}\nMW p = {p:.3f}", fontsize=10)
        ax.tick_params(axis="x", labelsize=10)
        caption_bits.append(f"{col} p={p:.3f}")
    fig.suptitle(f"Project maturity split (median age {median_age:.1f} years; "
                 f"mature n={n_mature}, young n={n_young})", fontsize=12)
    fig.tight_layout()
    fig.savefig(out / "fig5_maturity_split.png")
    plt.close(fig)
    return (f"Figure 5. Maturity split at the corpus median age ({median_age:.1f} years; "
            f"mature n={n_mature}, young n={n_young}). Mann–Whitney comparisons: "
            f"{'; '.join(caption_bits)}. Scale metrics (developers, commits) separate the "
            f"groups while the sustainability metrics (bus factor, HHI) need not — see the "
            f"printed p-values.")


def fig6_contributor_engagement_durations(snap: Path, out: Path) -> str:
    """Show how long non-bot contributor records remain engaged."""
    df = pd.read_csv(snap / "contributor_lifecycles.csv")
    df["is_bot_lifecycle"] = df.apply(_is_lifecycle_bot, axis=1)
    bot_count = int(df["is_bot_lifecycle"].sum())
    df = df[~df["is_bot_lifecycle"]].copy()
    df["duration_days"] = pd.to_numeric(df["duration_days"], errors="coerce")
    df["total_commits"] = pd.to_numeric(df["total_commits"], errors="coerce")
    df = df.dropna(subset=["duration_days", "total_commits"])
    n = len(df)

    buckets = [
        ("1 commit\n(duration 0)", df["total_commits"] == 1),
        ("<=1 week", (df["total_commits"] > 1) & (df["duration_days"] <= 7)),
        ("1-4 weeks", (df["duration_days"] > 7) & (df["duration_days"] <= 28)),
        ("1-3 months", (df["duration_days"] > 28) & (df["duration_days"] <= 92)),
        ("3-12 months", (df["duration_days"] > 92) & (df["duration_days"] <= 365)),
        ("1-5 years", (df["duration_days"] > 365) & (df["duration_days"] <= 365 * 5)),
        (">5 years", df["duration_days"] > 365 * 5),
    ]
    labels = [label for label, _ in buckets]
    counts = np.array([int(mask.sum()) for _, mask in buckets])
    shares = counts / n if n else np.zeros(len(counts))

    colors = [
       '#6f8796'
    ]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    bars = ax.bar(labels, shares, color=colors, edgecolor="white", linewidth=0.8)
    for bar, share, count in zip(bars, shares, counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f"{share * 100:.2f} %\n(n={count:,})",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    ax.set_ylim(0, max(0.6, shares.max() + 0.1))
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
    n_fmt = f"{n:,}".replace(",", " ")
    ax.set_ylabel(f"% of contributor records (n={n_fmt} non-bot)")
    ax.set_title("How long civic-tech contributors stay engaged?",
                 loc="left", fontweight="bold", fontsize=14)
    ax.grid(axis="y", color="0.9", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", labelrotation=0)
    fig.tight_layout()
    fig.savefig(out / "fig6_contributor_engagement_durations.png")
    plt.close(fig)

    single_count = int(counts[0])
    single_share = shares[0] if n else 0
    repo_count = df["repo_full_name"].nunique()
    return (f"Figure 6. Distribution of contributor engagement durations across "
            f"{n:,} non-bot contributor records in {repo_count} repositories, "
            f"excluding {bot_count:,} records detected as bots from lifecycle identity "
            f"fields. The leftmost bar is single-commit contributors — "
            f"{single_share * 100:.2f} % of all records (n={single_count:,}).")


def fig7_weekly_commits_vs_project_age(snap: Path, out: Path) -> str:
    """Plot weekly commit count against project age for repo-week observations."""
    repos = _load_repo_metrics(snap).rename(columns={"full_name": "repo"})
    repos = repos[["repo", "first_commit_date"]]
    repos["first_commit_date"] = pd.to_datetime(repos["first_commit_date"], utc=True)
    weekly = pd.read_csv(snap / "contributor_weekly_activity.csv")
    weekly["is_bot_lifecycle"] = weekly.apply(_is_lifecycle_bot, axis=1)
    bot_rows = int(weekly["is_bot_lifecycle"].sum())
    weekly = weekly[~weekly["is_bot_lifecycle"]].copy()
    weekly["commits"] = pd.to_numeric(weekly["commits"], errors="coerce")
    weekly["week_start"] = pd.to_datetime(weekly["week_start"], utc=True)
    weekly = weekly.dropna(subset=["repo_full_name", "week_start", "commits"])

    df = (
        weekly.groupby(["repo_full_name", "week_start"], as_index=False)["commits"]
        .sum()
        .rename(columns={"repo_full_name": "repo"})
    )
    df = df.merge(repos, on="repo", how="inner")
    df["project_age_years"] = (
        df["week_start"] - df["first_commit_date"]
    ).dt.days / 365.25
    df = df[df["project_age_years"] >= 0].dropna(
        subset=["project_age_years", "commits"]
    )
    n = len(df)

    fig, ax = plt.subplots(figsize=(10, 5.8))
    main_color = "#6f8796"
    line_color = "#d97706"
    ax.scatter(
        df["project_age_years"],
        df["commits"],
        s=8,
        facecolors=main_color,
        edgecolors="none",
        alpha=0.22,
        marker="o",
        label="Single repo-week",
    )
    df["age_bin_year"] = np.floor(df["project_age_years"]).astype(int)
    binned = (
        df.groupby("age_bin_year", as_index=False)
        .agg(
            median_weekly_commits=("commits", "median"),
            repo_weeks=("repo", "count"),
        )
        .query("repo_weeks >= 20")
    )
    if not binned.empty:
        ax.plot(
            binned["age_bin_year"] + 0.5,
            binned["median_weekly_commits"],
            color=line_color,
            marker="D",
            markerfacecolor="white",
            markeredgecolor=line_color,
            markeredgewidth=1.2,
            linewidth=2.4,
            linestyle="-",
            markersize=6,
            label="Median (binned by year)",
        )

    rho, p_value = stats.spearmanr(df["project_age_years"], df["commits"])
    ax.set_yscale("log")
    ax.set_ylim(bottom=0.7)
    ax.set_xlabel("Project age (years)")
    ax.set_ylabel("Weekly commit count (log scale)")
    ax.set_title(
        "Activity rises with project age - among surviving panel projects",
        loc="left",
        color="black",
        fontsize=15,
        fontweight="bold",
        pad=18,
    )
    ax.grid(axis="both", which="major", color="0.86", linewidth=0.8)
    ax.grid(axis="y", which="minor", color="0.92", linewidth=0.6)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("black")
    ax.spines["bottom"].set_color("black")
    ax.tick_params(colors="black")
    ax.xaxis.label.set_color("black")
    ax.yaxis.label.set_color("black")
    ax.legend(
        loc="upper left",
        frameon=True,
        framealpha=1,
        facecolor="white",
        edgecolor="0.6",
        fontsize=11,
        markerscale=1.4,
        handlelength=2.0,
    )
    fig.tight_layout()
    fig.savefig(out / "fig7_weekly_commits_vs_project_age.png")
    plt.close(fig)

    median_age = df["project_age_years"].median()
    median_weekly = df["commits"].median()
    repo_count = df["repo"].nunique()
    return (f"Figure 7. Weekly commit count vs. project age across {n:,} non-bot "
            f"repo-week observations from {repo_count} repositories, excluding "
            f"{bot_rows:,} bot-like weekly contributor rows. The orange diamond line shows "
            f"median weekly commits binned by completed project age year. Median "
            f"repo-week age is {median_age:.1f} years and median weekly commit count "
            f"is {median_weekly:.0f}; Spearman "
            f"rho = {rho:.3f}, p = {p_value:.3f}.")



def fig10_weekly_commit_health_by_theme(snap: Path, out: Path) -> str:
    """Scatter median weekly commits against health percentage using theme labels."""
    theme_csv = snap / "repo_metrics_with_theme.csv"
    if not theme_csv.exists():
        raise FileNotFoundError(f"Figure 10 theme CSV not found: {theme_csv}")

    df = pd.read_csv(theme_csv)
    weekly = pd.read_csv(snap / "contributor_weekly_activity.csv")
    weekly_summary = (
        weekly.groupby(["repo_full_name", "week_start"], as_index=False)["commits"]
        .sum()
        .groupby("repo_full_name", as_index=False)
        .agg(median_weekly_commits=("commits", "median"))
        .rename(columns={"repo_full_name": "full_name"})
    )
    df = df.merge(weekly_summary, on="full_name", how="left")

    required = {"full_name", "Theme", "median_weekly_commits", "health_percentage"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Theme scatter input is missing required columns: {sorted(missing)}")

    df["median_weekly_commits"] = pd.to_numeric(
        df["median_weekly_commits"], errors="coerce"
    )
    df["health_percentage"] = pd.to_numeric(df["health_percentage"], errors="coerce")
    sub = df.dropna(subset=["Theme", "median_weekly_commits", "health_percentage"]).copy()
    sub["Theme"] = sub["Theme"].astype(str).str.strip()
    sub = sub[sub["Theme"].ne("")]
    n = len(sub)

    theme_colors = {
        "Open Data": "#1f77b4",
        "Civil society engagement": "#ff7f0e",
        "Document Management": "#2ca02c",
        "Environmental Protection": "#b2182b",
        "Social Good": "#707070",
    }
    theme_order = [
        "Open Data",
        "Civil society engagement",
        "Document Management",
        "Environmental Protection",
        "Social Good",
    ]
    theme_order += sorted(set(sub["Theme"]) - set(theme_order))

    fig, ax = plt.subplots(figsize=(8, 5.6))
    for theme in theme_order:
        group = sub[sub["Theme"] == theme]
        if group.empty:
            continue
        hull_group = group[group["median_weekly_commits"] > 0].copy()
        hull_points = np.column_stack([
            np.log10(hull_group["median_weekly_commits"].to_numpy()),
            hull_group["health_percentage"].to_numpy(),
        ])
        hull_points = np.unique(hull_points, axis=0)
        if len(hull_points) >= 3:
            try:
                hull = ConvexHull(hull_points)
            except QhullError:
                hull = None
            if hull is not None:
                vertices = hull_points[hull.vertices]
                vertices = np.vstack([vertices, vertices[0]])
                ax.fill(
                    10 ** vertices[:, 0],
                    vertices[:, 1],
                    color=theme_colors.get(theme, "0.5"),
                    alpha=0.10,
                    linewidth=0,
                    zorder=1,
                )
                ax.plot(
                    10 ** vertices[:, 0],
                    vertices[:, 1],
                    color=theme_colors.get(theme, "0.5"),
                    alpha=0.75,
                    linewidth=1.4,
                    zorder=2,
                )
        ax.scatter(
            group["median_weekly_commits"],
            group["health_percentage"],
            s=80,
            alpha=0.78,
            marker="o",
            edgecolors="black",
            linewidths=0.5,
            color=theme_colors.get(theme, "0.5"),
            label=f"{theme} (n={len(group)})",
            zorder=3,
        )

    rho, p_value = stats.spearmanr(
        sub["median_weekly_commits"], sub["health_percentage"]
    )
    ax.set_xscale("log")
    ax.set_xlabel("Median weekly commits (log scale)")
    ax.set_ylabel("Repository health score (%)")
    ax.set_title(
        "Weekly activity vs. repository health by theme",
        loc="left",
        fontweight="bold",
        fontsize=14,
        pad=12,
    )
    ax.grid(axis="both", which="major", color="0.88", linewidth=0.8)
    ax.grid(axis="x", which="minor", color="0.93", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="best", framealpha=0.95, fontsize=9)
    fig.tight_layout()
    fig.savefig(out / "fig10_weekly_commit_health_by_theme.png")
    plt.close(fig)

    return (
        f"Figure 10. Median weekly commits vs. repository health percentage for "
        f"n={n} repositories with theme labels. Points are repositories and "
        f"color encodes theme; translucent polygons show per-theme convex hulls "
        f"in log-x plot coordinates. Across all repositories, Spearman rho = "
        f"{rho:.3f}, p = {p_value:.3f}."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", nargs="?", default=str(DEFAULT_SNAPSHOT))
    args = parser.parse_args()

    snap = Path(args.snapshot).resolve()
    if not snap.exists():
        print(f"ERROR: snapshot not found: {snap}", file=sys.stderr)
        return 1
    out = snap / "figures"
    out.mkdir(exist_ok=True)

    captions = []
    captions.append(fig1_busfactor_vs_hhi(snap, out))
    captions.append(fig2_effort_gini(snap, out))
    captions.append(fig3_burstiness_vs_stale(snap, out))
    captions.append(fig4_corpus_distributions(snap, out))
    captions.append(fig4_corpus_distributions_colored(snap, out))
    captions.append(fig5_maturity_split(snap, out))
    captions.append(fig6_contributor_engagement_durations(snap, out))
    captions.append(fig7_weekly_commits_vs_project_age(snap, out))
    captions.append(fig10_weekly_commit_health_by_theme(snap, out))

    print(f"\nGenerated {len(captions)} figures in {out}/\n")
    for c in captions:
        print(c)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
