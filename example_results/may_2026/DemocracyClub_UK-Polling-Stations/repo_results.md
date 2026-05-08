# DemocracyClub/UK-Polling-Stations

[View on GitHub](https://github.com/DemocracyClub/UK-Polling-Stations)

## At a glance

| | |
|---|---|
| **Repository** | [DemocracyClub/UK-Polling-Stations](https://github.com/DemocracyClub/UK-Polling-Stations) |
| **Primary language** | Python |
| **Stars / Forks** | 36 / 29 |
| **First commit** | 2015-02-21 |
| **Project age** | 11.4 years |
| **Total commits (repo_metrics)** | 8,767 |
| **Attributable contributors (CWA)** | 35 |
| **Cloud / AI-ML signals** | yes / no |
| **OSI-approved license** | yes |


## Main findings

A long-running (2015) Python data pipeline for UK polling-station data. **Largest net-negative LOC trajectory in the sample**: +6.3M / −9.7M = −3.4M net, 61% churn over its lifetime. 33 developers, 3,851 issues (3,786 closed). Effort concentration is high (Gini 0.92) with `symroe` carrying 52% of lines. **Summary**: the dataset's clearest example of a project past the growth phase; large vendored datasets being pruned consistently exceeds new code.

## Key metrics

| Metric | Value |
|---|---|
| Bus factor (humans only) | 2 |
| HHI (humans only, 0–10,000) | 3,067.40 |
| Effort Gini on lines changed | 0.92 |
| Effort Gini on commits | 0.82 |
| Top contributor | `symroe` |
| Top contributor's lines share | 51.5% |
| Mean weekly top-contributor share | 82.6% |
| % weeks dominated by one contributor (≥50%) | 94.5% |
| % solo weeks (≥99.9% from one person) | 28.7% |
| Lines added / removed | 6,297,063 / 9,733,304 |
| Net LOC delta | -3,436,241 |
| Overall churn ratio | 0.61 |
| Community profile (health %) | 75 |
| Issues (total / open / closed) | 3,851 / 65 / 3,786 |
| Median issue first response (h) | 45.10 |
| Median PR review turnaround (h) | 140.30 |
| Change-request acceptance ratio | 0.75 |
| Stale issue ratio | 0.97 |


## Things to note

- **Net-negative LOC trajectory.** Cumulative deletions (9,733,304) exceed cumulative additions (6,297,063) by 3,436,241 lines over the project's history — consistent with the maintenance phase signal in `analysis_n37.md` §3.8.

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
