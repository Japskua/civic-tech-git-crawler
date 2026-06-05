"""Generate AI-usage figures for the paper.

Reads a crawler snapshot (ai_usage.csv, repo_metrics.csv, and
ai_usage_analysis/adoption_timeline.csv) and writes PNGs to
<snapshot>/ai_usage_analysis/figures/:

  fig_adoption_timeline.png   — new + cumulative AI-dev adopters by quarter
  fig_community_adoption.png  — AI-dev adoption rate by civic-tech community
  fig_adopter_vs_nonadopter.png — commits & developers, adopters vs non (boxplots)
  fig_tool_frequency.png      — dev-tool prevalence (repos per tool)

Usage:
    uv run python scripts/ai_usage_figures.py <snapshot-dir>

Captions (suggested) are printed to stdout for pasting into the paper.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ACCENT = "#2563eb"   # blue
ACCENT2 = "#9333ea"  # purple
GREY = "#9ca3af"


def community(repo: str) -> str:
    o = repo.split("/")[0].lower()
    if o.startswith("codeforamerica") or o == "civiform":
        return "US — CfA / CiviForm"
    if o == "meshtastic":
        return "Meshtastic"
    if o == "codeforafrica":
        return "Code for Africa"
    if o == "codeforjapan":
        return "Code for Japan"
    if o.startswith("civictechwr") or o in ("bikespace", "choruslabs", "civic-dashboard"):
        return "Canada — CivicTechWR"
    if o.startswith(("codefor", "oklab", "openlegaldata", "code-for")):
        return "Germany — OK Lab"
    return "Other"


def fig_timeline(tl: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = range(len(tl))
    ax.bar(x, tl["repos_first_seen"], color=ACCENT, alpha=0.85, label="New adopters (quarter)")
    ax.set_xticks(list(x))
    ax.set_xticklabels(tl["quarter"], rotation=0)
    ax.set_ylabel("New adopters per quarter", color=ACCENT)
    ax.set_ylim(0, max(tl["repos_first_seen"].max() + 1, 4))
    ax2 = ax.twinx()
    ax2.plot(x, tl["cumulative"], color=ACCENT2, marker="o", lw=2, label="Cumulative adopters")
    ax2.set_ylabel("Cumulative adopters", color=ACCENT2)
    ax2.set_ylim(0, tl["cumulative"].max() + 2)
    for xi, c in zip(x, tl["cumulative"]):
        ax2.annotate(str(int(c)), (xi, c), textcoords="offset points", xytext=(0, 6),
                     ha="center", fontsize=8, color=ACCENT2)
    ax.set_title("AI-assisted-development adoption over time (first datable signal)")
    fig.tight_layout()
    fig.savefig(out / "fig_adoption_timeline.png", dpi=150)
    plt.close(fig)


def fig_community(ai: pd.DataFrame, out: Path) -> None:
    ai = ai.copy()
    ai["grp"] = ai["repo_full_name"].map(community)
    g = ai.groupby("grp").agg(repos=("dev", "size"), adopters=("dev", "sum")).reset_index()
    g["rate"] = g["adopters"] / g["repos"] * 100
    g = g.sort_values("rate")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = [ACCENT if r >= 50 else GREY for r in g["rate"]]
    ax.barh(g["grp"], g["rate"], color=colors)
    ax.set_xlabel("AI-assisted-development adoption rate (%)")
    ax.set_xlim(0, 108)
    for y, (_, row) in enumerate(g.iterrows()):
        ax.annotate(f"{int(row.adopters)}/{int(row.repos)} ({row.rate:.0f}%)",
                    (row.rate + 1, y), va="center", fontsize=8.5)
    ax.set_title("AI adoption varies by civic-tech community")
    fig.tight_layout()
    fig.savefig(out / "fig_community_adoption.png", dpi=150)
    plt.close(fig)


def fig_boxplots(
    ai: pd.DataFrame, rm: pd.DataFrame, cmp_p: dict, out: Path,
    dev_mode: str = "linear", fname: str = "fig_adopter_vs_nonadopter.png",
) -> None:
    """Adopter-vs-non boxplots. `dev_mode` controls the Developers panel y-axis:
    'linear' (full range), 'log', or 'clip' (zoom to the bulk; off-scale points
    annotated). The Total-commits panel is always log-scaled."""
    m = ai.merge(rm.rename(columns={"full_name": "repo_full_name"}), on="repo_full_name", how="left")
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.5))
    # (column, label, is_developers_panel)
    specs = [("total_commits", "Total commits", False), ("num_developers", "Developers", True)]
    for ax, (col, label, is_dev) in zip(axes, specs):
        a = pd.to_numeric(m.loc[m["dev"], col], errors="coerce").dropna()
        b = pd.to_numeric(m.loc[~m["dev"], col], errors="coerce").dropna()
        bp = ax.boxplot([a, b], patch_artist=True, widths=0.55, showfliers=False)
        ax.set_xticks([1, 2])
        ax.set_xticklabels(["AI\nadopters", "Non-\nadopters"])
        for patch, c in zip(bp["boxes"], [ACCENT, GREY]):
            patch.set_facecolor(c)
            patch.set_alpha(0.6)
        for i, data in enumerate([a, b], start=1):
            xj = np.random.default_rng(i).normal(i, 0.05, size=len(data))
            ax.scatter(xj, data, s=12, color="#374151", alpha=0.5, zorder=3)
        mode_note = ""
        if not is_dev:  # commits panel: always log
            ax.set_yscale("log")
        elif dev_mode == "log":
            ax.set_yscale("log")
        elif dev_mode == "clip":
            allv = pd.concat([a, b])
            cap = max(float(np.nanpercentile(allv, 90)), float(b.max()) * 1.1)
            ax.set_ylim(0, cap)
            off = int((a > cap).sum() + (b > cap).sum())
            if off:
                mode_note = f"\n({off} point(s) off-scale, max {int(allv.max())})"
        ax.set_ylabel(label)
        p = cmp_p.get(col)
        ptxt = f"Mann-Whitney p = {p:.3f}" if p is not None else ""
        ax.set_title(f"{label}\n{ptxt}{mode_note}", fontsize=10)
    fig.suptitle("AI adopters are larger and busier (medians differ; correlational)", fontsize=11)
    fig.tight_layout()
    fig.savefig(out / fname, dpi=150)
    plt.close(fig)


def fig_tools(ai: pd.DataFrame, out: Path) -> None:
    tools: Counter = Counter()
    for v in ai.loc[ai["dev"], "dev_ai_tools"].dropna():
        for t in str(v).split(";"):
            if t:
                tools[t] += 1
    items = sorted(tools.items(), key=lambda x: x[1])
    fig, ax = plt.subplots(figsize=(8, 4.5))
    labels = [k for k, _ in items]
    vals = [v for _, v in items]
    ax.barh(labels, vals, color=ACCENT)
    for y, v in enumerate(vals):
        ax.annotate(str(v), (v + 0.1, y), va="center", fontsize=9)
    ax.set_xlabel("Repositories")
    ax.set_xlim(0, max(vals) + 2)
    ax.set_title("AI development tools by prevalence (repos)")
    fig.tight_layout()
    fig.savefig(out / "fig_tool_frequency.png", dpi=150)
    plt.close(fig)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: ai_usage_figures.py <snapshot-dir>", file=sys.stderr)
        return 1
    snap = Path(sys.argv[1]).resolve()
    analysis = snap / "ai_usage_analysis"
    out = analysis / "figures"
    out.mkdir(parents=True, exist_ok=True)

    ai = pd.read_csv(snap / "ai_usage.csv")
    ai["dev"] = ai["dev_ai_detected"].astype(str).str.lower().eq("true")
    rm = pd.read_csv(snap / "repo_metrics.csv")
    tl = pd.read_csv(analysis / "adoption_timeline.csv")
    try:
        cmp_df = pd.read_csv(analysis / "adopter_vs_nonadopter.csv")
        cmp_p = {r.metric: r.mannwhitney_p for r in cmp_df.itertuples()
                 if isinstance(r.mannwhitney_p, float)}
    except Exception:  # noqa: BLE001
        cmp_p = {}

    fig_timeline(tl, out)
    fig_community(ai, out)
    fig_boxplots(ai, rm, cmp_p, out, dev_mode="linear",
                 fname="fig_adopter_vs_nonadopter.png")
    fig_boxplots(ai, rm, cmp_p, out, dev_mode="log",
                 fname="fig_adopter_vs_nonadopter_devlog.png")
    fig_boxplots(ai, rm, cmp_p, out, dev_mode="clip",
                 fname="fig_adopter_vs_nonadopter_devclip.png")
    fig_tools(ai, out)

    print(f"Figures written to {out.relative_to(snap.parent)}:")
    for f in sorted(out.glob("*.png")):
        print(f"  {f.name}")
    print("\nSuggested captions:")
    print("  fig_adoption_timeline:  'First datable AI-assisted-development signal per "
          "project, by quarter. AI adoption in the corpus is a 2025-2026 phenomenon.'")
    print("  fig_community_adoption: 'AI-assisted-development adoption rate by civic-tech "
          "community (n adopters / n repos). Adoption is highly uneven across communities.'")
    print("  fig_adopter_vs_nonadopter: 'Total commits (log scale) and developer count for "
          "AI adopters vs non-adopters. Adopters are larger and busier; the association is "
          "correlational, not causal.'")
    print("  fig_tool_frequency:     'AI development tools by number of repositories. Claude "
          "Code and GitHub Copilot dominate the toolchain.'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
