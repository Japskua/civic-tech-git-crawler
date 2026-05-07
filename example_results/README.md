# Example Results

These files are real output from the Civic Tech Git Crawler, included so you can browse the tool's output without running it yourself.

The repository ships **three full crawl snapshots** in this directory:

- **March 13, 2026 baseline** (the files in this top-level directory) — n=29, the prior version of the analysis.
- **April 20, 2026 refresh** in [`april_2026_refresh/`](april_2026_refresh/) — n=29 with per-(contributor, week) `lines_added` / `lines_removed` columns added to `contributor_weekly_activity.csv`.
- **May 2026 canonical dataset** in [`may_2026/`](may_2026/) — **n=37**, the dataset that backs the current `paper_draft.md`. Adds 8 larger and older civic-tech projects over the prior n=29 sample, organised one folder per repository for easy navigation.

The current paper analyses live in `may_2026/`. The March and April snapshots are kept for historical comparison and for reproducing the prior n=29 analysis if needed.

---

## Data Collection Details

| | |
|---|---|
| **Date collected** | 13 March 2026 |
| **Tool version** | v0.4.0 |
| **Configuration** | `config.example.yaml` (included in repository root) |
| **Repositories** | 29 repos from 10 organisations |
| **Contributors** | 694 total (642 human, 52 bot) |
| **Total commits** | 79,084 |
| **API calls consumed** | ~25,000 requests |
| **Crawl time** | ~90 minutes |
| **GitHub API rate limit** | 5,000 requests/hour (authenticated) |

## Repositories Crawled

| Repository | Organisation | Primary Language | Age (years) | Contributors | Commits |
|---|---|---|---|---|---|
| [DemocracyClub/UK-Polling-Stations](https://github.com/DemocracyClub/UK-Polling-Stations) | DemocracyClub | Python | 11.1 | 33 | 8,499 |
| [DemocracyClub/WhoCanIVoteFor](https://github.com/DemocracyClub/WhoCanIVoteFor) | DemocracyClub | Python | 10.0 | 29 | 3,353 |
| [fvialibre/edia](https://github.com/fvialibre/edia) | fvialibre | Jupyter Notebook | 3.4 | 3 | 81 |
| [fvialibre/heseia-sentence-bias-dataset](https://github.com/fvialibre/heseia-sentence-bias-dataset) | fvialibre | — | 0.8 | 1 | 9 |
| [luftdata/luftdata.se](https://github.com/luftdata/luftdata.se) | luftdata | SCSS | 8.1 | 4 | 206 |
| [CodeForAfrica/PromiseTracker](https://github.com/CodeForAfrica/PromiseTracker) | CodeForAfrica | TypeScript | 6.5 | 4 | 423 |
| [CodeForAfrica/academy.AFRICA](https://github.com/CodeForAfrica/academy.AFRICA) | CodeForAfrica | PHP | 2.4 | 3 | 700 |
| [CodeForAfrica/Dominion.AFRICA](https://github.com/CodeForAfrica/Dominion.AFRICA) | CodeForAfrica | JavaScript | 6.7 | 7 | 574 |
| [CodeForAfrica/GenderGap.AFRICA](https://github.com/CodeForAfrica/GenderGap.AFRICA) | CodeForAfrica | JavaScript | 9.0 | 11 | 254 |
| [CodeForAfrica/openAFRICA](https://github.com/CodeForAfrica/openAFRICA) | CodeForAfrica | Dockerfile | 8.5 | 6 | 154 |
| [CodeForAfrica/outbreak.AFRICA](https://github.com/CodeForAfrica/outbreak.AFRICA) | CodeForAfrica | JavaScript | 6.0 | 11 | 1,352 |
| [CodeForAfrica/ui](https://github.com/CodeForAfrica/ui) | CodeForAfrica | JavaScript | 3.7 | 19 | 10,656 |
| [CodeForAfrica/sensors.AFRICA](https://github.com/CodeForAfrica/sensors.AFRICA) | CodeForAfrica | JavaScript | 7.8 | 19 | 1,271 |
| [codeforamerica/form-flow](https://github.com/codeforamerica/form-flow) | codeforamerica | Java | 3.5 | 18 | 1,303 |
| [codeforamerica/vita-min](https://github.com/codeforamerica/vita-min) | codeforamerica | Ruby | 6.4 | 49 | 7,177 |
| [codeforamerica/tofu-modules-aws-serverless-database](https://github.com/codeforamerica/tofu-modules-aws-serverless-database) | codeforamerica | HCL | 1.6 | 3 | 39 |
| [codeforamerica/tax-benefits-backend](https://github.com/codeforamerica/tax-benefits-backend) | codeforamerica | HCL | 1.9 | 9 | 164 |
| [codeforamerica/pya](https://github.com/codeforamerica/pya) | codeforamerica | Ruby | 0.8 | 8 | 233 |
| [codeforamerica/honeycrisp-gem](https://github.com/codeforamerica/honeycrisp-gem) | codeforamerica | Ruby | 7.6 | 30 | 415 |
| [codeforamerica/asap_pdf](https://github.com/codeforamerica/asap_pdf) | codeforamerica | Ruby | 1.1 | 4 | 599 |
| [codeforamerica/cmr-maryland-eligibility-determination](https://github.com/codeforamerica/cmr-maryland-eligibility-determination) | codeforamerica | Python | 1.0 | 1 | 49 |
| [codeforamerica/document-transfer-service](https://github.com/codeforamerica/document-transfer-service) | codeforamerica | Ruby | 1.9 | 1 | 13 |
| [markov-root/atlas](https://github.com/markov-root/atlas) | markov-root | Astro | 0.2 | 1 | 41 |
| [codeforjapan/BirdXplorer](https://github.com/codeforjapan/BirdXplorer) | codeforjapan | Python | 2.5 | 9 | 682 |
| [meshtastic/Meshtastic-Android](https://github.com/meshtastic/Meshtastic-Android) | meshtastic | Kotlin | 6.1 | 99 | 6,024 |
| [meshtastic/web](https://github.com/meshtastic/web) | meshtastic | TypeScript | 4.9 | 71 | 1,509 |
| [meshtastic/firmware](https://github.com/meshtastic/firmware) | meshtastic | C++ | 6.1 | 395 | 11,456 |
| [civiform/civiform](https://github.com/civiform/civiform) | civiform | Java | 5.2 | 92 | 7,612 |
| [iiab/iiab](https://github.com/iiab/iiab) | iiab | Jinja | 8.8 | 27 | 14,236 |

## Output Files

### Crawl Data

| File | Rows | Description |
|------|------|-------------|
| `repo_metrics.csv` | 29 | Repository-level metrics: stars, forks, languages, license, CI/CD, community health score, cloud/AI-ML detection |
| `person_metrics.csv` | 694 | Per-contributor metrics: commit counts, lines added/deleted, averages per commit, bot detection (`is_bot` flag) |
| `temporal_summary.csv` | 29 | PR counts (total, merged, open, closed), tag and release counts per repository |
| `chaoss_summary.csv` | 29 | 45+ columns of CHAOSS and extended metrics: bus factor (with/without bots), burstiness, retention cohorts, responsiveness, HHI (3 variants), DORA, core-periphery, and more |
| `pull_requests.csv` | 39,117 | Individual PR records with timestamps and authors |
| `tags.csv` | 2,012 | Git tags per repository |
| `core_periphery.csv` | 229 | Per-contributor network analysis: degree/betweenness centrality, core/periphery classification |
| `weekly_snapshots.csv` | 3,885 | Weekly commit/contributor counts with cumulative totals per repository |
| `contributor_lifecycles.csv` | 1,059 | Per-contributor lifecycle: first/last commit, duration, active/departed status |
| `contributor_weekly_activity.csv` | 12,579 | Per-person weekly commit counts |
| `issue_records.csv` | 16,004 | Individual issue records with author, closer, comments, labels |
| `issue_summary.csv` | 29 | Aggregated issue analytics per repository |
| `cross_project_overlap.csv` | 524 | Contributors and how many of the crawled repos they contribute to |
| `full_results.json` | — | Complete nested data for all repositories in a single JSON file (same data as the CSVs, but in hierarchical format suitable for programmatic analysis) |

### Statistical Analysis

| File | Rows | Description |
|------|------|-------------|
| `statistical_analysis/dataset_summary.csv` | 1 | High-level dataset summary: repo count, org count, language count, contributor totals |
| `statistical_analysis/descriptive_statistics.csv` | 25 | Descriptive stats (count, mean, std, min, Q1, median, Q3, max, IQR) for 25 metrics |
| `statistical_analysis/normality_tests.csv` | 12 | Shapiro–Wilk tests for key metrics (11/12 non-normal) |
| `statistical_analysis/spearman_correlations.csv` | 17 | 17×17 Spearman rank correlation matrix |
| `statistical_analysis/spearman_p_values.csv` | 17 | 17×17 p-value matrix for correlations |
| `statistical_analysis/correlation_pairs_fdr.csv` | 136 | All pairwise correlations with Benjamini–Hochberg FDR correction (36 survive at α=0.05) |
| `statistical_analysis/partial_correlations.csv` | 10 | Partial Spearman correlations controlling for num_developers (5 robust, 5 confounded) |
| `statistical_analysis/group_comparisons.csv` | 18 | Mann–Whitney U tests comparing CI/CD, cloud, AI/ML, and license groups with Cliff's delta effect sizes |
| `statistical_analysis/bot_impact.csv` | 29 | Per-repo bot contributor counts and metric comparisons (with/without bots) |
| `statistical_analysis/wilcoxon_bot_impact.csv` | 3 | Wilcoxon signed-rank paired tests for bot impact on HHI, bus factor, elephant factor |
| `statistical_analysis/maturity_analysis.csv` | 12 | Mature vs. young project comparison (median age split at 5.2 years) |
| `statistical_analysis/org_kruskal_wallis.csv` | 8 | Kruskal–Wallis cross-organisation comparisons (codeforamerica, CodeForAfrica, meshtastic) |

### Visualisations

| Directory | Files | Description |
|---|---|---|
| `plots/` | 165 | PNG visualisations: growth curves, weekly activity, top contributors, contributor lifecycles, new contributors over time, and issue trends — generated per repository |

## Key Highlights

Notable findings from the n=29 dataset:

- **Bus factor median 2** (range 1–11 without bots) — most civic tech projects are one or two departures from critical risk
- **Elephant factor median 1** — a single organisation accounts for the majority of commits in almost every project
- **HHI median 5,685 → 2,606 after bot filtering** — bot contributors significantly inflate organisational concentration (Wilcoxon p = 6×10⁻⁵)
- **75% stale issue ratio** — three quarters of open issues go stale across the dataset
- **36 FDR-significant correlations** from 136 pairs tested; strongest: bus_factor ↔ HHI (ρ = −0.935)
- **5 of 10 key correlations confounded by project size** — partial correlations reveal that bus_factor ↔ health and burstiness ↔ health are entirely explained by team size
- **Mature projects (≥5.2y) have significantly more developers** (p = 0.003, Cliff's δ = 0.64) and higher health scores (p = 0.012)
- **Burstiness does not decrease with age** (p = 0.926) — irregular development persists regardless of project maturity
- **Organisational differences**: CodeForAfrica projects are significantly more bursty than codeforamerica or meshtastic (Kruskal–Wallis p = 0.010)
- **694 contributors** tracked, with 52 bots detected via heuristic pattern matching

## How to Reproduce

```bash
# Clone and install
git clone <repository-url>
cd civic_tech_git_crawler
uv sync

# Run the crawler with the example configuration
GITHUB_TOKEN=$(gh auth token) uv run civic-tech-crawler --config config.example.yaml

# Results will appear in ./output/

# Run statistical analysis on the results
uv run python scripts/statistical_analysis.py

# Generate visualisations
uv run python scripts/visualize.py
```

Note: Results may differ from these examples due to repository activity since the data was collected.

## How to Load in Python

```python
import pandas as pd

# Browse repository metrics
repos = pd.read_csv("example_results/repo_metrics.csv")
print(repos[["full_name", "stars", "forks", "num_developers", "total_commits"]])

# Browse CHAOSS metrics (with and without bot filtering)
chaoss = pd.read_csv("example_results/chaoss_summary.csv")
print(chaoss[["repo_full_name", "bus_factor", "bus_factor_no_bots",
              "herfindahl_hirschman_index", "hhi_no_bots",
              "burstiness_cv", "stale_issue_ratio"]])

# Browse bot impact
bots = pd.read_csv("example_results/statistical_analysis/bot_impact.csv")
print(bots[["repo_full_name", "bot_contributor_count", "bot_commit_count"]])

# Browse correlations (FDR-corrected)
corr = pd.read_csv("example_results/statistical_analysis/correlation_pairs_fdr.csv")
significant = corr[corr["significant_fdr"] == True]
print(significant[["var_a", "var_b", "rho", "p_value"]].head(20))

# Browse partial correlations
partial = pd.read_csv("example_results/statistical_analysis/partial_correlations.csv")
print(partial[["var_a", "var_b", "rho_zero_order", "rho_partial", "interpretation"]])
```

### Deep temporal analytics

```python
# Load contributor lifecycles
lifecycles = pd.read_csv("example_results/contributor_lifecycles.csv")
print(lifecycles[["repo_full_name", "contributor_id", "status", "activity_ratio"]])

# Load issue analytics
issues = pd.read_csv("example_results/issue_records.csv")
print(issues[["repo_full_name", "number", "state", "time_to_close_days"]])

# Load weekly snapshots
snapshots = pd.read_csv("example_results/weekly_snapshots.csv")
print(snapshots[["repo_full_name", "week_start", "total_commits", "cumulative_commits"]])
```

## How to Load in R

```r
library(readr)

repos <- read_csv("example_results/repo_metrics.csv")
chaoss <- read_csv("example_results/chaoss_summary.csv")
core_periphery <- read_csv("example_results/core_periphery.csv")
overlap <- read_csv("example_results/cross_project_overlap.csv")

# Statistical analysis results
correlations <- read_csv("example_results/statistical_analysis/correlation_pairs_fdr.csv")
partial <- read_csv("example_results/statistical_analysis/partial_correlations.csv")
maturity <- read_csv("example_results/statistical_analysis/maturity_analysis.csv")
```
