# mastodon/mastodon

[View on GitHub](https://github.com/mastodon/mastodon)

## At a glance

| | |
|---|---|
| **Repository** | [mastodon/mastodon](https://github.com/mastodon/mastodon) |
| **Primary language** | Ruby |
| **Stars / Forks** | 49,930 / 7,427 |
| **First commit** | 2016-02-20 |
| **Project age** | 10.4 years |
| **Total commits (repo_metrics)** | 21,229 |
| **Attributable contributors (CWA)** | 1,050 |
| **Cloud / AI-ML signals** | yes / no |
| **OSI-approved license** | no |


## Main findings

The Mastodon federation server (Ruby, 2016, 50k★, 406 attributable developers). **Issue analytics capped at 5,000 — the only repo in the sample to hit the cap**; actual issue total is higher and any total/closed/stale ratio for mastodon should be treated as right-censored. Bus factor 3, HHI 1,462 — well-distributed despite scale. `Gargron` carries 44% of lines and 62% of weekly top-shares. **Summary**: the dataset's clearest example of sustained large-scale community development with one founder still meaningfully central.

## Key metrics

| Metric | Value |
|---|---|
| Bus factor (humans only) | 3 |
| HHI (humans only, 0–10,000) | 1,461.30 |
| Effort Gini on lines changed | 0.98 |
| Effort Gini on commits | 0.92 |
| Top contributor | `Gargron` |
| Top contributor's lines share | 43.7% |
| Mean weekly top-contributor share | 62.2% |
| % weeks dominated by one contributor (≥50%) | 63.4% |
| % solo weeks (≥99.9% from one person) | 4.5% |
| Lines added / removed | 1,895,443 / 917,895 |
| Net LOC delta | 977,548 |
| Overall churn ratio | 0.33 |
| Community profile (health %) | 87 |
| Issues (total / open / closed) | 5,000 / 616 / 4,384 |
| Median issue first response (h) | 16 |
| Median PR review turnaround (h) | 3.20 |
| Change-request acceptance ratio | 0.84 |
| Stale issue ratio | 0.86 |


## Things to note

- **Issue analytics is right-censored at 5,000.** This is the only repo in the dataset to hit the cap. The actual GitHub-side issue total is higher; treat `total_issues`, `closed_issues`, and aggregated time-to-close metrics as lower bounds.

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
