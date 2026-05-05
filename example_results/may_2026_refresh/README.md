# May 2026 Refresh (n = 38)

This directory contains a **full re-crawl on 4–5 May 2026 of an expanded 38-repository civic-tech dataset**. It supersedes the 29-repository [April 2026 refresh](../april_2026_refresh/) by adding nine substantially larger or older projects: **ForumMagnum, AutoGPT, mastodon, okfde/froide, openplans/shareabouts, codeforamerica/recordtrac, CodeForAfrica/actNOW, CitizensFoundation/your-priorities-app, mysociety/ceuk-marking**.

The April refresh remains the dataset cited in the paper's Sections 4.1–4.7. This May refresh is a **broader, more heterogeneous sample** that brings in well-known open-source projects (AutoGPT at 184k stars, mastodon at 50k) alongside very small civic experiments (mysociety/ceuk-marking at 0 stars). It is intended both as a robustness check on the n=29 findings and as the dataset for any follow-up work that needs the wider distribution. See `analysis_n38.md` in this folder for the accompanying writeup.

---

## What's new vs. April 2026

| Addition | Why |
|---|---|
| **9 new repositories** (24% of the dataset) | Adds high-visibility projects (AutoGPT, mastodon, ForumMagnum) and three older mature codebases (okfde/froide from 2011, openplans/shareabouts from 2011, codeforamerica/recordtrac from 2013), expanding the dynamic range on every metric |
| **`detection.py` 422-tolerance** | GitHub's REST `/topics` endpoint started returning 422 *"Could not resolve to a node with the global id of …"* for several repositories during the May crawl. The crawler now catches `GithubException`, logs a warning, and continues with empty topics rather than aborting the whole repository |
| **`issue_analytics.py` runtime cap** | Civiform/civiform (~7,000 issues) caused two consecutive crash modes in earlier crawl attempts: a silent SIGKILL after a 403 secondary-rate-limit backoff and 37 minutes of completely silent PyGithub pagination. The collector now caps total issues at 5,000, emits a progress line every 250 issues, and catches `GithubException` at the iterator's `next()` so partial data is preserved on irrecoverable pagination failure |

---

## Data Collection Details

| | |
|---|---|
| **Date collected** | 4–5 May 2026 (crawl spanned ~15.5 wall-clock hours) |
| **Configuration** | `config.example.yaml` (38 repositories from 17 GitHub organisations) |
| **Repositories** | 38 |
| **Organisations** | 17 (CodeForAfrica, codeforamerica, DemocracyClub, fvialibre, luftdata, markov-root, codeforjapan, meshtastic, civiform, iiab, ForumMagnum, Significant-Gravitas, mastodon, okfde, openplans, CitizensFoundation, mysociety) |
| **Primary languages** | 16 (Python, JavaScript, Ruby, TypeScript, Java, HCL, Jupyter Notebook, SCSS, PHP, Astro, C++, CSS, Dockerfile, HTML, Jinja, Kotlin) |
| **Contributors (`person_metrics`)** | 731 total (680 human, 51 bot) |
| **Contributors (`contributor_weekly_activity`)** | 2,684 unique |
| **Total commits (sum across `repo_metrics`)** | 186,490 |
| **Total commits (sum of `contributor_weekly_activity.commits`)** | 152,305 |
| **Lines added (cumulative)** | 48,549,707 |
| **Lines removed (cumulative)** | 38,227,850 |
| **Pull requests** | 85,603 |
| **Issues** | 27,761 |
| **Tags** | 2,786 |
| **Earliest commit** | 2011-04-12 (`okfde/froide`) |
| **Median project age** | 6.2 years |
| **Crawl wallclock** | ~15.5 h (4 process restarts during development of the issue-analytics patch — see "Implementation history" below) |

### Why two commit totals differ

The 186,490 figure comes from `repo_metrics.total_commits`, which is GitHub's per-repository commit count for the default branch (returned by the `/commits` endpoint with `per_page=1` and reading the `Link: rel="last"` header — the cheapest exact count available).

The 152,305 figure is the sum of `contributor_weekly_activity.commits`, which uses the GraphQL bulk commit fetcher to attribute every commit to its (contributor, ISO-week) pair. It excludes a small number of commits where the contributor cannot be resolved (e.g. detached HEAD merges, vendored history, GraphQL truncation on heavy repos).

Use `repo_metrics.total_commits` when you want the canonical per-repo count; use the CWA-summed figure when you need contributor-resolved attribution.

### Why contributor counts differ between files

- `person_metrics.csv` (731 contributors) is built from the `/stats/contributors` endpoint, which summarises weekly contribution activity for default-branch commits linked to GitHub user accounts, plus a commit-history fallback (capped at 500 commits) for repositories where stats are unavailable.
- `contributor_weekly_activity.csv` (2,684 unique `contributor_id`s) is built from GraphQL over **every** commit on the default branch, with contributors keyed by GitHub login *or* author email when no login is linked. It therefore includes email-only authors that `stats/contributors` omits. The two files are consistent but describe slightly different populations; use `contributor_weekly_activity.csv` when you need the long tail of drive-by or anonymous contributors.

---

## Output Files

### Crawl data (same schema as April snapshot)

| File | Rows | Notes |
|---|---|---|
| `repo_metrics.csv` | 38 | Repository-level metrics |
| `person_metrics.csv` | 731 | Per-contributor metrics; includes `is_bot` flag |
| `temporal_summary.csv` | 38 | PR / tag / release counts |
| `chaoss_summary.csv` | 38 | 45+ CHAOSS and extended columns |
| `pull_requests.csv` | 85,603 | PR records |
| `tags.csv` | 2,786 | Git tags |
| `core_periphery.csv` | 285 | Per-contributor network role from PR-review collaboration graph |
| `weekly_snapshots.csv` | 5,547 | Weekly commit/contributor snapshots |
| `contributor_lifecycles.csv` | 2,852 | Per-contributor first/last commit, active/departed |
| `contributor_weekly_activity.csv` | 20,162 | Per-(contributor, ISO-week) commit + lines_added + lines_removed |
| `issue_records.csv` | 27,761 | Individual issue records (capped at 5,000 per repo — only `mastodon/mastodon` hit the cap) |
| `issue_summary.csv` | 38 | Aggregated issue analytics |
| `cross_project_overlap.csv` | 536 | Contributors active in multiple crawled repos |
| `full_results.json` | — | Complete nested data for all 38 repositories (52 MB) |
| `<repo>_data.json` × 38 | — | Per-repository cache files |

### Weekly activity analysis

Generated by `scripts/weekly_activity_analysis.py` against `contributor_weekly_activity.csv`.

| File | Description |
|---|---|
| `weekly_activity_analysis/weekly_elephant_factor.csv` | Per repo: mean top-contributor share per week, % elephant weeks, % single-contributor weeks |
| `weekly_activity_analysis/churn_ratio.csv` | Per repo: overall churn ratio (deletions / (additions+deletions)), net LOC delta, % deletion-heavy weeks |
| `weekly_activity_analysis/effort_gini.csv` | Per repo: Gini coefficient of `lines_changed` per contributor, Gini of `commits` per contributor, top1 share |
| `weekly_activity_analysis/summary.md` | Human-readable rundown of the most striking findings (now including AutoGPT / mastodon / ForumMagnum) |

### Statistical analysis

Generated by `scripts/statistical_analysis.py output/`.

| File | Rows | Description |
|---|---|---|
| `statistical_analysis/dataset_summary.csv` | 1 | Dataset-wide aggregates |
| `statistical_analysis/descriptive_statistics.csv` | 25 | Per-metric mean / median / IQR / std |
| `statistical_analysis/normality_tests.csv` | 12 | Shapiro–Wilk on every continuous metric |
| `statistical_analysis/spearman_correlations.csv` | 17 | Spearman ρ matrix |
| `statistical_analysis/spearman_p_values.csv` | 17 | Matching p-value matrix |
| `statistical_analysis/correlation_pairs_fdr.csv` | 136 | Pairwise correlations with Benjamini–Hochberg FDR control |
| `statistical_analysis/partial_correlations.csv` | 10 | Partial Spearman controlling for `num_developers` (project size) |
| `statistical_analysis/group_comparisons.csv` | 19 | Mann–Whitney U + Cliff's δ on CI/CD, Cloud, AI/ML, OSI-license groupings |
| `statistical_analysis/maturity_analysis.csv` | 11 | Mann–Whitney U on Mature (≥6.2y) vs Young splits |
| `statistical_analysis/org_kruskal_wallis.csv` | 7 | Kruskal–Wallis across organisations with ≥3 repos |
| `statistical_analysis/bot_impact.csv` | 38 | Per-repo bot/human breakdown and HHI with vs without bots |
| `statistical_analysis/wilcoxon_bot_impact.csv` | 3 | Paired Wilcoxon on HHI / bus / elephant factor with vs without bots |

### Visualizations

219 PNG plots in `plots/` — six per repository (where data exists):

- `<repo>_growth.png` — cumulative commits + contributors over time
- `<repo>_weekly_activity.png` — weekly commit volume
- `<repo>_lifecycle.png` — contributor lifecycles (first→last commit per person)
- `<repo>_new_contributors.png` — weekly new-contributor arrivals
- `<repo>_issue_trends.png` — opens, closes, and backlog size over time (where issues exist)
- `<repo>_top_contributors.png` — top 20 contributors by commit count

---

## Implementation history (May 4 crawl)

The crawl required five process attempts before completing successfully. All of these are reproduced (and patched) in the source tree on branch `claude/add-new-repos-2026-05`; the per-repo cache made resumption from each death cheap.

| Attempt | PID | Outcome |
|---|---|---|
| 1 | 2558 | Died at 09:18 UTC, SIGHUP from non-detached parent shell (10 repos saved). **Fix**: launch with `setsid nohup`. |
| 2 | (same chain) | Aborted on 9 consecutive repos because GitHub returned 422 from `/topics` on `repo.get_topics()`. **Fix**: catch `GithubException` in `detection.py`. |
| 3 | 2839 | Silent SIGKILL at 15:43 UTC during `civiform/civiform` issue analytics, after a 403 secondary-rate-limit backoff. Likely sandbox quota. (27 repos saved.) |
| 4 | 2466 | Looped silently for 37 minutes on `civiform/civiform` issue analytics — PyGithub's urllib3 requests do not log via the same logger that captures the rest of the crawler, so the silence was indistinguishable from a hang. **Fix**: `issue_analytics.py` now caps total issues at 5,000, emits a progress line every 250 issues, and catches `GithubException` at the iterator level. |
| 5 | 6749 | **Completed.** Survived a container restart partway through (thanks to `setsid`). 38 repos saved, 8 PyGithub backoffs survived, 1 issue cap hit (mastodon at 5,000), 0 repo crawl failures, 0 topic-fetch warnings. |

The two patches (`detection.py` and `issue_analytics.py`) are committed on branch `claude/add-new-repos-2026-05` and apply cleanly going forward.

---

## How to reproduce

```bash
# From repo root
git checkout claude/add-new-repos-2026-05
uv sync
export GITHUB_TOKEN=ghp_...        # public_repo scope; ~7-15 hours run time
uv run civic-tech-crawler --config config.example.yaml

# Then derive analyses
uv run python scripts/statistical_analysis.py output/
uv run python scripts/weekly_activity_analysis.py
uv run python scripts/visualize.py --output-dir output

# And copy into a refresh snapshot folder
cp -r output/ example_results/may_2026_refresh/
```

API budget: ~2,000 / 5,000 hourly REST and ~500 / 5,000 hourly GraphQL calls remained at end of the May crawl, so the run is well within a single token's quota for that day.
