# meshtastic/Meshtastic-Android

[View on GitHub](https://github.com/meshtastic/Meshtastic-Android)

## At a glance

| | |
|---|---|
| **Repository** | [meshtastic/Meshtastic-Android](https://github.com/meshtastic/Meshtastic-Android) |
| **Primary language** | Kotlin |
| **Stars / Forks** | 1,584 / 451 |
| **First commit** | 2020-01-20 |
| **Project age** | 6.4 years |
| **Total commits (repo_metrics)** | 6,495 |
| **Attributable contributors (CWA)** | 9 |
| **Cloud / AI-ML signals** | no / no |
| **OSI-approved license** | no |


## Main findings

The Android client for Meshtastic mesh radios (Kotlin, 2020, 107 developers, 1,475 issues). Bus factor 1, HHI 9,384 despite 107 contributors — driven by `jamesarich` doing 99% of lines (vs. 76% of commits). **Lines-vs-commits Gini gap of +0.13** is the second-largest in the sample, indicating mega-commits. Median issue response 1.4 h, PR turnaround 0.4 h. **Summary**: a small core team operating at very high velocity, with one author landing very large refactor commits.

## Key metrics

| Metric | Value |
|---|---|
| Bus factor (humans only) | 1 |
| HHI (humans only, 0–10,000) | 9,384.10 |
| Effort Gini on lines changed | 0.88 |
| Effort Gini on commits | 0.76 |
| Top contributor | `jamesarich` |
| Top contributor's lines share | 98.7% |
| Mean weekly top-contributor share | 92.1% |
| % weeks dominated by one contributor (≥50%) | 100.0% |
| % solo weeks (≥99.9% from one person) | 0.0% |
| Lines added / removed | 50,262 / 35,763 |
| Net LOC delta | 14,499 |
| Overall churn ratio | 0.42 |
| Community profile (health %) | 100 |
| Issues (total / open / closed) | 1,475 / 40 / 1,435 |
| Median issue first response (h) | 1.40 |
| Median PR review turnaround (h) | 0.40 |
| Change-request acceptance ratio | 0.92 |
| Stale issue ratio | 0.35 |


## Things to note

- **Commit-count discrepancy.** `repo_metrics.total_commits` reports 6,495 but `contributor_weekly_activity` only attributes 200 commits to identifiable authors (a 32.5× gap). Likely cause: a large fraction of history lives on non-default branches or is squash-merged. Use `repo_metrics.total_commits` for population-level counts; use the CWA sum when contributor attribution matters.
- **Extreme effort concentration** (HHI 9,384 on a 0–10,000 scale, bus factor 1). Removing the top contributor would substantially halt activity.

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
- [`../analysis_n38.md`](../analysis_n38.md) — academic writeup of the n=38 sample
- [`../per_repo_findings.md`](../per_repo_findings.md) — all 38 per-repo findings in one document
