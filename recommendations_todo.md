# Recommendations Implementation Checklist

> **Status: ALL COMPLETE** — All 10 recommended metrics plus 5 supporting metrics are fully implemented and merged to `master` across three PRs.

Based on the analysis in `recommended_actions_20_02_2026.md`.

## Implementation History

| PR | Branch | Metrics Added | Status |
|----|--------|---------------|--------|
| PR #1 | `improve_by_recommendations` | Elephant Factor, Contributor Retention Cohorts, Time to First Response (Issues & PRs), Documentation Freshness, Stale Issue Ratio, PR Review Depth & Turnaround (7 metrics, 15 fields) | ✅ Merged |
| PR #2 | `add_future_metrics` | HHI (Org Concentration), Institutional Type Classification, Cross-Project Contributor Overlap, DORA Metrics (4 metrics, 8 fields) | ✅ Merged |
| PR #3 | `add_core_periphery` | Core-Periphery Network Analysis (1 metric, 6 fields + new CSV + new dataclass) | ✅ Merged |

## HIGH Priority (Implemented in PR #1)

- [x] **Elephant Factor** — Minimum number of organizations whose contributors account for 50% of commits. CHAOSS metric, zero additional API calls (reuses existing org diversity data).
- [x] **Contributor Retention Cohorts** — Classify contributors as new (1 active week), casual (2-12 weeks), or regular (13+ weeks). Uses existing `get_stats_contributors()` weekly data.
- [x] **Time to First Response (Issues)** — Median hours from issue creation to first non-author comment. Sampled from last 100 issues.
- [x] **Time to First Response (PRs)** — Median hours from PR creation to first non-author comment. Sampled from last 100 PRs.

## LOW Effort (Implemented in PR #1)

- [x] **Documentation Freshness** — Last commit date on README.md and CONTRIBUTING.md. Two API calls per repo.
- [x] **Stale Issue Ratio** — Percentage of open issues with no activity for 90+ days.
- [x] **PR Review Depth & Turnaround** — Median hours from PR creation to first formal review, and average review comments per PR. Sampled from last 100 merged PRs.

## Future Work → Now Implemented (PR #2 + PR #3)

- [x] **Core-Periphery Network Analysis** — PR review collaboration graph with NetworkX. Classifies contributors as core/periphery by degree centrality. Separate `core_periphery.csv` output. *(PR #3)*
- [x] **Institutional Type Classification** — Government/nonprofit/academic/company classification from GitHub profile company field. *(PR #2)*
- [x] **Cross-Project Contributor Overlap** — Contributors active in multiple crawled repos. Separate `cross_project_overlap.csv` output. *(PR #2)*
- [x] **DORA Metrics** — Deployment frequency, median lead time, change failure rate (heuristic from PR titles). *(PR #2)*
- [x] **Herfindahl-Hirschman Index** — Organizational commit concentration index (0–10,000 scale). *(PR #2)*

## Data Quality Fixes

- [x] **Anonymous contributor fallback** — `repo_metrics.py` now retries with `anon=true` when `get_contributors().totalCount == 0` but `total_commits > 0`. Fixes `num_developers=0` for repos where all commit authors use unlinked emails.
- [x] **Commit-based person metrics fallback** — `person_metrics.py` falls back to iterating commits (capped at 500) when `stats/contributors` returns empty. Groups by author email to build minimal `PersonMetrics` records.
- [x] **Wired `repo_metrics` into `person_metrics`** — `cli.py` passes `repo_metrics` to `collect_person_metrics()` so the fallback can check `total_commits`.

## Supporting Changes (All Complete)

- [x] Added 29 new fields to `ChaossMetrics` dataclass in `models.py`
- [x] Added `CorePeripheryContributor` and `CrossProjectOverlap` dataclasses to `models.py`
- [x] Updated `_dict_to_chaoss_metrics()` in `cache.py` with `.get()` defaults for all new fields
- [x] Updated `_export_chaoss_summary()` headers in `csv_exporter.py` (39 columns total)
- [x] Added `_export_core_periphery()` and `_export_cross_project_overlap()` to `csv_exporter.py`
- [x] Added `get_last_commit_date_for_path()` method to `client.py`
- [x] Added `networkx>=3.0` dependency to `pyproject.toml`
- [x] Updated `README.md` with full metrics documentation

## Testing (All Verified)

- [x] Run `--force` crawl against 3 test repos (DemocracyClub/UK-Polling-Stations, DemocracyClub/WhoCanIVoteFor, fvialibre/edia)
- [x] Verify all 39 columns in `chaoss_summary.csv`
- [x] Verify new fields in per-repo JSON cache files
- [x] Verify `--export-only` works with new cache format
- [x] Verify backward compatibility with old cache files
- [x] Verify `core_periphery.csv` and `cross_project_overlap.csv` output
- [x] Unit tests for `_compute_core_periphery()` (empty, star graph, complete graph, weighted edges)
