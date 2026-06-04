"""AI-usage analysis over a crawler snapshot.

Reads ai_usage.csv / ai_signals.csv (plus repo_metrics, chaoss_summary) and
produces, under <snapshot>/ai_usage_analysis/:

- adoption_summary.csv        — corpus-level adoption counts/rates
- tool_frequency.csv          — dev-tool prevalence (repos per tool)
- provider_frequency.csv      — product-LLM provider prevalence
- signal_source_breakdown.csv — repos detected per evidence source + strength tier
- adoption_timeline.csv        — first AI-dev signal by calendar quarter
- adopter_vs_nonadopter.csv    — metric comparison (Mann-Whitney U)
- summary.md                   — human-readable digest

Usage:
    uv run python scripts/ai_usage_analysis.py <snapshot-dir>

Caveat: AI-usage detection is a LOWER BOUND (see the dataset README). With n=57
the comparisons are exploratory and correlational, not causal — AI tooling
co-varies with project recency/activity.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import pandas as pd

try:
    from scipy.stats import mannwhitneyu
except Exception:  # noqa: BLE001
    mannwhitneyu = None

# Evidence strength tiers (mirrors the README guidance).
SOURCE_TIER = {
    "file": "strong",
    "commit_trailer": "strong",
    "commit_author": "strong",
    "pr_author": "strong",
    "workflow": "medium",
    "bot_comment": "medium",
    "dependency": "medium",
    "pr_body": "medium",
    "topic": "weak",
}

# Metrics compared between AI-dev adopters and non-adopters.
COMPARE_METRICS = [
    ("total_commits", "repo_metrics"),
    ("num_developers", "repo_metrics"),
    ("stars", "repo_metrics"),
    ("health_percentage", "repo_metrics"),
    ("age_years", "derived"),
    ("bus_factor_no_bots", "chaoss"),
]


def _split(series: pd.Series) -> list[str]:
    out: list[str] = []
    for v in series.dropna():
        out += [x for x in str(v).split(";") if x]
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: ai_usage_analysis.py <snapshot-dir>", file=sys.stderr)
        return 1
    snap = Path(sys.argv[1]).resolve()
    outdir = snap / "ai_usage_analysis"
    outdir.mkdir(exist_ok=True)

    ai = pd.read_csv(snap / "ai_usage.csv")
    sig = pd.read_csv(snap / "ai_signals.csv")
    rm = pd.read_csv(snap / "repo_metrics.csv").rename(columns={"full_name": "repo_full_name"})
    try:
        ch = pd.read_csv(snap / "chaoss_summary.csv")
    except FileNotFoundError:
        ch = pd.DataFrame(columns=["repo_full_name"])

    for col in ("dev_ai_detected", "product_llm_detected"):
        ai[col] = ai[col].astype(str).str.lower().eq("true")

    n = len(ai)
    n_dev = int(ai["dev_ai_detected"].sum())
    n_prod = int(ai["product_llm_detected"].sum())

    # --- adoption summary ---------------------------------------------------
    adoption = pd.DataFrame(
        [
            ("repos_total", n, ""),
            ("dev_ai_detected", n_dev, f"{n_dev/n:.1%}"),
            ("product_llm_detected", n_prod, f"{n_prod/n:.1%}"),
            ("any_ai", int((ai["dev_ai_detected"] | ai["product_llm_detected"]).sum()),
             f"{(ai['dev_ai_detected'] | ai['product_llm_detected']).mean():.1%}"),
            ("dev_with_commit_evidence",
             int((ai["ai_coauthored_commit_count"] + ai["ai_authored_commit_count"] > 0).sum()), ""),
            ("dev_with_agent_prs", int((ai["ai_agent_pr_count"] > 0).sum()), ""),
            ("dev_with_ci_agent", int(ai["ci_ai_workflows"].fillna("").astype(bool).sum()), ""),
        ],
        columns=["metric", "count", "rate"],
    )
    adoption.to_csv(outdir / "adoption_summary.csv", index=False)

    # --- tool / provider frequency -----------------------------------------
    tools = Counter(_split(ai.loc[ai["dev_ai_detected"], "dev_ai_tools"]))
    tool_freq = pd.DataFrame(sorted(tools.items(), key=lambda x: -x[1]),
                             columns=["tool", "repos"])
    tool_freq.to_csv(outdir / "tool_frequency.csv", index=False)

    provs = Counter(_split(ai.loc[ai["product_llm_detected"], "product_llm_providers"]))
    prov_freq = pd.DataFrame(sorted(provs.items(), key=lambda x: -x[1]),
                             columns=["provider", "repos"])
    prov_freq.to_csv(outdir / "provider_frequency.csv", index=False)

    # --- signal source breakdown (repos per source + tier) -----------------
    src = (
        sig.groupby("source")["repo_full_name"].nunique()
        .rename("repos").reset_index()
    )
    src["tier"] = src["source"].map(SOURCE_TIER).fillna("?")
    src = src.sort_values(["tier", "repos"], ascending=[True, False])
    src.to_csv(outdir / "signal_source_breakdown.csv", index=False)

    # --- adoption timeline (first dev-AI signal by quarter) ----------------
    fd = pd.to_datetime(ai.loc[ai["dev_ai_detected"], "first_dev_ai_date"],
                        errors="coerce", utc=True).dropna()
    if len(fd):
        tl = fd.dt.to_period("Q").astype(str).value_counts().sort_index()
        tl_df = tl.rename_axis("quarter").reset_index(name="repos_first_seen")
        tl_df["cumulative"] = tl_df["repos_first_seen"].cumsum()
    else:
        tl_df = pd.DataFrame(columns=["quarter", "repos_first_seen", "cumulative"])
    tl_df.to_csv(outdir / "adoption_timeline.csv", index=False)

    # --- adopter vs non-adopter comparison ---------------------------------
    merged = ai.merge(rm, on="repo_full_name", how="left")
    if "bus_factor_no_bots" in ch.columns:
        merged = merged.merge(ch[["repo_full_name", "bus_factor_no_bots"]],
                              on="repo_full_name", how="left")
    # derive project age in years from first_commit_date
    fc = pd.to_datetime(merged.get("first_commit_date"), errors="coerce", utc=True)
    now = pd.Timestamp("2026-06-04", tz="UTC")
    merged["age_years"] = (now - fc).dt.days / 365.25

    rows = []
    grp = merged["dev_ai_detected"]
    for metric, _src in COMPARE_METRICS:
        if metric not in merged.columns:
            continue
        a = pd.to_numeric(merged.loc[grp, metric], errors="coerce").dropna()
        b = pd.to_numeric(merged.loc[~grp, metric], errors="coerce").dropna()
        if len(a) < 3 or len(b) < 3:
            continue
        p = ""
        if mannwhitneyu is not None:
            try:
                _, p = mannwhitneyu(a, b, alternative="two-sided")
                p = round(float(p), 4)
            except Exception:  # noqa: BLE001
                p = ""
        rows.append({
            "metric": metric,
            "adopter_median": round(float(a.median()), 2),
            "nonadopter_median": round(float(b.median()), 2),
            "adopter_n": len(a),
            "nonadopter_n": len(b),
            "mannwhitney_p": p,
        })
    cmp_df = pd.DataFrame(rows)
    cmp_df.to_csv(outdir / "adopter_vs_nonadopter.csv", index=False)

    # --- markdown digest ----------------------------------------------------
    def md_table(df: pd.DataFrame, empty: str = "_none_") -> str:
        if df is None or len(df) == 0:
            return empty
        try:
            return df.to_markdown(index=False)
        except Exception:  # noqa: BLE001 — tabulate not installed; plain fallback
            return "```\n" + df.to_string(index=False) + "\n```"

    top_dev = ai.loc[ai["dev_ai_detected"]].copy()
    top_dev["ai_commits"] = top_dev["ai_coauthored_commit_count"] + top_dev["ai_authored_commit_count"]
    top_dev = top_dev.sort_values("ai_commits", ascending=False).head(8)

    md = [
        f"# AI-usage analysis — {snap.name}\n",
        "> **AI-usage detection measures a lower bound** (disclosed/configured/automated "
        f"traces only). With n={n} the comparisons below are exploratory and "
        "**correlational, not causal** — AI tooling co-varies with project recency and activity.\n",
        "## Adoption\n",
        f"- **{n_dev}/{n} ({n_dev/n:.0%})** repos show **AI-assisted development**",
        f"- **{n_prod}/{n} ({n_prod/n:.0%})** repos **ship an LLM product feature**\n",
        "## Dev tools (repos)\n",
        md_table(tool_freq),
        "\n## Product LLM providers (repos)\n",
        md_table(prov_freq),
        "\n## Evidence sources (repos, by strength tier)\n",
        md_table(src),
        "\n## Adoption timeline (first AI-dev signal)\n",
        md_table(tl_df, "_no datable signals_"),
        "\n## Adopters vs non-adopters (medians; Mann-Whitney U)\n",
        md_table(cmp_df, "_insufficient data_"),
        "\n## Most AI-active repos\n",
        md_table(top_dev[["repo_full_name", "dev_ai_tools", "ai_coauthored_commit_count",
                          "ai_authored_commit_count", "ai_agent_pr_count", "first_dev_ai_date"]]),
        "",
    ]
    (outdir / "summary.md").write_text("\n".join(md))

    print(f"AI-usage analysis written to {outdir.relative_to(snap.parent)} "
          f"(dev={n_dev}/{n}, product={n_prod}/{n})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
