# Example Results — Pilot Run

These files are real output from a pilot run of the Civic Tech Git Crawler, included so you can browse the tool's output without running it yourself.

---

## Data Collection Details

| | |
|---|---|
| **Date collected** | 20 February 2026 |
| **Tool version** | v0.2.0 |
| **Configuration** | `config.example.yaml` (included in repository root) |
| **API calls consumed** | ~1,300 requests |
| **Crawl time** | ~17 minutes |
| **GitHub API rate limit** | 5,000 requests/hour (authenticated) |

## Repositories Crawled

| Repository | Category | Origin | Age | Contributors | Commits | Primary Language |
|-----------|----------|--------|-----|-------------|---------|-----------------|
| [DemocracyClub/UK-Polling-Stations](https://github.com/DemocracyClub/UK-Polling-Stations) | Electoral infrastructure | UK NGO | 11 years | 33 | 8,419 | Python |
| [DemocracyClub/WhoCanIVoteFor](https://github.com/DemocracyClub/WhoCanIVoteFor) | Voter information | UK NGO | 10 years | 29 | 3,327 | Python |
| [fvialibre/edia](https://github.com/fvialibre/edia) | AI fairness research | Argentine NGO | 2 years | 3 | 81 | Jupyter Notebook |

## Output Files

| File | Rows | Description |
|------|------|-------------|
| `repo_metrics.csv` | 3 | Repository-level metrics: stars, forks, languages, license, CI/CD, community health score, cloud/AI-ML detection |
| `person_metrics.csv` | 66 | Per-contributor metrics: commit counts, lines added/deleted, averages per commit |
| `temporal_summary.csv` | 3 | PR counts (total, merged, open, closed), tag and release counts per repository |
| `chaoss_summary.csv` | 3 | 39 columns of CHAOSS and extended metrics: bus factor, burstiness, retention cohorts, responsiveness, HHI, DORA, core-periphery, and more |
| `pull_requests.csv` | 7,176 | Individual PR records with timestamps and authors |
| `tags.csv` | 0 | Git tags (none of the pilot repos use formal tagging) |
| `core_periphery.csv` | 13 | Per-contributor network analysis: degree/betweenness centrality, core/periphery classification |
| `cross_project_overlap.csv` | 47 | Contributors and how many of the crawled repos they contribute to |
| `full_results.json` | — | Complete nested data for all repositories in a single JSON file (same data as the CSVs, but in hierarchical format suitable for programmatic analysis) |

## Key Highlights

Some notable findings from this pilot dataset:

- **Bus factor 1-2** across all projects — even the 11-year-old UK-Polling-Stations depends on just 2 developers for 50% of commits
- **Elephant factor 1** everywhere — a single organisation accounts for the majority of commits in each project
- **HHI 5,071-7,655** — all projects exceed the "highly concentrated" threshold of 2,500
- **Stale issue ratios 68-98%** — the majority of open issues have had no activity for 90+ days
- **PR reviews are fast (4-23h median)** but shallow (0.11 comments/PR average)
- **40.4% contributor overlap** — 19 of 47 unique contributors are active in both DemocracyClub projects
- **Core-periphery structure**: UK-Polling-Stations has 2 core / 3 periphery reviewers; WhoCanIVoteFor has a single core reviewer acting as hub

## How to Reproduce

```bash
# Clone and install
git clone <repository-url>
cd civic_tech_git_crawler
uv sync

# Run with the example configuration
GITHUB_TOKEN=$(gh auth token) uv run civic-tech-crawler --config config.example.yaml

# Results will appear in ./output/
```

Note: Results may differ from these examples due to repository activity since the data was collected.

## How to Load in Python

```python
import pandas as pd

# Browse repository metrics
repos = pd.read_csv("example_results/repo_metrics.csv")
print(repos[["full_name", "stars", "forks", "num_developers", "total_commits"]])

# Browse CHAOSS metrics
chaoss = pd.read_csv("example_results/chaoss_summary.csv")
print(chaoss[["repo_full_name", "bus_factor", "burstiness_cv", "stale_issue_ratio",
              "core_contributor_count", "periphery_contributor_count"]])

# Browse core-periphery network
cp = pd.read_csv("example_results/core_periphery.csv")
print(cp[["repo_full_name", "login", "classification", "degree_centrality"]])
```

## How to Load in R

```r
library(readr)

repos <- read_csv("example_results/repo_metrics.csv")
chaoss <- read_csv("example_results/chaoss_summary.csv")
core_periphery <- read_csv("example_results/core_periphery.csv")
overlap <- read_csv("example_results/cross_project_overlap.csv")
```
