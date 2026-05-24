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
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SNAPSHOT = ROOT / "datasets" / "2026_05"

# Reference date for age computation (crawl completion).
CRAWL_DATE = pd.Timestamp("2026-05-24", tz="UTC")

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


def _load_repo_chaoss(snap: Path) -> pd.DataFrame:
    rm = pd.read_csv(snap / "repo_metrics.csv").rename(columns={"full_name": "repo"})
    ch = pd.read_csv(snap / "chaoss_summary.csv").rename(columns={"repo_full_name": "repo"})
    df = rm.merge(ch, on="repo")
    df["age_years"] = (
        CRAWL_DATE - pd.to_datetime(df["first_commit_date"], utc=True)
    ).dt.days / 365.25
    return df


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
        ("hhi_no_bots", "HHI (no bots, 0–10,000)", False),
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
                   label=f"median {s.median():.0f}" if not log else f"median {s.median():.0f}")
        ax.set_title(label, fontsize=10)
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
            f"dominated by highly concentrated projects — median bus factor {bf_med:.0f} and "
            f"median HHI {hhi_med:.0f} — with a long tail of larger, more collaborative repositories.")


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
        ax.boxplot([s_young, s_mature], labels=["Young", "Mature"], showmeans=True,
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
    captions.append(fig5_maturity_split(snap, out))

    print(f"\nGenerated {len(captions)} figures in {out}/\n")
    for c in captions:
        print(c)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
