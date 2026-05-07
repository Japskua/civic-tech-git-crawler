# okfde/froide

[View on GitHub](https://github.com/okfde/froide)

## At a glance

| | |
|---|---|
| **Repository** | [okfde/froide](https://github.com/okfde/froide) |
| **Primary language** | Python |
| **Stars / Forks** | 409 / 99 |
| **First commit** | 2011-04-12 |
| **Project age** | 15.4 years |
| **Total commits (repo_metrics)** | 7,888 |
| **Attributable contributors (CWA)** | 19 |
| **Cloud / AI-ML signals** | no / no |
| **OSI-approved license** | yes |


## Main findings

The German Freedom-of-Information request platform from Open Knowledge DE. **Oldest project in the sample (first commit 2011-04-12, 15 years)**. 38 developers, 436 issues, bus factor 2. `stefanw` carries 80% of lines and 95% of weekly top-shares — extreme dependence on the founding maintainer despite a long history. Effort-Gini 0.95. **Summary**: the canonical "long-lived single-founder civic platform" — long history, broad contribution surface, but a single author still essentially holds the codebase.

## Key metrics

| Metric | Value |
|---|---|
| Bus factor (humans only) | 2 |
| HHI (humans only, 0–10,000) | 2,932.20 |
| Effort Gini on lines changed | 0.83 |
| Effort Gini on commits | 0.79 |
| Top contributor | `krmax44` |
| Top contributor's lines share | 51.4% |
| Mean weekly top-contributor share | 85.8% |
| % weeks dominated by one contributor (≥50%) | 95.7% |
| % solo weeks (≥99.9% from one person) | 34.4% |
| Lines added / removed | 134,776 / 92,956 |
| Net LOC delta | 41,820 |
| Overall churn ratio | 0.41 |
| Community profile (health %) | 62 |
| Issues (total / open / closed) | 436 / 107 / 329 |
| Median issue first response (h) | 18.10 |
| Median PR review turnaround (h) | 67.50 |
| Change-request acceptance ratio | 0.71 |
| Stale issue ratio | 0.99 |


## Things to note

- **Commit-count discrepancy.** `repo_metrics.total_commits` reports 7,888 but `contributor_weekly_activity` only attributes 1,100 commits to identifiable authors (a 7.2× gap). Likely cause: a large fraction of history lives on non-default branches or is squash-merged. Use `repo_metrics.total_commits` for population-level counts; use the CWA sum when contributor attribution matters.

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
