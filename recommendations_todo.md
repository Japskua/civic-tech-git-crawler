# Recommendations Implementation Checklist

Based on the analysis in `recommended_actions_20_02_2026.md`.

## HIGH Priority (Implement First)

- [x] **Elephant Factor** -- Minimum number of organizations whose contributors account for 50% of commits. CHAOSS metric, zero additional API calls (reuses existing org diversity data). *Files: models.py, chaoss_metrics.py, cache.py, csv_exporter.py*

- [x] **Contributor Retention Cohorts** -- Classify contributors as new (1 active week), casual (2-12 weeks), or regular (13+ weeks). Uses existing `get_stats_contributors()` weekly data. *Files: models.py, chaoss_metrics.py, cache.py, csv_exporter.py*

- [x] **Time to First Response (Issues)** -- Median hours from issue creation to first non-author comment. Sampled from last 100 issues. *Files: models.py, chaoss_metrics.py, cache.py, csv_exporter.py*

- [x] **Time to First Response (PRs)** -- Median hours from PR creation to first non-author comment. Sampled from last 100 PRs. *Files: models.py, chaoss_metrics.py, cache.py, csv_exporter.py*

## LOW Effort (Implement Second)

- [x] **Documentation Freshness** -- Last commit date on README.md and CONTRIBUTING.md. Two API calls per repo. *Files: client.py, models.py, chaoss_metrics.py, cache.py, csv_exporter.py*

- [x] **Stale Issue Ratio** -- Percentage of open issues with no activity for 90+ days. *Files: models.py, chaoss_metrics.py, cache.py, csv_exporter.py*

- [x] **PR Review Depth & Turnaround** -- Median hours from PR creation to first formal review, and average review comments per PR. Sampled from last 100 merged PRs. *Files: models.py, chaoss_metrics.py, cache.py, csv_exporter.py*

## Supporting Changes

- [x] Add 15 new fields to `ChaossMetrics` dataclass in `models.py`
- [x] Update `_dict_to_chaoss_metrics()` in `cache.py` with `.get()` defaults
- [x] Update `_export_chaoss_summary()` headers in `csv_exporter.py`
- [x] Add `get_last_commit_date_for_path()` method to `client.py`
- [x] Update `README.md` with new metrics documentation

## Testing

- [x] Run `--force` crawl against 3 test repos
- [x] Verify new columns in `chaoss_summary.csv`
- [x] Verify new fields in per-repo JSON cache files
- [x] Verify `--export-only` works with new cache format
- [x] Verify backward compatibility with old cache files

## Future Work (Not in This Branch)

- [ ] Core-Periphery Network Analysis (centrality metrics)
- [ ] Institutional Type Classification (government/nonprofit/academic/company)
- [ ] Cross-Project Contributor Overlap
- [ ] DORA Metrics (deployment frequency, lead time)
- [ ] Herfindahl-Hirschman Index for org concentration
