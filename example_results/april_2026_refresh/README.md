# April 2026 Refresh

This directory contains a **full re-crawl of the 29-repository dataset on 20 April 2026**. It extends the March 13 snapshot in the parent directory with an effort-resolved view of every commit on each repository's default branch, enabling the analyses in Section 4.7 of the paper.

The March 13 snapshot in `example_results/` remains the primary dataset for Sections 4.1–4.6 of the paper (bus factor, HHI, correlations, partial correlations, group comparisons). This April refresh is the primary dataset for Section 4.7 (weekly elephant factor, churn ratio, effort Gini).

## What's New

| Addition | Why |
|---|---|
| `lines_added` and `lines_removed` columns in `contributor_weekly_activity.csv` | Previously the CSV only had per-week commit counts. The April crawl records additions and deletions per (contributor, ISO-week) via a GraphQL bulk query, enabling effort-weighted analyses |
| `weekly_activity_analysis/` subfolder | Three derived CSVs + a summary Markdown covering Analysis A (Weekly Elephant Factor), Analysis B (Churn Ratio) and Analysis D (Effort Gini) |
| Re-run of all crawler collectors | Gives a 6-week refresh of the base metrics alongside the new LOC data |

## Data Collection Details

| | |
|---|---|
| **Date collected** | 20 April 2026 |
| **Configuration** | `config.example.yaml` |
| **Repositories** | 29 repos from 10 organisations (same list as March snapshot) |
| **Contributors (person_metrics)** | 445 total (410 human, 35 bot) |
| **Contributors (contributor_weekly_activity, GraphQL)** | 893 unique |
| **Total commits** | 80,807 |
| **Lines added (cumulative)** | 19,036,152 |
| **Lines removed (cumulative)** | 17,553,880 |
| **Commit history coverage** | Full default-branch history (earliest 2015-02-16) |
| **Crawl time** | ~7.5 hours |
| **Key implementation change** | GraphQL batched commit fetching (100 commits per API call) replaced per-commit REST calls, giving ~35× speedup. Also added httpx-based replacements for the PyGithub stats endpoints, after discovering that PyGithub's recursive retry on HTTP 202 responses triggered `RecursionError` on large repositories |

## Why contributor counts differ between files

- `person_metrics.csv` (445 contributors) is built from the `/stats/contributors` endpoint, which summarises weekly contribution activity for default-branch commits linked to GitHub user accounts, plus a commit-history fallback (capped at 500 commits) for repositories where stats are unavailable.
- `contributor_weekly_activity.csv` (893 unique `contributor_id`s) is built from GraphQL over **every** commit on the default branch, with contributors keyed by GitHub login *or* author email when no login is linked. It therefore includes email-only authors that `stats/contributors` omits. The two files are consistent but describe slightly different populations; use `contributor_weekly_activity.csv` when you need the long tail of drive-by or anonymous contributors.

## Output Files

### Crawl data (same schema as March snapshot)

| File | Rows | Notes |
|---|---|---|
| `repo_metrics.csv` | 29 | Repository-level metrics |
| `person_metrics.csv` | 445 | Per-contributor metrics |
| `temporal_summary.csv` | 29 | PR / tag / release counts |
| `chaoss_summary.csv` | 29 | 45+ CHAOSS and extended columns |
| `pull_requests.csv` | 40,311 | PR records |
| `tags.csv` | 2,115 | Git tags |
| `core_periphery.csv` | 227 | Per-contributor network analysis |
| `weekly_snapshots.csv` | 3,799 | Weekly commit/contributor snapshots |
| `contributor_lifecycles.csv` | 1,085 | Per-contributor first/last commit, active/departed |
| **`contributor_weekly_activity.csv`** | **12,449** | **Per-person weekly activity; now includes `lines_added` and `lines_removed`** |
| `issue_records.csv` | 16,295 | Individual issue records |
| `issue_summary.csv` | 29 | Aggregated issue analytics |
| `cross_project_overlap.csv` | 282 | Contributors active in multiple crawled repos |
| `full_results.json` | — | Complete nested data for all 29 repositories |
| `<repo>_data.json` × 29 | — | Per-repository cache files |

### Weekly activity analysis (Section 4.7)

| File | Description |
|---|---|
| `weekly_activity_analysis/weekly_elephant_factor.csv` | Per repo: mean top-contributor share per week, % elephant weeks, % single-contributor weeks |
| `weekly_activity_analysis/churn_ratio.csv` | Per repo: overall churn ratio (deletions / (additions+deletions)), net LOC delta, % deletion-heavy weeks |
| `weekly_activity_analysis/effort_gini.csv` | Per repo: Gini coefficient of lines_changed per contributor, Gini of commits per contributor, top1 share |
| `weekly_activity_analysis/summary.md` | Human-readable rundown of the most striking findings |

### Statistical analysis (refreshed on April data)

The April data yields slightly different medians and correlation coefficients than the March snapshot (e.g. HHI-no-bots median: 2,606 → 4,979; burstiness CV median: 1.57 → 0.91). The paper's Section 4.1–4.6 numerical claims correspond to the **March** analysis in the parent directory; this April stat analysis is included for reproducibility of the underlying crawl, not to replace the paper's reported values.

| File | Rows |
|---|---|
| `statistical_analysis/dataset_summary.csv` | 1 |
| `statistical_analysis/descriptive_statistics.csv` | 25 |
| `statistical_analysis/normality_tests.csv` | 12 |
| `statistical_analysis/spearman_correlations.csv` | 17 |
| `statistical_analysis/spearman_p_values.csv` | 17 |
| `statistical_analysis/correlation_pairs_fdr.csv` | 136 |
| `statistical_analysis/partial_correlations.csv` | 7 |
| `statistical_analysis/group_comparisons.csv` | 18 |
| `statistical_analysis/bot_impact.csv` | 29 |
| `statistical_analysis/wilcoxon_bot_impact.csv` | 3 |
| `statistical_analysis/maturity_analysis.csv` | 12 |
| `statistical_analysis/org_kruskal_wallis.csv` | 8 |

## Reproducing this refresh

```bash
# Crawl the 29 repositories — needs ~4–8 hours of continuous network time
GITHUB_TOKEN=$(gh auth token) caffeinate -i uv run civic-tech-crawler \
    --config config.example.yaml --force

# Derived analyses
uv run python scripts/statistical_analysis.py output
uv run python scripts/weekly_activity_analysis.py

# Results land in ./output/; copy to example_results/april_2026_refresh/ to snapshot
```

The `caffeinate -i` prefix is macOS-specific and prevents the system from sleeping during the long crawl; on Linux, run inside `screen` / `tmux` or equivalent.
