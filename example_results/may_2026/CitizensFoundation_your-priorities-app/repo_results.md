# CitizensFoundation/your-priorities-app

[View on GitHub](https://github.com/CitizensFoundation/your-priorities-app)

## At a glance

| | |
|---|---|
| **Repository** | [CitizensFoundation/your-priorities-app](https://github.com/CitizensFoundation/your-priorities-app) |
| **Primary language** | HTML |
| **Stars / Forks** | 142 / 38 |
| **First commit** | 2014-08-22 |
| **Project age** | 12.4 years |
| **Total commits (repo_metrics)** | 8,018 |
| **Attributable contributors (CWA)** | 1 |
| **Cloud / AI-ML signals** | yes / no |
| **OSI-approved license** | yes |


## Main findings

A Reykjavík-based participatory democracy platform (HTML, started 2014). The crawl finds 4 attributable contributors and an extreme effort profile: **Gini = 0.00 because 100% of every active week is `rbjarnason`** — the platform's lead developer. The repo has 1.8M lines added vs. 1.7M removed (churn 0.49), characteristic of a long-running balanced rewrite. Note the discrepancy flagged in `analysis_n37.md` §4.3: `repo_metrics.total_commits` reports 8,011 vs. 800 attributable in `contributor_weekly_activity` — most history is likely on non-default branches or squash-merged. **One-line summary**: a textbook single-maintainer civic platform with a decade of solo evolution.

## Key metrics

| Metric | Value |
|---|---|
| Bus factor (humans only) | 1 |
| HHI (humans only, 0–10,000) | 10,000 |
| Effort Gini on lines changed | 0 |
| Effort Gini on commits | 0 |
| Top contributor | `rbjarnason` |
| Top contributor's lines share | 100.0% |
| Mean weekly top-contributor share | 100.0% |
| % weeks dominated by one contributor (≥50%) | 100.0% |
| % solo weeks (≥99.9% from one person) | 100.0% |
| Lines added / removed | 911,556 / 870,284 |
| Net LOC delta | 41,272 |
| Overall churn ratio | 0.49 |
| Community profile (health %) | 37 |
| Issues (total / open / closed) | 34 / 13 / 21 |
| Median issue first response (h) | 24.80 |
| Median PR review turnaround (h) | — |
| Change-request acceptance ratio | 0.42 |
| Stale issue ratio | 1 |


## Things to note

- **Commit-count discrepancy.** `repo_metrics.total_commits` reports 8,018 but `contributor_weekly_activity` only attributes 600 commits to identifiable authors (a 13.4× gap). Likely cause: a large fraction of history lives on non-default branches or is squash-merged. Use `repo_metrics.total_commits` for population-level counts; use the CWA sum when contributor attribution matters.
- **Extreme effort concentration** (HHI 10,000 on a 0–10,000 scale, bus factor 1). Removing the top contributor would substantially halt activity.

## Files in this folder

| File | Description |
|---|---|
| `data.json` | Full per-repository crawler output (every metric for this repo, JSON-encoded) |
| `growth.png` | Cumulative commits and contributors over time |
| `issue_trends.png` | Issue opens, closes, and backlog size over time (only present if the repo has issues) |
| `lifecycle.png` | Per-contributor lifecycle (first→last commit) for the top 25 authors |
| `new_contributors.png` | Weekly new-contributor arrival rate |
| `repo_results.md` | This file |
| `top_contributors.png` | Top 20 contributors by commit count |
| `weekly_activity.png` | Weekly commit volume |

## See also

- [`../README.md`](../README.md) — full dataset overview and reproduction instructions
- [`../analysis_n37.md`](../analysis_n37.md) — academic writeup of the n=37 sample
- [`../per_repo_findings.md`](../per_repo_findings.md) — all 38 per-repo findings in one document
