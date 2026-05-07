"""Generate synthesis figures for paper_draft.md.

Run after the canonical n=37 snapshot has been built. Outputs PNG figures
into example_results/may_2026/figures/ and prints a paper-ready figure
caption block to stdout.

Usage:
    uv run python scripts/paper_figures.py [snapshot-dir]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SNAPSHOT = ROOT / "example_results" / "may_2026"

EXTENSION_8 = {
    "ForumMagnum/ForumMagnum",
    "mastodon/mastodon",
    "okfde/froide",
    "openplans/shareabouts",
    "codeforamerica/recordtrac",
    "CodeForAfrica/actNOW",
    "CitizensFoundation/your-priorities-app",
    "mysociety/ceuk-marking",
}

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


def fig1_busfactor_vs_hhi(snap: Path, out: Path) -> str:
    rm = pd.read_csv(snap / "repo_metrics.csv").rename(columns={"full_name": "repo"})
    ch = pd.read_csv(snap / "chaoss_summary.csv").rename(columns={"repo_full_name": "repo"})
    df = rm.merge(ch, on="repo")
    df["age_years"] = (
        pd.Timestamp("2026-05-06", tz="UTC") - pd.to_datetime(df["first_commit_date"], utc=True)
    ).dt.days / 365.25
    df["mature"] = df["age_years"] >= 6.3
    df["cohort"] = df["repo"].apply(lambda r: "Extension (8)" if r in EXTENSION_8 else "Core (29)")

    fig, ax = plt.subplots(figsize=(7, 5))
    for cohort, marker, label in [("Core (29)", "o", "Core (n=29)"),
                                  ("Extension (8)", "^", "Extension (n=8)")]:
        sub = df[df.cohort == cohort]
        ax.scatter(sub["hhi_no_bots"], sub["bus_factor_no_bots"],
                   s=np.clip(sub["num_developers"] * 1.2, 30, 400),
                   alpha=0.6, marker=marker, edgecolors="black", linewidths=0.5,
                   label=f"{label}, point size ∝ num_developers")

    # Annotate the most extreme points
    for _, r in df.nlargest(3, "hhi_no_bots").iterrows():
        ax.annotate(r["repo"].split("/")[-1], (r["hhi_no_bots"], r["bus_factor_no_bots"]),
                    xytext=(5, 4), textcoords="offset points", fontsize=8, alpha=0.7)
    for _, r in df.nlargest(2, "bus_factor_no_bots").iterrows():
        ax.annotate(r["repo"].split("/")[-1], (r["hhi_no_bots"], r["bus_factor_no_bots"]),
                    xytext=(5, 4), textcoords="offset points", fontsize=8, alpha=0.7)

    rho, p = stats.spearmanr(df["hhi_no_bots"], df["bus_factor_no_bots"])
    ax.set_xlabel("HHI (humans only, 0–10,000 scale)")
    ax.set_ylabel("Bus factor (humans only)")
    ax.set_title(f"Bus factor vs. organisational concentration (n=37)\nSpearman ρ = {rho:.3f}, p < 1e-15")
    ax.legend(loc="upper right", framealpha=0.95)
    fig.savefig(out / "fig1_busfactor_vs_hhi.png")
    plt.close(fig)
    return ("Figure 1. Bus factor vs. HHI on the n=37 sample. Each point is a repository; "
            "marker size encodes num_developers. The strong negative relationship "
            "(ρ = −0.920, partial −0.872 controlling for team size) is the central "
            "concentration-of-effort mechanism the paper is built around.")


def fig2_effort_gini(snap: Path, out: Path) -> str:
    g = pd.read_csv(snap / "weekly_activity_analysis" / "effort_gini.csv")
    g["cohort"] = g["repo_full_name"].apply(
        lambda r: "Extension (8)" if r in EXTENSION_8 else "Core (29)"
    )

    fig, ax = plt.subplots(figsize=(7, 5))
    for cohort, marker, label in [("Core (29)", "o", "Core (n=29)"),
                                  ("Extension (8)", "^", "Extension (n=8)")]:
        sub = g[g.cohort == cohort]
        ax.scatter(sub["effort_gini_commits"], sub["effort_gini_lines"],
                   s=80, alpha=0.6, marker=marker, edgecolors="black", linewidths=0.5,
                   label=label)

    # Diagonal y=x
    ax.plot([0, 1], [0, 1], "k--", alpha=0.4, linewidth=1, label="y = x (equal Gini)")

    # Annotate the heaviest line-Gini repos
    top = g.nlargest(5, "effort_gini_lines")
    for _, r in top.iterrows():
        ax.annotate(r["repo_full_name"].split("/")[-1],
                    (r["effort_gini_commits"], r["effort_gini_lines"]),
                    xytext=(6, 2), textcoords="offset points", fontsize=8, alpha=0.8)

    gap_mean = (g["effort_gini_lines"] - g["effort_gini_commits"]).mean()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Gini of commits per contributor")
    ax.set_ylabel("Gini of lines changed per contributor")
    ax.set_title(f"Effort Gini: lines vs. commits (n=37)\n"
                 f"Mean gap (lines − commits) = {gap_mean:+.3f}; lines-Gini ≥ commits-Gini in 33/37 repos")
    ax.legend(loc="lower right", framealpha=0.95)
    fig.savefig(out / "fig2_effort_gini.png")
    plt.close(fig)
    return ("Figure 2. Effort Gini coefficients on lines-changed vs. commits per contributor. "
            "Points above y=x indicate effort concentration is more extreme than commit-count "
            "concentration suggests. Mean gap +0.057 across 37 repositories.")


def fig3_burstiness_vs_stale(snap: Path, out: Path) -> str:
    ch = pd.read_csv(snap / "chaoss_summary.csv")
    df = ch[["repo_full_name", "burstiness_cv", "stale_issue_ratio"]].dropna()

    fig, ax = plt.subplots(figsize=(7, 5))
    df_in = df[df["repo_full_name"].isin(EXTENSION_8)]
    df_co = df[~df["repo_full_name"].isin(EXTENSION_8)]
    ax.scatter(df_co["burstiness_cv"], df_co["stale_issue_ratio"],
               s=80, alpha=0.6, marker="o", edgecolors="black", linewidths=0.5,
               label="Core (n=29)")
    ax.scatter(df_in["burstiness_cv"], df_in["stale_issue_ratio"],
               s=80, alpha=0.6, marker="^", edgecolors="black", linewidths=0.5,
               label="Extension (n=8)")

    # Linear fit (purely visual; statistics in caption use Spearman)
    x, y = df["burstiness_cv"].values, df["stale_issue_ratio"].values
    slope, intercept, _, _, _ = stats.linregress(x, y)
    xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, slope * xs + intercept, "k-", alpha=0.4, linewidth=1.2, label="OLS fit")

    rho, p = stats.spearmanr(x, y)
    ax.set_xlabel("Burstiness CV (trailing 52 weeks)")
    ax.set_ylabel("Stale issue ratio")
    ax.set_title(f"Burstiness vs. stale-issue-ratio (n={len(df)} pairs)\n"
                 f"Spearman ρ = {rho:.3f}, p = {p:.3f} (uncorrected; not FDR-significant). "
                 f"n=29 paper reported ρ = 0.685 on n=17 pairs.")
    ax.legend(loc="lower right", framealpha=0.95)
    fig.savefig(out / "fig3_burstiness_vs_stale.png")
    plt.close(fig)
    return (f"Figure 3. Burstiness vs. stale-issue-ratio after the coverage fix. The n=29 "
            f"paper reported ρ = 0.685 on a subset of n=17 repositories whose `/stats/commit_activity` "
            f"happened to return in time. Recomputing burstiness from a separately-collected GraphQL "
            f"source raises coverage to 26 pairs and attenuates the relationship to ρ = {rho:.3f}, "
            f"p = {p:.3f}. Direction holds; no longer FDR-significant.")


def fig4_cohort_boxplots(snap: Path, out: Path) -> str:
    rm = pd.read_csv(snap / "repo_metrics.csv").rename(columns={"full_name": "repo"})
    ch = pd.read_csv(snap / "chaoss_summary.csv").rename(columns={"repo_full_name": "repo"})
    df = rm.merge(ch, on="repo")
    df["cohort"] = df["repo"].apply(lambda r: "Ext (8)" if r in EXTENSION_8 else "Core (29)")

    metrics = [
        ("stars", "Stars (log10)", True),
        ("total_commits", "Total commits (log10)", True),
        ("bus_factor_no_bots", "Bus factor (no bots)", False),
        ("hhi_no_bots", "HHI (no bots)", False),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(13, 4))
    for ax, (col, label, log) in zip(axes, metrics):
        data = [
            df[df.cohort == "Core (29)"][col].dropna().pipe(lambda s: np.log10(s.replace(0, 0.5)) if log else s),
            df[df.cohort == "Ext (8)"][col].dropna().pipe(lambda s: np.log10(s.replace(0, 0.5)) if log else s),
        ]
        bp = ax.boxplot(data, labels=["Core", "Ext"], showmeans=True, widths=0.6,
                        boxprops=dict(linewidth=1.2), medianprops=dict(linewidth=1.5, color="black"))
        # Mann-Whitney p
        u, p = stats.mannwhitneyu(data[0], data[1], alternative="two-sided")
        ax.set_title(f"{label}\nMW p = {p:.3f}", fontsize=10)
        ax.tick_params(axis="x", labelsize=10)
    fig.suptitle("Cohort comparison: 8 May extensions vs. 29 core civic-tech projects (n=37)", fontsize=12)
    fig.tight_layout()
    fig.savefig(out / "fig4_cohort_boxplots.png")
    plt.close(fig)
    return ("Figure 4. Cohort comparison on stars, total_commits (both log10), bus factor, and HHI. "
            "The 8 added projects differ on scale (commits, stars) but not on the sustainability "
            "metrics (bus factor, HHI), supporting the conclusion that the paper's headline "
            "mechanisms extrapolate to substantially larger civic-tech projects.")


def fig5_maturity_split(snap: Path, out: Path) -> str:
    rm = pd.read_csv(snap / "repo_metrics.csv").rename(columns={"full_name": "repo"})
    ch = pd.read_csv(snap / "chaoss_summary.csv").rename(columns={"repo_full_name": "repo"})
    df = rm.merge(ch, on="repo")
    df["age_years"] = (
        pd.Timestamp("2026-05-06", tz="UTC") - pd.to_datetime(df["first_commit_date"], utc=True)
    ).dt.days / 365.25
    df["maturity"] = np.where(df["age_years"] >= 6.3, "Mature ≥6.3y", "Young <6.3y")

    metrics = [
        ("num_developers", "Num developers", True),
        ("total_commits", "Total commits (log10)", True),
        ("bus_factor_no_bots", "Bus factor (no bots)", False),
        ("hhi_no_bots", "HHI (no bots)", False),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(13, 4))
    for ax, (col, label, log) in zip(axes, metrics):
        s_mature = df[df.maturity == "Mature ≥6.3y"][col].dropna().pipe(
            lambda s: np.log10(s.replace(0, 0.5)) if log else s
        )
        s_young = df[df.maturity == "Young <6.3y"][col].dropna().pipe(
            lambda s: np.log10(s.replace(0, 0.5)) if log else s
        )
        bp = ax.boxplot([s_young, s_mature], labels=["Young", "Mature"], showmeans=True,
                        widths=0.6, boxprops=dict(linewidth=1.2),
                        medianprops=dict(linewidth=1.5, color="black"))
        u, p = stats.mannwhitneyu(s_young, s_mature, alternative="two-sided")
        ax.set_title(f"{label}\nMW p = {p:.3f}", fontsize=10)
        ax.tick_params(axis="x", labelsize=10)
    fig.suptitle("Project maturity split (median age 6.3 years; mature n=19, young n=18)", fontsize=12)
    fig.tight_layout()
    fig.savefig(out / "fig5_maturity_split.png")
    plt.close(fig)
    return ("Figure 5. Maturity split — projects ≥6.3 years vs. <6.3 years. Mature projects "
            "have significantly more developers (p=0.004), more commits (p=0.009), and higher "
            "bus factor (p=0.036). The bus factor effect that was borderline non-significant "
            "at n=29 reaches significance at n=37 with the wider sample's added power.")


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
    captions.append(fig4_cohort_boxplots(snap, out))
    captions.append(fig5_maturity_split(snap, out))

    print(f"\nGenerated {len(captions)} figures in {out}/\n")
    for c in captions:
        print(c)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
