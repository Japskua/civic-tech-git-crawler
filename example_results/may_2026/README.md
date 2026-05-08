# May 2026 Refresh (n = 37) — canonical dataset

This is the **canonical n=37 civic-tech crawl**, collected on 5–6 May 2026 with all the crawler's self-healing improvements (auto-respawn, stats endpoint warm-up, burstiness fallback, issue-cap, get_topics tolerance) in effect. It supersedes the earlier `may_2026_refresh/` snapshot, which has been removed.

The accompanying paper rewrite at `paper_draft.md` reports its results against this dataset. See `analysis_n37.md` in this folder for the academic-style writeup of the findings, methodology, and threats to validity.

---

## Dataset summary

| | |
|---|---|
| **Repositories** | 37 |
| **Organisations** | 16 |
| **Primary languages** | 16 |
| **Crawl date** | 5–6 May 2026 |
| **Crawl wallclock** | ~12 hours net (across 4 sandbox-killed-and-respawned attempts) |
| **person_metrics rows** | 703 (654 human, 49 bot) |
| **contributor_weekly_activity unique contributors** | 2,344 |
| **contributor-weeks** | 22,486 |
| **Total commits (`repo_metrics`)** | 178,099 |
| **Total commits (CWA)** | 162,033 |
| **Lines added (cumulative)** | 44,402,684 |
| **Lines removed (cumulative)** | 34,787,587 |
| **PR records** | 77,780 |
| **Issue records** | 23,951 |
| **Tags** | 2,689 |
| **Earliest commit** | 2011-04-12 (`okfde/froide`, 15 years) |
| **Median project age** | 6.3 years |

---

## What's different vs. the earlier `may_2026_refresh`

| | Earlier `may_2026_refresh` (deleted) | This `may_2026` |
|---|---|---|
| Repository count | 38 (included AutoGPT) | **37** (AutoGPT excluded — see paper §3.2) |
| Burstiness coverage | 5/38 (most repos NaN due to GitHub stats endpoint timeouts) | **37/37** (recomputed from `weekly_snapshots`) |
| Stats endpoint retry budget | 45 s | 225 s, with warm-up pre-pass at crawl start |
| Crawler death recovery | Manual relaunches (4 hrs lost over 3 deaths) | Auto-respawn wrapper |
| Per-repo crawl timestamps | 14-hour spread | 28-hour spread (across 4 respawn cycles), but a single canonical run |

The earlier snapshot has been removed in this branch — this folder is the only May 2026 dataset retained going forward.

---

## Why AutoGPT is excluded

`Significant-Gravitas/AutoGPT` was crawled in the earlier `may_2026_refresh` exploratory pass but is excluded from this canonical n=37 dataset and from the paper. Civic technology in the strict sense (the definition the paper defends in §3.2) is software designed for civic engagement, government services, public participation, transparency, or democratic processes. AutoGPT is a general-purpose autonomous AI agent framework whose civic uses are downstream user behaviour rather than design intent. Including it would dilute the sample's coherence as a civic-tech population.

The eight other May additions (`ForumMagnum`, `mastodon`, `okfde/froide`, `openplans/shareabouts`, `codeforamerica/recordtrac`, `CodeForAfrica/actNOW`, `CitizensFoundation/your-priorities-app`, `mysociety/ceuk-marking`) are all defensibly civic — see paper §3.2 for the per-repo justification.

---

## Output files

### Crawl data (one row per repository unless noted)

| File | Rows | Notes |
|---|---|---|
| `repo_metrics.csv` | 37 | Repository-level metrics (stars, forks, languages, license, CI/CD, etc.) |
| `person_metrics.csv` | 703 | Per-(repo, contributor) metrics; includes `is_bot` flag |
| `temporal_summary.csv` | 37 | PR / tag / release counts |
| `chaoss_summary.csv` | 37 | 45+ CHAOSS columns including `burstiness_cv` (recomputed from weekly_snapshots, 37/37 populated) and the new `burstiness_cv_full_history` column |
| `pull_requests.csv` | 77,780 | Individual PR records |
| `tags.csv` | 2,689 | Git tags |
| `core_periphery.csv` | 262 | Per-contributor network role from PR-review collaboration graph |
| `weekly_snapshots.csv` | 5,791 | Weekly commit/contributor snapshots |
| `contributor_lifecycles.csv` | 2,562 | Per-contributor first/last commit, active/departed |
| `contributor_weekly_activity.csv` | 22,486 | Per-(contributor, ISO-week) commit + lines_added + lines_removed |
| `issue_records.csv` | 23,951 | Individual issue records (capped at 5,000 per repo — only `mastodon/mastodon` hit the cap) |
| `issue_summary.csv` | 37 | Aggregated issue analytics |
| `cross_project_overlap.csv` | 511 | Contributors active in multiple crawled repos |
| `full_results.json` | — | Complete nested data for all 37 repositories |

### Per-repository folders (37)

Each repository has its own folder named `<owner>_<repo>/` containing:

- `repo_results.md` — at-a-glance metadata, key metrics table, the per-repo finding paragraph from `per_repo_findings.md`, any rule-based caveats (mastodon's 5,000-issue cap, your-priorities-app's commit-count discrepancy, markov-root's email-only top contributor, net-negative LOC trajectories, etc.), file listing, and cross-links back to the dataset-level docs.
- `data.json` — full crawler output for the repository
- 5–6 PNG plots: `growth.png`, `weekly_activity.png`, `lifecycle.png`, `new_contributors.png`, `top_contributors.png`, plus `issue_trends.png` if the repo has issues

### Derived analyses

| Folder/file | Description |
|---|---|
| `statistical_analysis/` | 12 CSVs from `scripts/statistical_analysis.py` — descriptives, normality, Spearman+FDR, partial correlations, group comparisons, maturity split, organisational Kruskal–Wallis, paired Wilcoxon for bot impact |
| `weekly_activity_analysis/` | 3 CSVs from `scripts/weekly_activity_analysis.py` (weekly elephant factor, churn ratio, effort Gini) plus `summary.md` |
| `per_repo_findings.md` | All 37 short per-repo paragraphs in one document, plus a cross-cutting observations section |
| `analysis_n37.md` | Academic-style writeup of headline findings, methodology, and threats to validity |

---

## How to reproduce

```bash
# Crawl
git checkout claude/full-recrawl-n37-2026-05  # or main
uv sync
export GITHUB_TOKEN=ghp_...
setsid nohup env GITHUB_TOKEN="$GITHUB_TOKEN" \
    scripts/run_with_respawn.sh config.example.yaml output 37 \
    > crawl.log 2>&1 < /dev/null & disown

# Derive analyses
uv run python scripts/statistical_analysis.py output/
uv run python scripts/weekly_activity_analysis.py output/
uv run python scripts/visualize.py --output-dir output

# (Optional, only for snapshots created with old crawler versions where
# burstiness coverage may be sparse — the current crawler self-heals.)
uv run python scripts/recompute_burstiness.py output/

# Snapshot
cp -r output/ example_results/<refresh-name>/
uv run python scripts/build_repo_folders.py example_results/<refresh-name>/
```

The crawl typically takes 10–15 hours wall-clock with the auto-respawn wrapper handling the ~4-hour sandbox-kill cycle. Crawls within a single `output/` directory resume from per-repo cache, so lost work is bounded by the in-flight repo at the time of death.

---

## Cross-links

- [`paper_draft.md`](../../paper_draft.md) — the n=37 research paper (top of repo)
- [`analysis_n37.md`](analysis_n37.md) — academic writeup of this snapshot's findings
- [`per_repo_findings.md`](per_repo_findings.md) — per-repo descriptive findings (37 entries)
- [`../../README.md`](../../README.md) — top-level project readme
- [`../april_2026_refresh/`](../april_2026_refresh/) — earlier n=29 snapshot used for the original paper's §4.7 (weekly LOC analysis)
- [`../`](../) — March 2026 baseline (n=29) used for the original paper's §4.1–§4.6
