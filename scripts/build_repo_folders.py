"""Generate per-repository folders and repo_results.md files.

Reads existing flat outputs in <snapshot-dir>/ and produces:
- <snapshot-dir>/<owner>_<repo>/repo_results.md
- <snapshot-dir>/<owner>_<repo>/data.json (moved)
- <snapshot-dir>/<owner>_<repo>/<plotname>.png (moved)

Usage:
    uv run python scripts/build_repo_folders.py [snapshot-dir]

Default snapshot-dir is example_results/may_2026/. Idempotent:
re-running only moves files that haven't already been moved, and always
rewrites the markdown from the latest CSV state.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SNAPSHOT = ROOT / "example_results" / "may_2026"


def parse_findings_per_repo(findings_path: Path) -> dict[str, str]:
    """Pull per-repo paragraphs out of per_repo_findings.md keyed by 'owner/repo'."""
    if not findings_path.exists():
        return {}
    text = findings_path.read_text()
    parts = re.split(r"\n## ", "\n" + text)  # leading \n so first split discards header
    out: dict[str, str] = {}
    for chunk in parts[1:]:
        lines = chunk.split("\n", 1)
        if len(lines) < 2:
            continue
        repo, body = lines[0].strip(), lines[1].strip()
        if "/" in repo:
            out[repo] = body
    return out


def file_slug(repo: str) -> str:
    return repo.replace("/", "_")


def fmt_num(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    if isinstance(v, float):
        if v.is_integer():
            return f"{int(v):,}"
        return f"{v:,.2f}"
    if isinstance(v, int):
        return f"{v:,}"
    return str(v)


def collect_data(snapshot: Path) -> dict[str, dict]:
    """Pull a per-repo merged dict of metrics from the snapshot CSVs."""
    rm = pd.read_csv(snapshot / "repo_metrics.csv").rename(columns={"full_name": "repo"})
    ch = pd.read_csv(snapshot / "chaoss_summary.csv").rename(columns={"repo_full_name": "repo"})
    isum = pd.read_csv(snapshot / "issue_summary.csv").rename(columns={"repo_full_name": "repo"})
    churn = pd.read_csv(snapshot / "weekly_activity_analysis" / "churn_ratio.csv").rename(
        columns={"repo_full_name": "repo"}
    )
    gini = pd.read_csv(snapshot / "weekly_activity_analysis" / "effort_gini.csv").rename(
        columns={"repo_full_name": "repo"}
    )
    eleph = pd.read_csv(snapshot / "weekly_activity_analysis" / "weekly_elephant_factor.csv").rename(
        columns={"repo_full_name": "repo"}
    )
    cwa = pd.read_csv(snapshot / "contributor_weekly_activity.csv")
    cwa_commits = cwa.groupby("repo_full_name")["commits"].sum().rename("cwa_commits")

    merged = (
        rm.merge(ch, on="repo", how="left", suffixes=("", "_chaoss"))
        .merge(isum, on="repo", how="left", suffixes=("", "_issum"))
        .merge(churn, on="repo", how="left", suffixes=("", "_churn"))
        .merge(gini, on="repo", how="left", suffixes=("", "_gini"))
        .merge(eleph, on="repo", how="left", suffixes=("", "_eleph"))
        .merge(cwa_commits, left_on="repo", right_index=True, how="left")
    )
    out: dict[str, dict] = {}
    for _, r in merged.iterrows():
        out[r["repo"]] = r.to_dict()
    return out


def things_to_note(repo: str, d: dict) -> list[str]:
    notes: list[str] = []
    if repo == "mastodon/mastodon":
        notes.append(
            "**Issue analytics is right-censored at 5,000.** This is the only repo in "
            "the dataset to hit the cap. The actual GitHub-side issue total is higher; treat "
            "`total_issues`, `closed_issues`, and aggregated time-to-close metrics as lower bounds."
        )

    cwa_c = d.get("cwa_commits") or 0
    rm_c = d.get("total_commits") or 0
    if rm_c and cwa_c and rm_c >= 200 and rm_c >= 2 * cwa_c:
        notes.append(
            f"**Commit-count discrepancy.** `repo_metrics.total_commits` reports "
            f"{int(rm_c):,} but `contributor_weekly_activity` only attributes "
            f"{int(cwa_c):,} commits to identifiable authors (a {rm_c/cwa_c:.1f}× gap). "
            "Likely cause: a large fraction of history lives on non-default branches or "
            "is squash-merged. Use `repo_metrics.total_commits` for population-level counts; "
            "use the CWA sum when contributor attribution matters."
        )

    top1 = d.get("top1_contributor")
    if isinstance(top1, str) and "@" in top1:
        notes.append(
            f"**Top contributor `{top1}` is an email-only author** with no linked GitHub "
            "account. They are visible in `contributor_weekly_activity.csv` (which is keyed "
            "by login *or* email) but absent from `person_metrics.csv` (which is keyed by login)."
        )

    if d.get("net_loc_delta", 0) and d["net_loc_delta"] < 0:
        notes.append(
            f"**Net-negative LOC trajectory.** Cumulative deletions ({int(d['total_removed']):,}) "
            f"exceed cumulative additions ({int(d['total_added']):,}) by "
            f"{abs(int(d['net_loc_delta'])):,} lines over the project's history "
            "— consistent with the maintenance-phase signal discussed in `../analysis_n57.md` §2.7."
        )

    health = d.get("health_percentage")
    if pd.notna(health) and health <= 25:
        notes.append(
            f"**Low GitHub community-profile score ({int(health)}%).** Likely missing some of: "
            "CONTRIBUTING, CODE_OF_CONDUCT, GOVERNANCE, README, issue/PR templates."
        )

    bf = d.get("bus_factor_no_bots")
    hhi = d.get("hhi_no_bots")
    if pd.notna(bf) and bf == 1 and pd.notna(hhi) and hhi >= 8000:
        notes.append(
            f"**Extreme effort concentration** (HHI {int(hhi):,} on a 0–10,000 scale, "
            f"bus factor 1). Removing the top contributor would substantially halt activity."
        )

    if (d.get("total_issues") or 0) == 0:
        notes.append(
            "**Empty issue tracker.** No issues recorded — coordination likely happens via PRs, "
            "external systems, or out-of-band channels."
        )

    return notes


def quick_facts_table(repo: str, d: dict) -> str:
    age_years = None
    fc = d.get("first_commit_date")
    if isinstance(fc, str) and len(fc) >= 4:
        # crude: 2026 - year(first commit)
        try:
            age_years = 2026 - int(fc[:4]) + (5 / 12)  # roughly mid-2026
        except ValueError:
            age_years = None

    rows = [
        ("Repository", f"[{repo}](https://github.com/{repo})"),
        ("Primary language", d.get("primary_language") or "—"),
        ("Stars / Forks", f"{fmt_num(d.get('stars'))} / {fmt_num(d.get('forks'))}"),
        ("First commit", str(d.get("first_commit_date") or "—")[:10]),
        ("Project age", f"{age_years:.1f} years" if age_years is not None else "—"),
        ("Total commits (repo_metrics)", fmt_num(d.get("total_commits"))),
        ("Attributable contributors (CWA)", fmt_num(d.get("contributors") or d.get("num_developers"))),
        ("Cloud / AI-ML signals", f"{'yes' if d.get('cloud_detected') else 'no'} / {'yes' if d.get('ai_ml_detected') else 'no'}"),
        ("OSI-approved license", "yes" if d.get("is_osi_approved") else "no"),
    ]
    out = "| | |\n|---|---|\n"
    for k, v in rows:
        out += f"| **{k}** | {v} |\n"
    return out


def metrics_table(repo: str, d: dict) -> str:
    rows = [
        ("Bus factor (humans only)", fmt_num(d.get("bus_factor_no_bots"))),
        ("HHI (humans only, 0–10,000)", fmt_num(d.get("hhi_no_bots"))),
        ("Effort Gini on lines changed", fmt_num(d.get("effort_gini_lines"))),
        ("Effort Gini on commits", fmt_num(d.get("effort_gini_commits"))),
        ("Top contributor", f"`{d.get('top1_contributor')}`" if d.get("top1_contributor") else "—"),
        ("Top contributor's lines share", f"{(d['top1_lines_share']*100):.1f}%" if pd.notna(d.get('top1_lines_share')) else "—"),
        ("Mean weekly top-contributor share", f"{(d['mean_top_share']*100):.1f}%" if pd.notna(d.get('mean_top_share')) else "—"),
        ("% weeks dominated by one contributor (≥50%)", f"{d['elephant_weeks_pct']:.1f}%" if pd.notna(d.get('elephant_weeks_pct')) else "—"),
        ("% solo weeks (≥99.9% from one person)", f"{d['single_contributor_weeks_pct']:.1f}%" if pd.notna(d.get('single_contributor_weeks_pct')) else "—"),
        ("Lines added / removed", f"{fmt_num(d.get('total_added'))} / {fmt_num(d.get('total_removed'))}"),
        ("Net LOC delta", fmt_num(d.get("net_loc_delta"))),
        ("Overall churn ratio", fmt_num(d.get("overall_churn_ratio"))),
        ("Community profile (health %)", fmt_num(d.get("health_percentage"))),
        ("Issues (total / open / closed)", f"{fmt_num(d.get('total_issues'))} / {fmt_num(d.get('open_issues'))} / {fmt_num(d.get('closed_issues'))}"),
        ("Median issue first response (h)", fmt_num(d.get("median_time_to_first_response_issues_hours"))),
        ("Median PR review turnaround (h)", fmt_num(d.get("median_pr_review_turnaround_hours"))),
        ("Change-request acceptance ratio", fmt_num(d.get("change_request_acceptance_ratio"))),
        ("Stale issue ratio", fmt_num(d.get("stale_issue_ratio"))),
    ]
    out = "| Metric | Value |\n|---|---|\n"
    for k, v in rows:
        out += f"| {k} | {v} |\n"
    return out


def file_listing(folder: Path) -> str:
    """Return a markdown listing of files actually in the repo's folder."""
    lines = ["| File | Description |", "|---|---|"]
    descriptions = {
        "data.json": "Full per-repository crawler output (every metric for this repo, JSON-encoded)",
        "growth.png": "Cumulative commits and contributors over time",
        "lifecycle.png": "Per-contributor lifecycle (first→last commit) for the top 25 authors",
        "weekly_activity.png": "Weekly commit volume",
        "new_contributors.png": "Weekly new-contributor arrival rate",
        "issue_trends.png": "Issue opens, closes, and backlog size over time (only present if the repo has issues)",
        "top_contributors.png": "Top 20 contributors by commit count",
        "repo_results.md": "This file",
    }
    names = {f.name for f in folder.iterdir() if f.is_file()}
    names.add("repo_results.md")  # always include — file is written after this listing is built
    for name in sorted(names):
        lines.append(f"| `{name}` | {descriptions.get(name, '—')} |")
    return "\n".join(lines)


def render(repo: str, d: dict, finding_paragraph: str, folder: Path) -> str:
    notes = things_to_note(repo, d)
    notes_section = ""
    if notes:
        notes_section = "## Things to note\n\n"
        for n in notes:
            notes_section += f"- {n}\n"
        notes_section += "\n"
    return f"""# {repo}

[View on GitHub](https://github.com/{repo})

## At a glance

{quick_facts_table(repo, d)}

## Main findings

{finding_paragraph}

## Key metrics

{metrics_table(repo, d)}

{notes_section}## Files in this folder

{file_listing(folder)}

## See also

- [`../README.md`](../README.md) — full dataset overview and reproduction instructions
- [`../analysis_n57.md`](../analysis_n57.md) — academic writeup of the n=57 corpus
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "snapshot",
        nargs="?",
        default=str(DEFAULT_SNAPSHOT),
        help=f"Snapshot directory (default: {DEFAULT_SNAPSHOT.relative_to(ROOT)})",
    )
    args = parser.parse_args()

    snapshot = Path(args.snapshot).resolve()
    if not snapshot.exists():
        print(f"ERROR: snapshot directory '{snapshot}' does not exist", file=sys.stderr)
        return 1

    plots = snapshot / "plots"
    findings_path = snapshot / "per_repo_findings.md"

    findings = parse_findings_per_repo(findings_path)
    metrics = collect_data(snapshot)

    if not findings:
        print(
            f"NOTE: no per_repo_findings.md found at {findings_path} — repo_results.md "
            "will be generated from metric tables only."
        )
    elif set(metrics.keys()) - set(findings.keys()):
        missing = set(metrics.keys()) - set(findings.keys())
        print(f"WARNING: {len(missing)} repos have no entry in per_repo_findings.md: {sorted(missing)}")

    moved_jsons = 0
    moved_plots = 0
    written_md = 0

    for repo, d in metrics.items():
        slug = file_slug(repo)
        folder = snapshot / slug
        folder.mkdir(exist_ok=True)

        # Move data.json
        src_json = snapshot / f"{slug}_data.json"
        dst_json = folder / "data.json"
        if src_json.exists() and not dst_json.exists():
            shutil.move(src_json, dst_json)
            moved_jsons += 1

        # Move plots: <slug>_<kind>.png  →  <kind>.png
        if plots.exists():
            for plot in sorted(plots.glob(f"{slug}_*.png")):
                kind = plot.stem[len(slug) + 1 :]
                dst_plot = folder / f"{kind}.png"
                if not dst_plot.exists():
                    shutil.move(plot, dst_plot)
                    moved_plots += 1

        # Write repo_results.md
        finding = findings.get(
            repo,
            "_Per-repository narrative findings are not bundled with this snapshot. "
            "See [`../analysis_n57.md`](../analysis_n57.md) for cross-cutting findings; "
            "the per-repository quantitative metrics are in the **Key metrics** table below._",
        )
        (folder / "repo_results.md").write_text(render(repo, d, finding, folder))
        written_md += 1

    # Clean up empty plots/ folder if all moved
    if plots.exists() and not any(plots.iterdir()):
        plots.rmdir()

    print(
        f"done — snapshot={snapshot.relative_to(ROOT) if snapshot.is_relative_to(ROOT) else snapshot} "
        f"folders={len(metrics)} jsons_moved={moved_jsons} "
        f"plots_moved={moved_plots} md_written={written_md}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
