# codeforamerica/recordtrac

[View on GitHub](https://github.com/codeforamerica/recordtrac)

## At a glance

| | |
|---|---|
| **Repository** | [codeforamerica/recordtrac](https://github.com/codeforamerica/recordtrac) |
| **Primary language** | CSS |
| **Stars / Forks** | 60 / 41 |
| **First commit** | 2013-03-28 |
| **Project age** | 13.4 years |
| **Total commits (repo_metrics)** | 2,570 |
| **Attributable contributors (CWA)** | 26 |
| **Cloud / AI-ML signals** | yes / no |
| **OSI-approved license** | no |


## Main findings

A 2013 records-request tracking platform (CSS-primary, 17 developers). One of the dataset's three **net-negative LOC repos** (−34k net, 52% churn). 149 issues, all 84 closed ones likely from initial deployment phase. **Summary**: a 12-year-old project visibly in mature-maintenance mode; deletions outpace additions and the issue queue has stalled.

## Key metrics

| Metric | Value |
|---|---|
| Bus factor (humans only) | 2 |
| HHI (humans only, 0–10,000) | 4,357.40 |
| Effort Gini on lines changed | 0.84 |
| Effort Gini on commits | 0.87 |
| Top contributor | `criscristina` |
| Top contributor's lines share | 34.5% |
| Mean weekly top-contributor share | 79.9% |
| % weeks dominated by one contributor (≥50%) | 88.8% |
| % solo weeks (≥99.9% from one person) | 36.0% |
| Lines added / removed | 333,219 / 366,883 |
| Net LOC delta | -33,664 |
| Overall churn ratio | 0.52 |
| Community profile (health %) | 37 |
| Issues (total / open / closed) | 149 / 65 / 84 |
| Median issue first response (h) | 16.10 |
| Median PR review turnaround (h) | — |
| Change-request acceptance ratio | 0.59 |
| Stale issue ratio | 1 |


## Things to note

- **Net-negative LOC trajectory.** Cumulative deletions (366,883) exceed cumulative additions (333,219) by 33,664 lines over the project's history — consistent with the maintenance phase signal in `analysis_n37.md` §3.8.

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
