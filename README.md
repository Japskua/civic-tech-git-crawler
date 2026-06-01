# Civic Tech Git Crawler

A Python command-line tool for collecting comprehensive metrics from GitHub repositories. Designed for academic research on civic technology contributions, contributor networks, and open-source community health.

The tool implements metrics from the [CHAOSS](https://chaoss.community/) (Community Health Analytics in Open Source Software) framework alongside standard repository statistics, contributor-level code change analysis, and automated detection of cloud infrastructure and AI/ML technology usage.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Authentication](#authentication)
- [Configuration](#configuration)
- [Usage](#usage)
- [Output Files](#output-files)
- [Dataset](#dataset)
- [Metrics Reference](#metrics-reference)
  - [Repository Metrics](#repository-metrics)
  - [Contributor Metrics](#contributor-metrics)
  - [Temporal Metrics](#temporal-metrics)
  - [CHAOSS Metrics](#chaoss-metrics)
  - [Technology Detection](#technology-detection)
  - [Commit History & Contributor Lifecycles](#commit-history--contributor-lifecycles)
  - [Issue Analytics](#issue-analytics)
- [Incremental Runs & Crash Recovery](#incremental-runs--crash-recovery)
- [Analysis Pipeline](#analysis-pipeline)
- [Statistical Analysis](#statistical-analysis)
- [Weekly Activity Analysis](#weekly-activity-analysis)
- [API Rate Limits](#api-rate-limits)
- [Visualization](#visualization)
- [Examples](#examples)
- [Extending the Tool](#extending-the-tool)
- [Citing This Tool and the Dataset](#citing-this-tool-and-the-dataset)
- [License](#license)

---

## Quick Start

```bash
# 1. Clone and enter the project
git clone <repository-url>
cd civic_tech_git_crawler

# 2. Install dependencies (requires uv: https://docs.astral.sh/uv/)
uv sync

# 3. Set your GitHub token
export GITHUB_TOKEN="ghp_your_token_here"

# 4. Crawl the canonical civic-tech corpus (57 repos — long-running)
uv run civic-tech-crawler --config config.example.yaml

# 5. Find results in ./datasets/2026_05/
ls datasets/2026_05/
```

> A full 57-repo crawl takes several hours and is best run through the
> resumable, auto-respawning wrapper — see
> [Incremental Runs & Crash Recovery](#incremental-runs--crash-recovery). To try
> the tool quickly, copy `config.example.yaml` to `config.yaml` and trim the
> `repositories:` list to one or two entries first.

### Run with Docker

A `Dockerfile` is included for reproducible runs without managing a local Python
environment. The image is built from the same `pyproject.toml`, ships the
crawler CLI plus the resumable wrapper at `scripts/run_with_respawn.sh`, and
reads `/config/config.yaml` writing to `/output` by default.

```bash
# 1. Build the image (~1 min, ~800 MB)
docker build -t civic-tech-crawler .

# 2. Single-pass crawl — uses the image's default ENTRYPOINT
docker run --rm \
    -e GITHUB_TOKEN="$(gh auth token)" \
    -v "$PWD/config.yaml:/config/config.yaml:ro" \
    -v "$PWD/datasets/2026_05:/output" \
    civic-tech-crawler

# 3. Or — long, multi-hour crawl via the auto-respawning wrapper
docker run --rm \
    -e GITHUB_TOKEN="$(gh auth token)" \
    -v "$PWD/config.yaml:/config/config.yaml:ro" \
    -v "$PWD/datasets/2026_05:/output" \
    --entrypoint /app/scripts/run_with_respawn.sh \
    civic-tech-crawler /config/config.yaml /output 57

# 4. Inspect the CLI without mounting anything
docker run --rm civic-tech-crawler --help
```

The image is verified on every CI run (see `.github/workflows/ci.yml`).

---

## Installation

### Prerequisites

- **Python 3.13+**
- **[uv](https://docs.astral.sh/uv/)** package manager (install via `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- A **GitHub Personal Access Token** with `public_repo` scope

### Install

```bash
git clone <repository-url>
cd civic_tech_git_crawler
uv sync
```

This installs the following dependencies:

| Package | Purpose |
|---------|---------|
| [PyGithub](https://github.com/PyGithub/PyGithub) | GitHub API v3 client with typed objects and automatic pagination |
| [httpx](https://www.python-httpx.org/) | HTTP client for API endpoints not covered by PyGithub |
| [NetworkX](https://networkx.org/) | Graph analysis library for core-periphery network metrics |
| [PyYAML](https://pyyaml.org/) | YAML configuration file parsing |
| [Matplotlib](https://matplotlib.org/) | Chart generation for the visualization script |
| [Pandas](https://pandas.pydata.org/) | Data loading and manipulation for the visualization script |
| [SciPy](https://scipy.org/) | Statistical testing (Spearman, Mann-Whitney U, Wilcoxon, Kruskal-Wallis, Shapiro-Wilk) |
| [NumPy](https://numpy.org/) | Numerical computation for statistical analysis |
| [Rich](https://rich.readthedocs.io/) | Terminal progress bars and formatted output |

---

## Authentication

The tool requires a GitHub Personal Access Token (PAT) to access the GitHub API. A token with `public_repo` scope is sufficient for public repositories.

### Creating a token

1. Go to [GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select the `public_repo` scope
4. Copy the generated token

### Providing the token

**Option A: Environment variable (recommended)**

```bash
export GITHUB_TOKEN="ghp_your_token_here"
uv run civic-tech-crawler --config config.yaml
```

**Option B: GitHub CLI (if you have `gh` installed)**

```bash
GITHUB_TOKEN=$(gh auth token) uv run civic-tech-crawler --config config.yaml
```

**Option C: CLI flag**

```bash
uv run civic-tech-crawler --config config.yaml --token "ghp_your_token_here"
```

### Rate limits

- **Without token**: 60 requests/hour (practically unusable)
- **With token**: 5,000 requests/hour (sufficient for ~15-50 repositories per run)

---

## Configuration

Create a `config.yaml` file (copy from `config.example.yaml` as a starting point):

```bash
cp config.example.yaml config.yaml
```

### Full configuration reference

```yaml
# GitHub API settings
github:
  max_retries: 5            # Retry attempts for stats endpoints returning 202
  retry_delay: 3            # Base delay in seconds between retries (linear backoff)
  rate_limit_buffer: 100    # Pause when this many API calls remain

# Repositories to crawl (owner/repo format).
# config.example.yaml ships with the full canonical 57-repo civic-tech
# corpus (2026-05 refresh). See datasets/2026_05/README.md for the manifest
# and selection rationale.
repositories:
  - "DemocracyClub/UK-Polling-Stations"
  - "mastodon/mastodon"
  - "compdemocracy/polis"
  # … 35 more — see config.example.yaml

# Output settings
output:
  directory: "./datasets/2026_05"   # Where to write CSV and JSON files

# Technology detection keywords (fully customizable)
detection:
  cloud_keywords:
    topics:                 # GitHub topics that indicate cloud usage
      - aws
      - gcp
      - azure
      - cloud
      - serverless
      - kubernetes
      - docker
    languages:              # Programming languages that indicate cloud
      - HCL
      - Dockerfile
    files:                  # Files in the repository root that indicate cloud
      - Dockerfile
      - docker-compose.yml
      - docker-compose.yaml
      - cdk.json
      - serverless.yml
      - terraform.tf
      - cloudbuild.yaml
      - appspec.yml
      - Procfile
      - .buildpacks
    dependencies:           # Package dependencies that indicate cloud
      - boto3
      - google-cloud
      - azure
      - aws-cdk
      - pulumi

  ai_ml_keywords:
    topics:                 # GitHub topics that indicate AI/ML
      - machine-learning
      - deep-learning
      - ai
      - nlp
      - computer-vision
      - artificial-intelligence
    languages:              # Languages that indicate AI/ML
      - Jupyter Notebook
    files:                  # File patterns (wildcards supported)
      - "*.ipynb"
    dependencies:           # Package dependencies that indicate AI/ML
      - tensorflow
      - pytorch
      - torch
      - scikit-learn
      - transformers
      - keras
      - xgboost
      - lightgbm
      - openai
      - langchain
      - huggingface
      - spacy
      - nltk
```

### Configuration priority

Settings are resolved in this order (highest priority first):

1. **CLI flags** (`--token`, `--repos`, `--output-dir`)
2. **Environment variables** (`GITHUB_TOKEN`)
3. **config.yaml values**
4. **Built-in defaults**

The YAML file supports environment variable expansion using `${VAR_NAME}` syntax.

---

## Usage

### Basic usage

```bash
uv run civic-tech-crawler --config config.yaml
```

### All CLI flags

```
usage: civic-tech-crawler [-h] [--config CONFIG] [--token TOKEN] [--repos REPOS]
                          [--output-dir OUTPUT_DIR] [--skip-chaoss]
                          [--skip-temporal] [--skip-detection]
                          [--skip-commit-history] [--skip-issue-analytics]
                          [--verbose] [--force] [--export-only]

GitHub repository metrics crawler for civic tech research

options:
  -h, --help               show this help message and exit
  --config CONFIG          Path to YAML configuration file (default: config.yaml)
  --token TOKEN            GitHub personal access token (overrides GITHUB_TOKEN env var)
  --repos REPOS            Comma-separated list of repos (e.g., owner/repo1,owner/repo2)
  --output-dir OUTPUT_DIR  Output directory (default: ./output)
  --skip-chaoss            Skip CHAOSS metrics collection
  --skip-temporal          Skip temporal metrics (PRs, tags, releases)
  --skip-detection         Skip cloud/AI-ML technology detection
  --skip-commit-history    Skip full commit history parsing
  --skip-issue-analytics   Skip detailed issue analytics
  --verbose                Enable debug logging
  --force                  Re-crawl all repos even if cached data exists
  --export-only            Skip crawling; regenerate CSV/JSON from cached per-repo data
```

### Flag details

| Flag | Effect |
|------|--------|
| `--config` | Specifies the YAML configuration file. Defaults to `config.yaml` in the working directory. |
| `--token` | Overrides the `GITHUB_TOKEN` environment variable. Useful for one-off runs. |
| `--repos` | Overrides the repository list from the config file. Comma-separated, no spaces. |
| `--output-dir` | Overrides the output directory. Created automatically if it does not exist. |
| `--skip-chaoss` | Skips CHAOSS metric collection (bus factor, burstiness, defect resolution, etc.). Saves significant API calls. |
| `--skip-temporal` | Skips pulling all PRs, tags, and releases. Useful when only repository-level metrics are needed. Also disables CHAOSS metrics that depend on PR data (acceptance ratio, release frequency). |
| `--skip-detection` | Skips cloud and AI/ML technology detection. Saves a few API calls per repository. |
| `--skip-commit-history` | Skips full commit history parsing (weekly snapshots, contributor lifecycles). Saves ~N/100 API calls per repo where N is the total number of commits. |
| `--skip-issue-analytics` | Skips detailed issue analytics (per-issue records, closer tracking). Saves significant API calls for repos with many closed issues (up to ~2000 calls for the `closed_by` field). |
| `--verbose` | Shows detailed debug output including every HTTP request and response. |
| `--force` | Re-crawl all repositories even if cached results exist in the output directory. Overwrites existing cache files. |
| `--export-only` | Skip crawling entirely. Regenerates all CSV and JSON output files from the existing cached per-repo JSON files in the output directory. Useful for rebuilding exports after manual edits or for merging results from multiple runs. |

### Running with `python -m`

```bash
uv run python -m civic_tech_crawler --config config.yaml
```

---

## Output Files

All output files are written to the output directory (default: `./output/`). Both CSV and JSON formats are produced automatically.

> **Want to see what the output looks like?** Browse the [`datasets/2026_05/`](datasets/2026_05/) directory — the canonical **n=57 civic-tech corpus**. After the analysis pass it is organised one folder per repository, so you can navigate to any single project's metrics, plots, and findings in one click — see [Dataset](#dataset) below.

### CSV files

| File | Rows | Description |
|------|------|-------------|
| `repo_metrics.csv` | 1 per repository | Repository-level metrics (stars, forks, languages, license, CI/CD, etc.) |
| `person_metrics.csv` | 1 per repository-contributor pair | Contributor commit counts, code additions/deletions, averages |
| `temporal_summary.csv` | 1 per repository | PR counts (total, merged, open, closed), tag and release counts |
| `chaoss_summary.csv` | 1 per repository | CHAOSS framework metrics (bus factor, burstiness, acceptance ratio, etc.) |
| `pull_requests.csv` | 1 per pull request | Individual PR records with timestamps and authors |
| `tags.csv` | 1 per tag | Git tags with commit SHAs and dates |
| `core_periphery.csv` | 1 per contributor in review network | Core-periphery network analysis (centrality, classification) per contributor |
| `weekly_snapshots.csv` | 1 per repository-week | Weekly commit/contributor counts with cumulative totals |
| `contributor_lifecycles.csv` | 1 per repository-contributor pair | Contributor lifecycle: first/last commit, duration, activity ratio, active/departed status |
| `contributor_weekly_activity.csv` | 1 per contributor-week pair | Per-person weekly commit counts with lines added / removed |
| `issue_records.csv` | 1 per issue | Individual issue records: author, closer, comments, labels, time-to-close |
| `issue_summary.csv` | 1 per repository | Aggregated issue analytics: counts, averages, top openers/closers |
| `cross_project_overlap.csv` | 1 per unique contributor | Cross-project contributor overlap (login, number of repos contributed to) |

### JSON files

| File | Description |
|------|-------------|
| `full_results.json` | Complete nested data for all repositories in a single file |
| `{Owner}_{Repo}_data.json` | Per-repository cache file with all collected metrics. These files serve as the **persistent cache** for incremental runs and crash recovery (see [Incremental Runs & Crash Recovery](#incremental-runs--crash-recovery)). |

### CSV formatting conventions

- **Lists** are semicolon-separated: `Python;HTML;JavaScript`
- **Dictionaries** are semicolon-separated key=value pairs: `Python=1715697;HTML=102611`
- **Booleans** are `True` or `False`
- **Dates** are ISO 8601 format: `2024-01-15T10:30:00+00:00`
- **Null/missing values** are empty strings

### JSON structure

```json
[
  {
    "repo_metrics": {
      "full_name": "owner/repo",
      "stars": 42,
      "...": "..."
    },
    "person_metrics": [
      {
        "login": "contributor1",
        "num_commits": 150,
        "additions": 12000,
        "deletions": 5000,
        "...": "..."
      }
    ],
    "temporal_metrics": {
      "pr_count_total": 200,
      "prs": [ ... ],
      "tags": [ ... ],
      "releases": [ ... ]
    },
    "chaoss_metrics": {
      "bus_factor": 3,
      "burstiness_cv": 1.27,
      "...": "..."
    },
    "commit_history": {
      "repo_full_name": "owner/repo",
      "total_weeks": 355,
      "total_unique_contributors": 31,
      "new_contributor_rate_per_month": 0.32,
      "weekly_snapshots": [ "..." ],
      "contributor_lifecycles": [ "..." ],
      "contributor_weeks": [ "..." ]
    },
    "issue_analytics": {
      "repo_full_name": "owner/repo",
      "total_issues": 415,
      "open_issues": 102,
      "closed_issues": 313,
      "avg_comments_per_issue": 2.1,
      "median_time_to_close_days": 14.5,
      "issues": [ "..." ]
    }
  }
]
```

---

## Dataset

The canonical dataset lives in [`datasets/2026_05/`](datasets/2026_05/) — the
**n=57 civic-tech corpus** (2026-05 refresh). It supersedes all earlier
exploratory and example runs, which have been removed from the repository. Its
[`README.md`](datasets/2026_05/README.md) holds the full repository manifest
(grouped by community/region), the selection rationale, the data-quality caveats
(forks, placeholder repos, scale outliers), the methodology, and the output-file
index.

| | |
|---|---|
| **Location** | [`datasets/2026_05/`](datasets/2026_05/) |
| **Repositories** | 57 |
| **Organisations** | 24 (US, Canada, Africa, Japan, Taiwan, Germany, UK) |
| **Schema** | identical to every prior run, so any `scripts/` analysis works unchanged |

After the analysis pass, the dataset is organised so each repository has its own
folder containing everything needed to understand that one project at a glance:

```
datasets/2026_05/
├── README.md                   ← manifest, selection rationale, methodology, file index
├── analysis_n57.md             ← academic writeup: headline findings, methodology, threats to validity
├── <owner>_<repo>/             ← one folder per repository (38 total)
│   ├── repo_results.md         ← at-a-glance metadata + main finding + caveats
│   ├── data.json               ← full crawler output for this repo
│   └── *.png                   ← growth / lifecycle / contributors / weekly activity / issue trend plots
├── repo_metrics.csv            ← aggregate CSVs (one row per repo)
├── chaoss_summary.csv
├── contributor_weekly_activity.csv
├── statistical_analysis/       ← CSVs from scripts/statistical_analysis.py
└── weekly_activity_analysis/   ← CSVs + summary.md from scripts/weekly_activity_analysis.py
```

Each repository's `repo_results.md` contains:

1. **At-a-glance**: language, stars/forks, age, commit count, cloud / AI-ML / OSI-license signals
2. **Main findings**: a short paragraph on the most distinctive aspect of the project
3. **Key metrics**: bus factor, HHI, effort Gini, churn ratio, issue stats, response times
4. **Things to note**: auto-detected caveats (e.g. right-censored 5,000-issue caps, net-negative LOC trajectories)
5. **Files in this folder**: index of the JSON + plot files
6. **See also**: links back to the dataset-level docs

### Reproducing / regenerating the dataset

```bash
export GITHUB_TOKEN=$(gh auth token)

# Full crawl with auto-respawn (resumable; writes to datasets/2026_05/)
setsid nohup env GITHUB_TOKEN="$GITHUB_TOKEN" \
    scripts/run_with_respawn.sh config.yaml datasets/2026_05 57 \
    > crawl.log 2>&1 < /dev/null & disown

# Analysis pass
uv run python scripts/statistical_analysis.py datasets/2026_05/
uv run python scripts/weekly_activity_analysis.py datasets/2026_05/
uv run python scripts/visualize.py --output-dir datasets/2026_05

# (Optional — only for older crawler versions with sparse burstiness coverage;
# the current crawler self-heals.)
uv run python scripts/recompute_burstiness.py datasets/2026_05/

# Build the per-repo folders + repo_results.md files
uv run python scripts/build_repo_folders.py datasets/2026_05/
```

`scripts/run_with_respawn.sh` automatically relaunches the crawler if the process gets externally killed (e.g. by sandbox timeouts), and exits cleanly only when all 57 per-repo cache files are present **and** `full_results.json` has been written. `scripts/build_repo_folders.py` is idempotent — it only moves files that haven't been moved yet, and rewrites the markdown each run from the latest CSVs.

---

## Metrics Reference

### Repository Metrics

These are collected for each repository and exported to `repo_metrics.csv`.

| Metric | Column | Type | Description |
|--------|--------|------|-------------|
| Repository name | `full_name` | string | Full `owner/repo` identifier |
| Description | `description` | string | Repository description |
| Developers | `num_developers` | integer | Total number of unique contributors (falls back to `anon=true` for repos with unlinked commit authors) |
| Commits | `total_commits` | integer | Total commit count across all branches |
| Languages | `languages` | dict | Programming languages with byte counts (e.g., `Python=1715697;HTML=102611`) |
| Primary language | `primary_language` | string | Most-used programming language |
| First commit | `first_commit_date` | datetime | Timestamp of the earliest commit |
| Last commit | `last_commit_date` | datetime | Timestamp of the most recent commit |
| License (SPDX) | `license_spdx` | string | SPDX license identifier (e.g., `MIT`, `GPL-3.0-only`) |
| License (name) | `license_name` | string | Human-readable license name |
| OSI approved | `is_osi_approved` | boolean | Whether the license is [OSI-approved](https://opensource.org/licenses/) |
| Topics | `topics` | list | GitHub repository topics |
| Contributing guide | `has_contributing` | boolean | CONTRIBUTING file present |
| Code of conduct | `has_code_of_conduct` | boolean | CODE_OF_CONDUCT file present |
| Governance | `has_governance` | boolean | GOVERNANCE.md file present |
| README | `has_readme` | boolean | README file present |
| Issue template | `has_issue_template` | boolean | Issue template present |
| PR template | `has_pr_template` | boolean | Pull request template present |
| Community health | `health_percentage` | integer | GitHub community health score (0-100) |
| Stars | `stars` | integer | GitHub star count |
| Watchers | `watchers` | integer | GitHub watcher count (users receiving notifications) |
| Forks | `forks` | integer | Fork count |
| Cloud detected | `cloud_detected` | boolean | Cloud infrastructure technology detected |
| Cloud signals | `cloud_signals` | list | Specific signals that triggered cloud detection |
| AI/ML detected | `ai_ml_detected` | boolean | AI/ML technology detected |
| AI/ML signals | `ai_ml_signals` | list | Specific signals that triggered AI/ML detection |
| CI/CD | `has_ci_cd` | boolean | GitHub Actions workflows present |
| CI/CD workflows | `ci_cd_workflows` | list | Names of CI/CD workflows |
| Deployments | `deployments_count` | integer | Number of GitHub deployments |
| Created | `created_at` | datetime | Repository creation date |
| Updated | `updated_at` | datetime | Last update date (any activity: issues, PRs, settings) |
| Pushed | `pushed_at` | datetime | Last code push date (more accurate for activity filtering than `updated_at`) |
| Size | `size_kb` | integer | Repository size in kilobytes |

**Note on stars vs. watchers:** The GitHub API has a historical naming inconsistency. This tool uses `stargazers_count` for stars and `subscribers_count` for watchers, which are the correct current mappings.

---

### Contributor Metrics

Per-person metrics are exported to `person_metrics.csv`. One row per (repository, contributor) pair.

| Metric | Column | Type | Description |
|--------|--------|------|-------------|
| Repository | `repo_full_name` | string | Repository identifier |
| Username | `login` | string | GitHub username |
| Name | `name` | string | Real name from GitHub profile |
| Bot flag | `is_bot` | boolean | Whether this contributor is detected as a bot |
| Commits | `num_commits` | integer | Total commits by this contributor |
| Additions | `additions` | integer | Total lines of code added |
| Deletions | `deletions` | integer | Total lines of code deleted |
| Avg additions/commit | `avg_additions_per_commit` | float | Mean lines added per commit |
| Avg deletions/commit | `avg_deletions_per_commit` | float | Mean lines deleted per commit |

#### Bot Detection

Contributors are automatically classified as bots using a heuristic detection pipeline. A contributor is flagged as `is_bot = True` if their GitHub login matches any of:

- The `[bot]` suffix (e.g., `dependabot[bot]`, `renovate[bot]`, `github-actions[bot]`)
- Known bot login patterns: `snyk-bot`, `codecov[bot]`, `imgbot[bot]`, `stale[bot]`, `allcontributors[bot]`, `transifex-integration[bot]`
- The general patterns `*-bot` or `*Bot` in the login name

Bot detection enables **dual metric reporting** in the CHAOSS metrics: all concentration metrics (bus factor, elephant factor, HHI) are computed both with and without bot contributors. This follows recommendations from Dey et al. (2020) and Golzadeh et al. (2021).

**Data source:** The GitHub [Repository Statistics API](https://docs.github.com/en/rest/metrics/statistics#get-all-contributor-commit-activity) (`/repos/{owner}/{repo}/stats/contributors`), which returns weekly breakdowns of commits, additions, and deletions per contributor. The tool aggregates all weeks to produce totals and averages. **Fallback:** When the statistics endpoint returns empty (e.g., all commit authors use emails not linked to GitHub accounts), the tool falls back to iterating commits directly (capped at 500) and grouping by author email.

---

### Temporal Metrics

Temporal metrics are exported to `temporal_summary.csv` (summary), `pull_requests.csv` (individual PRs), and `tags.csv` (individual tags).

#### Summary (`temporal_summary.csv`)

| Metric | Column | Type | Description |
|--------|--------|------|-------------|
| Total PRs | `pr_count_total` | integer | Total pull requests (all states) |
| Merged PRs | `pr_count_merged` | integer | Successfully merged pull requests |
| Open PRs | `pr_count_open` | integer | Currently open pull requests |
| Closed (unmerged) | `pr_count_closed_unmerged` | integer | Closed without merging |
| Tags | `tag_count` | integer | Total git tags |
| Releases | `release_count` | integer | Total GitHub releases |

#### Individual PR records (`pull_requests.csv`)

| Column | Type | Description |
|--------|------|-------------|
| `repo_full_name` | string | Repository identifier |
| `number` | integer | PR number |
| `title` | string | PR title |
| `state` | string | `open` or `closed` |
| `author_login` | string | PR author's GitHub username |
| `created_at` | datetime | When the PR was opened |
| `merged_at` | datetime | When the PR was merged (empty if not merged) |
| `closed_at` | datetime | When the PR was closed (empty if still open) |

#### Individual tag records (`tags.csv`)

| Column | Type | Description |
|--------|------|-------------|
| `repo_full_name` | string | Repository identifier |
| `name` | string | Tag name (e.g., `v1.2.3`) |
| `commit_sha` | string | Associated commit SHA |
| `date` | datetime | Commit date |

---

### CHAOSS Metrics

The tool implements metrics from the [CHAOSS](https://chaoss.community/) framework, a Linux Foundation project that defines implementation-agnostic metrics for assessing open-source community health.

These are exported to `chaoss_summary.csv` (one row per repository) and in full detail in the JSON output.

#### Common Metrics

| Metric | Column | CHAOSS Definition | Calculation |
|--------|--------|-------------------|-------------|
| Code Changes | `weekly_commits` (JSON only) | [Code Changes Commits](https://chaoss.community/kb/metric-code-changes-commits/) | Weekly commit counts for the past year, from GitHub's commit activity statistics API |
| Acceptance Ratio | `change_request_acceptance_ratio` | [Change Request Acceptance Ratio](https://chaoss.community/kb/metric-change-request-acceptance-ratio/) | `merged_PRs / total_PRs` |
| Bus Factor | `bus_factor` | [Contributor Absence Factor](https://chaoss.community/kb/metric-contributor-absence-factor/) | Minimum number of contributors whose combined commits account for 50% of total commits. Contributors are sorted by commit count in descending order, and counted until the running sum reaches 50%. |
| Contribution Types | `contribution_types` | [Types of Contributions](https://chaoss.community/kb/metric-types-of-contributions/) | Counts of code commits, pull requests, and issues |

#### Diversity, Equity & Inclusion Metrics

| Metric | Column | CHAOSS Definition | Calculation |
|--------|--------|-------------------|-------------|
| Org Diversity | `organizational_diversity` | [Organizational Diversity](https://chaoss.community/kb/metric-organizational-diversity/) | Groups contributors by the `company` field from their GitHub profile. Shows how many contributors belong to each organization. |
| Label Inclusivity | `newcomer_friendly_labels` | [Issue Label Inclusivity](https://chaoss.community/kb/metric-issue-label-inclusivity/) | Counts issue labels matching newcomer-friendly patterns: `good first issue`, `help wanted`, `beginner`, `easy`, `first-timers-only`, `newcomer`, `starter`, `low-hanging-fruit`, `up-for-grabs` |

#### Evolution Metrics

| Metric | Column | CHAOSS Definition | Calculation |
|--------|--------|-------------------|-------------|
| Release Frequency | `release_frequency_per_month` | [Release Frequency](https://chaoss.community/kb/metric-release-frequency/) | `total_releases / months_between_first_and_last_release` (requires at least 2 releases) |
| Technical Fork | `fork_count` | [Technical Fork](https://chaoss.community/kb/metric-technical-fork/) | Total fork count from GitHub API |
| Burstiness | `burstiness_cv`, `burstiness_mean`, `burstiness_std` | [Burstiness](https://chaoss.community/kb/metric-burstiness/) | Statistical analysis of weekly commit counts. **CV (Coefficient of Variation)** = standard deviation / mean. Higher CV indicates more irregular (bursty) development patterns. |

**Interpreting burstiness:** A `burstiness_cv` close to 0 indicates steady, consistent development. A value above 1.0 indicates highly variable activity with bursts of development followed by quiet periods.

#### Risk Metrics

| Metric | Column | CHAOSS Definition | Calculation |
|--------|--------|-------------------|-------------|
| Defect Resolution | `median_defect_resolution_days` | [Defect Resolution Duration](https://chaoss.community/kb/defect-resolution-duration/) | Median number of days from issue creation to closure for issues labeled `bug`. Fetches up to 500 closed bug issues. |
| OSI License | `osi_approved_license` | [OSI Approved Licenses](https://chaoss.community/kb/metric-osi-approved-licenses/) | Checks the repository's SPDX license identifier against a set of 98 OSI-approved licenses |

#### Extended Community Health Metrics

These metrics extend the core CHAOSS framework with additional indicators recommended by academic literature on open-source sustainability.

| Metric | Column | Description | Calculation |
|--------|--------|-------------|-------------|
| Elephant Factor | `elephant_factor` | Organizational-level bus factor (Goggins et al., 2021) | Minimum number of organizations whose contributors account for 50% of commits. Same algorithm as bus factor, applied at org level. |
| Contributor Retention | `contributor_new_count`, `contributor_casual_count`, `contributor_regular_count` | Contributor cohort analysis (Zhou & Mockus, 2012) | Classifies contributors by active weeks: **new** (1 week), **casual** (2-12 weeks), **regular** (13+ weeks). |
| Time to First Response (Issues) | `median_time_to_first_response_issues_hours` | CHAOSS: Time to First Response | Median hours from issue creation to first non-author comment. Sampled from last 100 issues. |
| Time to First Response (PRs) | `median_time_to_first_response_prs_hours` | CHAOSS: Time to First Response | Median hours from PR creation to first non-author comment. Sampled from last 100 PRs. |
| Documentation Freshness | `readme_last_updated`, `contributing_last_updated` | Documentation quality signal (Prana et al., 2019) | Date of the most recent commit touching README.md and CONTRIBUTING.md. |
| Stale Issue Ratio | `stale_issue_ratio`, `stale_issue_count`, `open_issue_count` | Issue responsiveness indicator | Percentage of open issues with no activity for 90+ days. |
| PR Review Turnaround | `median_pr_review_turnaround_hours` | Code review quality (Rigby & Bird, 2013) | Median hours from PR creation to first formal review. Sampled from last 100 merged PRs. |
| PR Review Depth | `avg_review_comments_per_pr` | Code review quality (Bosu et al., 2017) | Average number of review comments per PR. Sampled from last 100 merged PRs. |
| HHI (Org Concentration) | `herfindahl_hirschman_index` | Market concentration index (Rhoades, 1993) | Herfindahl-Hirschman Index computed on organizational commit shares. Ranges from 0 (perfectly diverse) to 10,000 (single-org monopoly). |
| Institutional Classification | `contributor_org_types` | Institutional diversity (Schweik & English, 2012) | Classifies contributors into government, academic, nonprofit, company, or unknown based on GitHub profile company field pattern matching. |
| DORA Deployment Frequency | `dora_deployment_frequency_per_month` | DORA / Accelerate (Forsgren et al., 2018) | Number of releases per month over the repository's lifetime. |
| DORA Lead Time | `dora_median_lead_time_days` | DORA / Accelerate (Forsgren et al., 2018) | Median days between consecutive releases (proxy for time from code change to production). |
| DORA Change Failure Rate | `dora_change_failure_rate` | DORA / Accelerate (Forsgren et al., 2018) | Ratio of revert/hotfix/bugfix PRs to total merged PRs (heuristic from PR title patterns). |
| Core Contributors | `core_contributor_count` | Core-periphery structure (Crowston & Howison, 2006) | Number of contributors classified as "core" in the PR review collaboration network. Uses degree centrality above the median threshold. |
| Periphery Contributors | `periphery_contributor_count` | Core-periphery structure (Crowston & Howison, 2006) | Number of contributors classified as "periphery" in the PR review collaboration network. |
| Core-Periphery Ratio | `core_periphery_ratio` | Core-periphery structure (Crowston & Howison, 2006) | Proportion of core contributors: `core / (core + periphery)`. |
| Network Density | `network_density` | Social network analysis | Ratio of actual edges to possible edges in the PR review collaboration graph. Higher density = more interconnected reviews. |
| Avg Degree Centrality | `avg_degree_centrality` | Social network analysis | Average number of unique collaborators per person (normalized). Higher values indicate broader collaboration patterns. |

#### Bot-Filtered Metrics

All concentration metrics are computed in dual mode — with and without bot contributors — to assess the impact of automated accounts on project health indicators. The following additional columns are present in `chaoss_summary.csv`:

| Metric | Column | Description |
|--------|--------|-------------|
| Bus Factor (no bots) | `bus_factor_no_bots` | Bus factor computed excluding bot contributors |
| Elephant Factor (no bots) | `elephant_factor_no_bots` | Elephant factor computed excluding bot contributors |
| HHI (no bots) | `hhi_no_bots` | HHI where each unknown-affiliation contributor is treated as their own org (not lumped into "Unknown") and bots are excluded |
| HHI (known orgs only) | `hhi_known_orgs_only` | HHI computed using only contributors with known organisational affiliation |
| Bot contributor count | `bot_contributor_count` | Number of bot contributors detected in this repository |
| Bot commit count | `bot_commit_count` | Total commits by bot contributors |
| Unknown org contributors | `unknown_org_contributor_count` | Number of contributors with unknown organisational affiliation |

**Interpreting the three HHI variants:**
- `herfindahl_hirschman_index`: Original HHI — all unknown-affiliation contributors lumped into one "Unknown" org. Can inflate concentration artificially.
- `hhi_no_bots`: Improved HHI — bots excluded, each unknown contributor treated as their own org. Better reflects true organisational diversity.
- `hhi_known_orgs_only`: Strictest HHI — only contributors with identified organisations. Most accurate but smallest sample.

In antitrust economics, HHI < 1,500 = unconcentrated, 1,500–2,500 = moderately concentrated, > 2,500 = highly concentrated (US DOJ guidelines).

#### Core-Periphery Network Analysis

A separate CSV file (`core_periphery.csv`) provides per-contributor network analysis:

| Column | Description |
|--------|-------------|
| `repo_full_name` | Repository identifier |
| `login` | GitHub username |
| `degree_centrality` | Normalized count of unique collaborators (0-1) |
| `betweenness_centrality` | How often this person bridges between other collaborators (0-1) |
| `classification` | `core` or `periphery` based on degree centrality above/below median |
| `num_collaborators` | Raw number of unique people this contributor has reviewed or been reviewed by |

The collaboration graph is built from PR author↔reviewer pairs extracted during the PR review metrics pass (last 100 merged PRs). Zero additional API calls required.

#### Cross-Project Contributor Overlap

A separate CSV file (`cross_project_overlap.csv`) is exported with contributor-level overlap data:

| Column | Description |
|--------|-------------|
| `login` | GitHub username |
| `repos_contributed_to` | Number of crawled repositories this contributor appears in |

Summary statistics (total unique contributors, multi-repo count, multi-repo ratio) are printed to the console after each run.

---

### Technology Detection

The detection module uses a multi-signal approach to identify cloud infrastructure and AI/ML technology usage. It checks four signal categories for each technology type:

1. **Topics** -- GitHub repository topic tags
2. **Languages** -- Programming languages used in the repository
3. **Files** -- Presence of specific files in the repository root
4. **Dependencies** -- Package names in `requirements.txt`, `pyproject.toml`, or `package.json`

Each detected signal is recorded in the format `{category}:{keyword}` (e.g., `file:Dockerfile`, `dependency:boto3`, `language:Jupyter Notebook`).

Detection is positive (`cloud_detected: True` or `ai_ml_detected: True`) if **at least one signal** is found. All keyword lists are fully configurable in `config.yaml`.

---

### Commit History & Contributor Lifecycles

The commit history collector parses the **full commit history** of each repository (not limited to the 52-week window of the GitHub Statistics API). This enables long-term temporal analysis of project activity and contributor engagement patterns.

**Data source:** The GitHub GraphQL API — `Repository.defaultBranchRef.target.history(first: 100, after: $cursor)` — fetches 100 commits per API call and returns `oid`, `additions`, `deletions`, `committedDate`, author email/name, and author GitHub login in a single payload. This is roughly **35× faster** than the previous per-commit REST pattern (benchmarked on an 8,700-commit repo: ~3 minutes vs. ~50 minutes at the 5 000/hour rate limit) and gives us line-level effort data "for free" as part of the same request. **API cost:** ~1 call per 100 commits (i.e. `ceil(N / 100)` where N is the commit count).

> **Implementation note on PyGithub.** The collector previously used PyGithub's `Commit.stats` lazy-load for per-commit additions/deletions. PyGithub's `Requester.__requestRaw` retries HTTP 202 responses *recursively* ([Requester.py:1238](https://github.com/PyGithub/PyGithub/blob/main/github/Requester.py)); for GitHub's stats endpoints that take minutes to compute, the retries accumulate Python stack frames until `RecursionError` is raised. The GraphQL rewrite bypasses that code path entirely. The companion httpx-based `GitHubClient.get_stats_contributors` and `get_stats_commit_activity` methods do the same for the REST stats endpoints with an iterative (for-loop) retry.

#### Weekly Snapshots (`weekly_snapshots.csv`)

One row per (repository, ISO week) pair. Weeks are aligned to Monday start dates.

| Column | Type | Description |
|--------|------|-------------|
| `repo_full_name` | string | Repository identifier |
| `week_start` | date | Monday of the ISO week (e.g., `2024-01-08`) |
| `total_commits` | integer | Number of commits in this week |
| `unique_contributors` | integer | Number of distinct contributors in this week |
| `new_contributors` | integer | Number of contributors making their first-ever commit in this week |
| `cumulative_commits` | integer | Running total of commits up to and including this week |
| `cumulative_contributors` | integer | Running total of unique contributors up to and including this week |

#### Contributor Lifecycles (`contributor_lifecycles.csv`)

One row per (repository, contributor) pair. Provides lifecycle analysis for each contributor.

| Column | Type | Description |
|--------|------|-------------|
| `repo_full_name` | string | Repository identifier |
| `contributor_id` | string | Unique identifier: GitHub login if linked, else author email |
| `login` | string | GitHub username (empty if commit author has no linked account) |
| `name` | string | Name from commit metadata |
| `email` | string | Email from commit metadata |
| `first_commit_date` | datetime | Timestamp of this contributor's first commit |
| `last_commit_date` | datetime | Timestamp of this contributor's most recent commit |
| `duration_days` | integer | Days between first and last commit |
| `total_commits` | integer | Total number of commits by this contributor |
| `active_weeks` | integer | Number of ISO weeks with at least one commit |
| `total_weeks_span` | integer | Total ISO weeks from first to last commit |
| `activity_ratio` | float | `active_weeks / total_weeks_span` — measures engagement density (1.0 = committed every week) |
| `status` | string | `active` if last commit within 90 days, `departed` otherwise |
| `departed_weeks_ago` | integer | Weeks since last commit (only for departed contributors) |
| `avg_commits_per_active_week` | float | `total_commits / active_weeks` |

**Contributor identification:** Uses the GitHub login associated with the commit author if available. Falls back to the commit author email for unlinked accounts. This is consistent with the person metrics collector.

**Departure detection:** Contributors with no commits in the last 90 days are classified as `departed`. The `departed_weeks_ago` field shows how long ago they were last active.

#### Contributor Weekly Activity (`contributor_weekly_activity.csv`)

One row per (repository, contributor, ISO week) triple. Only weeks where the contributor made at least one commit are included. The `lines_added` and `lines_removed` columns come from the same GraphQL commit-history query that produces the weekly snapshots — there is no extra API cost.

| Column | Type | Description |
|--------|------|-------------|
| `repo_full_name` | string | Repository identifier |
| `contributor_id` | string | Unique identifier (login or email) |
| `week_start` | date | Monday of the ISO week |
| `commits` | integer | Number of commits by this contributor in this week |
| `lines_added` | integer | Sum of `additions` across this contributor's commits in this week (non-negative) |
| `lines_removed` | integer | Sum of `deletions` across this contributor's commits in this week (non-negative) |

**Interpretation of line counts.** GitHub reports per-commit `additions` and `deletions` as non-negative integers computed as the diff against the commit's first parent. Every row is therefore non-negative, but summing `lines_added − lines_removed` across a repository's entire default-branch history can be negative — this happens when the traversed history contains large deletions not offset by equally large earlier additions (e.g. repositories where bulk data files are replaced with smaller versions over many commits, or where vendored directories that predate the current default branch are later purged). Two repositories in the example dataset exhibit this pattern (`DemocracyClub/UK-Polling-Stations` and `CodeForAfrica/sensors.AFRICA`). The crawler therefore reports `lines_added` and `lines_removed` separately rather than a signed delta.

---

### Issue Analytics

The issue analytics collector retrieves **all issues** (excluding pull requests) with per-issue detail and summary statistics. This enables analysis of community engagement, issue responsiveness, and contributor participation patterns.

**Data source:** `repo.get_issues(state="all")` — paginated iteration through all issues. Pull requests are filtered out. The `closed_by` field requires an individual issue fetch per closed issue (capped at 2,000). **API cost:** ~M/100 + C calls (M = total issues, C = closed issues, capped at 2,000).

#### Issue Records (`issue_records.csv`)

One row per issue (excluding pull requests).

| Column | Type | Description |
|--------|------|-------------|
| `repo_full_name` | string | Repository identifier |
| `number` | integer | Issue number |
| `title` | string | Issue title |
| `state` | string | `open` or `closed` |
| `author_login` | string | GitHub username of the issue author |
| `closed_by_login` | string | GitHub username of the person who closed the issue (empty if open) |
| `created_at` | datetime | When the issue was created |
| `closed_at` | datetime | When the issue was closed (empty if open) |
| `updated_at` | datetime | When the issue was last updated |
| `comment_count` | integer | Number of comments on the issue |
| `labels` | list | Semicolon-separated label names |
| `time_to_close_days` | float | Days from creation to closure (empty if open) |

#### Issue Summary (`issue_summary.csv`)

One row per repository with aggregated issue analytics.

| Column | Type | Description |
|--------|------|-------------|
| `repo_full_name` | string | Repository identifier |
| `total_issues` | integer | Total number of issues (excluding PRs) |
| `open_issues` | integer | Currently open issues |
| `closed_issues` | integer | Closed issues |
| `avg_comments_per_issue` | float | Mean number of comments across all issues |
| `median_time_to_close_days` | float | Median days from creation to closure for closed issues |
| `unique_openers` | integer | Number of distinct users who opened issues |
| `unique_closers` | integer | Number of distinct users who closed issues |
| `top_openers` | dict | Semicolon-separated `login=count` pairs for most frequent issue openers |
| `top_closers` | dict | Semicolon-separated `login=count` pairs for most frequent issue closers |

---

## Incremental Runs & Crash Recovery

The tool supports **incremental crawling**, meaning you can run it in parts across multiple sessions and the results accumulate automatically. This is essential when crawling large numbers of repositories.

### How it works

After each repository is successfully crawled, its data is immediately saved as a per-repo JSON file (`{Owner}_{Repo}_data.json`) in the output directory. On subsequent runs, the tool checks for these files and skips already-crawled repositories.

At export time, all per-repo cache files in the output directory are loaded and merged into the aggregated CSV and JSON output files — even repos crawled in previous sessions.

### Scenarios

| Scenario | What happens |
|----------|-------------|
| First run with 10 repos | Crawls all 10, saves 10 JSON cache files, exports CSV/JSON |
| Second run with same 10 repos | Loads all 10 from cache (zero API calls), re-exports CSV/JSON |
| Second run with 5 *new* repos | Crawls only the 5 new repos. Export merges all 15 repos into CSV/JSON. |
| Crash at repo #6 of 10 | Repos 1–5 are already saved to disk. Re-run loads 1–5 from cache, crawls 6–10. |
| `--force` with 10 repos | Re-crawls all 10 regardless of cache, overwrites cache files |
| `--export-only` | No crawling. Rebuilds CSV/JSON from all cached per-repo files in the output directory |

### Example: Multi-session workflow

```bash
# Session 1: Crawl first batch of repos
uv run civic-tech-crawler --repos "org/repo1,org/repo2,org/repo3"

# Session 2 (next day): Crawl more repos — previous results are preserved
uv run civic-tech-crawler --repos "org/repo4,org/repo5,org/repo6"

# Session 3: Rebuild all exports from cached data (no API calls)
uv run civic-tech-crawler --export-only

# The output CSV/JSON now contains all 6 repositories
```

### Refreshing stale data

To re-crawl a specific repository (e.g., to get updated metrics), delete its cache file and re-run:

```bash
# Delete cache for one repo
rm output/DemocracyClub_UK-Polling-Stations_data.json

# Re-run — only the deleted repo will be re-crawled
uv run civic-tech-crawler --config config.yaml
```

To re-crawl everything:

```bash
uv run civic-tech-crawler --config config.yaml --force
```

---

## Analysis Pipeline

The tool follows a sequential pipeline for each repository. Understanding this pipeline helps in interpreting the results and estimating API usage.

```
                          +-----------------------+
                          |    Load Configuration |
                          |   (YAML + CLI + env)  |
                          +-----------+-----------+
                                      |
                          +-----------v-----------+
                          |  Initialize GitHub    |
                          |  API Client           |
                          +-----------+-----------+
                                      |
                    +-----------------v------------------+
                    |       FOR EACH REPOSITORY          |
                    |                                    |
                    |  +-----------------------------+   |
                    |  | 0. CHECK CACHE              |   |
                    |  |    - If cached → load & skip|   |
                    |  |    - If --force → re-crawl  |   |
                    |  +-------------+---------------+   |
                    |                |                    |
                    |  +-------------v---------------+   |
                    |  | 1. REPO METRICS             |   |
                    |  |    - Basic info & languages  |   |
                    |  |    - Commit history (first/  |   |
                    |  |      last dates, total count)|   |
                    |  |    - Community health profile|   |
                    |  |    - CI/CD workflows         |   |
                    |  |    - Deployments             |   |
                    |  +-------------+---------------+   |
                    |                |                    |
                    |  +-------------v---------------+   |
                    |  | 2. PERSON METRICS            |   |
                    |  |    - Contributor stats with  |   |
                    |  |      weekly breakdowns       |   |
                    |  |    - User profile lookup     |   |
                    |  |      (cached across repos)   |   |
                    |  +-------------+---------------+   |
                    |                |                    |
                    |  +-------------v---------------+   |
                    |  | 3. DETECTION (optional)      |   |
                    |  |    - Scan root files         |   |
                    |  |    - Parse dependency files  |   |
                    |  |    - Match keywords          |   |
                    |  +-------------+---------------+   |
                    |                |                    |
                    |  +-------------v---------------+   |
                    |  | 4. TEMPORAL METRICS (opt.)   |   |
                    |  |    - All pull requests       |   |
                    |  |    - All tags                |   |
                    |  |    - All releases            |   |
                    |  +-------------+---------------+   |
                    |                |                    |
                    |  +-------------v---------------+   |
                    |  | 5. CHAOSS METRICS (optional) |   |
                    |  |    - Weekly commit activity  |   |
                    |  |    - Bus factor calculation  |   |
                    |  |    - Acceptance ratio        |   |
                    |  |    - Org diversity           |   |
                    |  |    - Label inclusivity       |   |
                    |  |    - Burstiness stats        |   |
                    |  |    - Defect resolution       |   |
                    |  +-------------+---------------+   |
                    |                |                    |
                    |  +-------------v---------------+   |
                    |  | 6. COMMIT HISTORY (optional) |   |
                    |  |    - GraphQL history query   |   |
                    |  |      (100 commits / call)    |   |
                    |  |    - Weekly snapshots         |   |
                    |  |    - Contributor lifecycles   |   |
                    |  |    - Per-(person,week) LOC    |   |
                    |  |    - Departure detection      |   |
                    |  +-------------+---------------+   |
                    |                |                    |
                    |  +-------------v---------------+   |
                    |  | 7. ISSUE ANALYTICS (optional)|   |
                    |  |    - All issues (no PRs)     |   |
                    |  |    - Per-issue records        |   |
                    |  |    - Closer attribution       |   |
                    |  |    - Summary statistics       |   |
                    |  +-------------+---------------+   |
                    |                |                    |
                    |  +-------------v---------------+   |
                    |  | 8. SAVE TO CACHE             |   |
                    |  |    - Immediate persistence   |   |
                    |  |    - Crash-safe (per-repo)   |   |
                    |  +-----------------------------+   |
                    |                                    |
                    +------------------+-----------------+
                                       |
                          +------------v-------------+
                          |    EXPORT RESULTS        |
                          |    - 13 CSV files        |
                          |    - Full JSON           |
                          |    (from all cached data)|
                          +--------------------------+
```

### Pipeline characteristics

- **Incremental & crash-safe:** Each repository is saved to disk immediately after crawling. If the process is interrupted, already-crawled repos are preserved and loaded from cache on the next run.
- **Error isolation:** If one repository fails, the tool continues with the remaining repositories. Failed repositories are logged and excluded from the output.
- **Progress reporting:** A Rich progress bar shows current repository and collection step in the terminal.
- **Collector dependencies:** CHAOSS metrics depend on data from person metrics and temporal metrics. If temporal metrics are skipped (`--skip-temporal`), dependent CHAOSS metrics (acceptance ratio, release frequency) will be `null`.
- **User info caching:** Contributor profile lookups are cached in memory. If the same person contributes to multiple repositories, their profile is fetched only once.

### Retry mechanism

GitHub's statistics endpoints (`/stats/contributors`, `/stats/commit_activity`) are computed asynchronously. The API returns HTTP 202 while computing, which means the data is not yet ready. The tool handles this with:

- **Linear backoff**: Waits 3s, 6s, 9s, 12s, 15s between attempts
- **Maximum 5 retries** (configurable via `github.max_retries`)
- **Graceful degradation**: If stats are unavailable after all retries, the affected metrics are recorded as `null` rather than failing the entire repository
- **Anonymous contributor fallback**: If the contributors endpoint returns 0 but commits exist (e.g., all authors use unlinked emails), the tool retries with `anon=true`. Person metrics fall back to commit-based counting (capped at 500 commits)

---

## Statistical Analysis

A standalone statistical analysis script performs comprehensive non-parametric testing on the crawled data. This is designed for academic research papers and generates publication-ready CSV tables.

### Usage

```bash
# Run statistical analysis on crawled data
uv run python scripts/statistical_analysis.py

# Specify a custom output directory
uv run python scripts/statistical_analysis.py --output-dir ./my_output
```

Output files are saved to `{output-dir}/statistical_analysis/`.

### Analyses Performed

| Analysis | Output File | Description |
|----------|-------------|-------------|
| Dataset summary | `dataset_summary.csv` | High-level overview: repo count, org count, language count, contributor totals (human vs. bot) |
| Descriptive statistics | `descriptive_statistics.csv` | Count, mean, std, min, Q1, median, Q3, max, IQR for 25+ metrics |
| Normality tests | `normality_tests.csv` | Shapiro-Wilk tests for key metrics (justifies non-parametric methods) |
| Correlation matrix | `spearman_correlations.csv` | 17x17 Spearman rank correlation matrix |
| P-value matrix | `spearman_p_values.csv` | 17x17 p-value matrix for correlations |
| FDR-corrected pairs | `correlation_pairs_fdr.csv` | All pairwise correlations with Benjamini-Hochberg FDR correction |
| Partial correlations | `partial_correlations.csv` | Partial Spearman correlations controlling for num_developers (disentangles size effects) |
| Group comparisons | `group_comparisons.csv` | Mann-Whitney U tests (CI/CD, cloud, AI/ML, license) with Cliff's delta effect sizes |
| Bot impact | `bot_impact.csv` | Per-repo bot counts and metric comparisons (with/without bots) |
| Bot impact tests | `wilcoxon_bot_impact.csv` | Wilcoxon signed-rank paired tests for bot impact on HHI, bus factor, elephant factor |
| Maturity analysis | `maturity_analysis.csv` | Mature vs. young project comparison (median age split) with Mann-Whitney U |
| Organisation comparison | `org_kruskal_wallis.csv` | Kruskal-Wallis H tests comparing metrics across organisations (≥3 repos each) |

### Statistical Methods

**Why non-parametric?** The script first runs Shapiro-Wilk normality tests on all key metrics. In the canonical 2026-05 dataset (n=57), most key metrics are significantly non-normal (p < 0.05), justifying the exclusive use of non-parametric methods.

| Method | Purpose | When Used |
|--------|---------|-----------|
| Shapiro-Wilk | Normality testing | All key metrics |
| Spearman rank correlation | Monotonic relationships | All metric pairs (136 unique pairs for 17 metrics) |
| Benjamini-Hochberg FDR | Multiple testing correction | Applied to all 136 correlation p-values at alpha=0.05 |
| Partial Spearman correlation | Control for confounders | 10 key pairs, controlling for num_developers |
| Mann-Whitney U | Two-group comparison | CI/CD vs. no CI/CD, mature vs. young, etc. |
| Cliff's delta | Non-parametric effect size | All two-group comparisons |
| Wilcoxon signed-rank | Paired comparison | Metrics with bots vs. without bots (same repos) |
| Kruskal-Wallis H | Multi-group comparison | Cross-organisation differences (3+ groups) |
| Epsilon-squared | Kruskal-Wallis effect size | All multi-group comparisons |

### Example: Loading Statistical Results

```python
import pandas as pd

# Which correlations survived FDR correction?
corr = pd.read_csv("output/statistical_analysis/correlation_pairs_fdr.csv")
significant = corr[corr["significant_fdr"] == True]
print(f"{len(significant)} of {len(corr)} pairs survive FDR correction")
print(significant[["var_a", "var_b", "rho", "p_value"]].head(10))

# Which relationships are confounded by project size?
partial = pd.read_csv("output/statistical_analysis/partial_correlations.csv")
robust = partial[partial["interpretation"] == "robust"]
confounded = partial[partial["interpretation"] == "confounded"]
print(f"Robust: {len(robust)}, Confounded: {len(confounded)}")
print(partial[["var_a", "var_b", "rho_zero_order", "rho_partial", "interpretation"]])

# Does bot filtering change concentration metrics?
wilcoxon = pd.read_csv("output/statistical_analysis/wilcoxon_bot_impact.csv")
print(wilcoxon[["comparison", "median_with", "median_without", "p_value", "significant"]])

# How do mature vs. young projects differ?
maturity = pd.read_csv("output/statistical_analysis/maturity_analysis.csv")
sig = maturity[maturity["p_value"] < 0.05]
print(sig[["metric", "mature_median", "young_median", "p_value", "cliffs_delta", "effect_magnitude"]])
```

---

## Weekly Activity Analysis

A second analysis script derives effort-resolved sustainability metrics from the per-(contributor, week) `lines_added` / `lines_removed` data in `contributor_weekly_activity.csv`. These analyses complement the count-based metrics in `statistical_analysis/` with an effort-weighted view of contributor concentration.

### Usage

```bash
uv run python scripts/weekly_activity_analysis.py
```

Reads `output/contributor_weekly_activity.csv` and writes to `output/weekly_activity_analysis/`.

### Analyses Performed

| Analysis | Output File | Description |
|---|---|---|
| Weekly Elephant Factor | `weekly_elephant_factor.csv` | Per repo: mean share of weekly `lines_added + lines_removed` contributed by the single busiest author that week; percentage of weeks where that share ≥ 50% ("elephant weeks") and ≥ 99.9% ("single-contributor weeks"). A time-resolved complement to the static elephant factor in `chaoss_summary.csv`. |
| Churn Ratio | `churn_ratio.csv` | Per repo: overall and weekly `deletions / (additions + deletions)`, alongside total adds/removes, net LOC delta, and percentage of deletion-heavy weeks. Values close to 0 indicate growth mode, close to 1 indicate cleanup/rewrite mode. |
| Effort Gini | `effort_gini.csv` | Per repo: Gini coefficient of total `lines_added + lines_removed` per contributor, paired with the Gini of per-contributor commit counts. The gap between the two quantifies how much effort-weighted concentration exceeds count-based concentration. |
| Summary | `summary.md` | Human-readable Markdown rundown of the most striking findings across all three analyses. |

### Example: Loading weekly activity results

```python
import pandas as pd

# Which repos are most dominated by one contributor week-by-week?
elephant = pd.read_csv("output/weekly_activity_analysis/weekly_elephant_factor.csv")
print(elephant.sort_values("mean_top_share", ascending=False)
              .head(10)[["repo_full_name", "mean_top_share",
                         "elephant_weeks_pct", "single_contributor_weeks_pct"]])

# Which repos are in growth vs. maintenance mode?
churn = pd.read_csv("output/weekly_activity_analysis/churn_ratio.csv")
print(churn[["repo_full_name", "overall_churn_ratio", "net_loc_delta"]]
        .sort_values("overall_churn_ratio", ascending=False))

# How much does count-based concentration under-estimate effort concentration?
gini = pd.read_csv("output/weekly_activity_analysis/effort_gini.csv")
gini["gini_gap"] = gini["effort_gini_lines"] - gini["effort_gini_commits"]
print(gini.sort_values("gini_gap", ascending=False)
          [["repo_full_name", "effort_gini_lines", "effort_gini_commits", "gini_gap"]]
          .head(10))
```

---

## API Rate Limits

### Estimated API usage per repository

| Collection Step | API Calls |
|----------------|-----------|
| Repository metadata + languages + community profile | ~5 |
| Commits (count + first/last) | ~3 |
| Statistics endpoints (contributors + weekly activity) | ~2-10 (with retries) |
| User profile lookups (cached) | ~5-50 (depends on contributors) |
| Pull requests (paginated, 100/page) | ~1-50 (depends on PR count) |
| Tags + releases | ~2-5 |
| Detection (root files + dependency files) | ~3-5 |
| Labels + bug issues | ~2-10 |
| Full commit history (paginated) | ~N/100 (N = total commits) |
| Issue analytics (list + closed_by) | ~M/100 + C (M = issues, C = closed, capped at 2,000) |
| **Total per repository** | **~25-500** |

### Planning your runs

| Repositories | Estimated API Calls | Time (approx.) |
|-------------|--------------------|----|
| 3 | 75-1,500 | 1-10 minutes |
| 10 | 250-5,000 | 5-30 minutes |
| 50 | 1,250-25,000 | 30-120 minutes (use incremental runs) |
| 100+ | 2,500+ | Use incremental runs across sessions |

The tool monitors remaining API calls and automatically sleeps when the rate limit is nearly exhausted, resuming when the limit resets (every hour). For large-scale crawling, the [incremental caching](#incremental-runs--crash-recovery) feature means you can split runs across multiple sessions without losing progress.

### Reducing API usage

Use skip flags to disable expensive collectors:

```bash
# Fastest: only repo-level metrics and person metrics
uv run civic-tech-crawler --skip-temporal --skip-chaoss --skip-detection

# Skip only CHAOSS (which depends on temporal data anyway)
uv run civic-tech-crawler --skip-chaoss

# Skip the deep temporal analytics (commit history + issue analytics)
uv run civic-tech-crawler --skip-commit-history --skip-issue-analytics
```

---

## Visualization

A standalone visualization script generates publication-ready PNG charts from the crawled CSV data.

### Usage

```bash
# Generate all charts for all repositories
uv run python scripts/visualize.py --output-dir ./output

# Generate charts for a single repository
uv run python scripts/visualize.py --output-dir ./output --repo DemocracyClub/WhoCanIVoteFor
```

Charts are saved to `output/plots/` as PNG files at 150 DPI.

### Chart types

| Chart | Filename | Description |
|-------|----------|-------------|
| Project Growth | `{repo}_growth.png` | Dual-axis line chart of cumulative commits and cumulative contributors over time |
| Weekly Activity | `{repo}_weekly_activity.png` | Bar chart of weekly commit counts with a contributor count overlay line |
| Contributor Lifecycles | `{repo}_lifecycle.png` | Horizontal Gantt chart showing the active period of the top 30 contributors (green = active, red = departed) |
| New Contributor Rate | `{repo}_new_contributors.png` | Bar chart of new contributors per week with a 4-week rolling average line |
| Issue Trends | `{repo}_issue_trends.png` | Monthly issues opened vs. closed with a cumulative open issues area fill |
| Top Contributors | `{repo}_top_contributors.png` | Horizontal bar chart of the top 15 contributors showing additions vs. deletions |

### Data sources

The visualization script reads from these CSV files (generated by the crawler):

- `weekly_snapshots.csv` — growth curves, weekly activity, new contributor rate
- `contributor_lifecycles.csv` — lifecycle Gantt chart
- `issue_records.csv` — issue trend analysis
- `person_metrics.csv` — top contributors chart

---

## Examples

### Example 1: Crawl a single repository

```bash
export GITHUB_TOKEN="ghp_..."
uv run civic-tech-crawler --repos "torvalds/linux" --output-dir ./linux_analysis
```

### Example 2: Crawl multiple specific repositories

```bash
uv run civic-tech-crawler \
  --repos "mysociety/alaveteli,codeforamerica/brigade,decidim/decidim" \
  --output-dir ./civic_tech_analysis
```

### Example 3: Quick scan (skip expensive metrics)

```bash
uv run civic-tech-crawler \
  --config config.yaml \
  --skip-temporal \
  --skip-chaoss \
  --output-dir ./quick_scan
```

### Example 4: Incremental crawling across sessions

```bash
# Day 1: Crawl first batch
uv run civic-tech-crawler --repos "org/repo1,org/repo2,org/repo3"

# Day 2: Add more repos (previous 3 loaded from cache, only new ones crawled)
uv run civic-tech-crawler --repos "org/repo1,org/repo2,org/repo3,org/repo4,org/repo5"

# Day 3: Just regenerate exports from all cached data
uv run civic-tech-crawler --export-only
```

### Example 5: Force re-crawl all repos

```bash
uv run civic-tech-crawler --config config.yaml --force
```

### Example 6: Debug mode

```bash
uv run civic-tech-crawler --config config.yaml --verbose 2>&1 | tee crawl.log
```

### Example 7: Run statistical analysis

```bash
# Run full statistical analysis pipeline
uv run python scripts/statistical_analysis.py

# Results appear in output/statistical_analysis/
ls output/statistical_analysis/
# bot_impact.csv  correlation_pairs_fdr.csv  dataset_summary.csv
# descriptive_statistics.csv  group_comparisons.csv  maturity_analysis.csv
# normality_tests.csv  org_kruskal_wallis.csv  partial_correlations.csv
# spearman_correlations.csv  spearman_p_values.csv  wilcoxon_bot_impact.csv
```

### Example 8: Generate visualizations

```bash
# Generate all plots from crawled data
uv run python scripts/visualize.py --output-dir ./output

# Generate plots for a single repository
uv run python scripts/visualize.py --output-dir ./output --repo DemocracyClub/WhoCanIVoteFor

# Output: output/plots/{Owner}_{Repo}_{chart_name}.png
```

### Example 9: Loading results in Python for analysis

```python
import pandas as pd

# Load repository-level metrics
repos = pd.read_csv("output/repo_metrics.csv")
print(repos[["full_name", "stars", "forks", "num_developers", "total_commits"]])

# Load contributor metrics (with bot detection)
contributors = pd.read_csv("output/person_metrics.csv")
humans = contributors[contributors["is_bot"] == False]
bots = contributors[contributors["is_bot"] == True]
print(f"Human contributors: {len(humans)}, Bot contributors: {len(bots)}")

top = humans.sort_values("num_commits", ascending=False).head(10)
print(top[["repo_full_name", "login", "num_commits", "additions", "deletions"]])

# Load CHAOSS metrics (with and without bot filtering)
chaoss = pd.read_csv("output/chaoss_summary.csv")
print(chaoss[["repo_full_name", "bus_factor", "bus_factor_no_bots",
              "herfindahl_hirschman_index", "hhi_no_bots",
              "burstiness_cv", "stale_issue_ratio",
              "bot_contributor_count", "bot_commit_count"]])
```

### Example 10: Loading results in R

```r
library(readr)

repos <- read_csv("output/repo_metrics.csv")
contributors <- read_csv("output/person_metrics.csv")
chaoss <- read_csv("output/chaoss_summary.csv")
prs <- read_csv("output/pull_requests.csv")

# Contributor network analysis
library(dplyr)
contributors %>%
  group_by(login) %>%
  summarise(
    repos = n(),
    total_commits = sum(num_commits),
    total_additions = sum(additions)
  ) %>%
  arrange(desc(total_commits))
```

### Example 11: Loading deep temporal analytics in Python

```python
import pandas as pd

# Load weekly snapshots for growth analysis
snapshots = pd.read_csv("output/weekly_snapshots.csv")
print(snapshots[["repo_full_name", "week_start", "total_commits", "cumulative_commits"]])

# Load contributor lifecycles
lifecycles = pd.read_csv("output/contributor_lifecycles.csv")
active = lifecycles[lifecycles["status"] == "active"]
departed = lifecycles[lifecycles["status"] == "departed"]
print(f"Active: {len(active)}, Departed: {len(departed)}")
print(active[["repo_full_name", "contributor_id", "total_commits", "activity_ratio"]])

# Load issue analytics
issues = pd.read_csv("output/issue_records.csv")
print(issues[["repo_full_name", "number", "state", "comment_count", "time_to_close_days"]])

# Issue summary
summary = pd.read_csv("output/issue_summary.csv")
print(summary[["repo_full_name", "total_issues", "median_time_to_close_days", "unique_openers"]])
```

### Example 12: Full nested JSON analysis

```python
import json

with open("output/full_results.json") as f:
    data = json.load(f)

for repo in data:
    name = repo["repo_metrics"]["full_name"]
    bus = repo["chaoss_metrics"]["bus_factor"] if repo["chaoss_metrics"] else "N/A"
    cloud = repo["repo_metrics"]["cloud_detected"]
    ai_ml = repo["repo_metrics"]["ai_ml_detected"]
    print(f"{name}: bus_factor={bus}, cloud={cloud}, ai_ml={ai_ml}")
```

### Example 13: Working with statistical analysis results

```python
import pandas as pd

# 1. Dataset summary
summary = pd.read_csv("output/statistical_analysis/dataset_summary.csv")
print(f"Repos: {summary['total_repositories'].iloc[0]}")
print(f"Contributors: {summary['total_contributors'].iloc[0]} "
      f"({summary['human_contributors'].iloc[0]} human, "
      f"{summary['bot_contributors'].iloc[0]} bot)")

# 2. Find FDR-significant correlations
corr = pd.read_csv("output/statistical_analysis/correlation_pairs_fdr.csv")
sig = corr[corr["significant_fdr"] == True].sort_values("rho", key=abs, ascending=False)
print(f"\n{len(sig)} FDR-significant correlations:")
print(sig[["var_a", "var_b", "rho", "p_value"]].to_string(index=False))

# 3. Identify confounded vs robust relationships
partial = pd.read_csv("output/statistical_analysis/partial_correlations.csv")
for _, row in partial.iterrows():
    print(f"{row['var_a']} <-> {row['var_b']}: "
          f"zero-order={row['rho_zero_order']:.3f}, "
          f"partial={row['rho_partial']:.3f} -> {row['interpretation']}")

# 4. Bot impact on concentration metrics
wilcoxon = pd.read_csv("output/statistical_analysis/wilcoxon_bot_impact.csv")
for _, row in wilcoxon.iterrows():
    status = "SIGNIFICANT" if row.get("significant") else "not significant"
    print(f"{row['comparison']}: median {row['median_with']:.0f} -> "
          f"{row['median_without']:.0f} (p={row['p_value']}, {status})")

# 5. Mature vs young projects
maturity = pd.read_csv("output/statistical_analysis/maturity_analysis.csv")
sig_mat = maturity[maturity["p_value"] < 0.05]
print(f"\nSignificant maturity differences:")
print(sig_mat[["metric", "mature_median", "young_median",
               "p_value", "cliffs_delta", "effect_magnitude"]].to_string(index=False))
```

### Example 14: End-to-end research workflow

```bash
# 1. Crawl repositories (config.yaml writes to datasets/2026_05/)
GITHUB_TOKEN=$(gh auth token) uv run civic-tech-crawler --config config.yaml

# 2. Run statistical analysis
uv run python scripts/statistical_analysis.py datasets/2026_05/

# 3. Generate visualisations
uv run python scripts/visualize.py --output-dir datasets/2026_05

# 4. datasets/ is version-controlled, so results are committed in place
#    (no copy step needed). Build the per-repo folders for browsing:
uv run python scripts/build_repo_folders.py datasets/2026_05/

# Results are now ready for inclusion in a research paper
```

---

## Extending the Tool

### Adding new repositories

Edit `config.yaml` and add entries to the `repositories` list:

```yaml
repositories:
  - "owner/repo-name"
  - "another-org/another-repo"
```

### Customizing detection keywords

Edit the `detection` section in `config.yaml` to add domain-specific keywords. For example, to detect blockchain technology:

```yaml
detection:
  # ... existing cloud and ai_ml sections ...

  # Note: Custom detection categories require code changes.
  # However, you can expand the existing cloud/ai_ml keyword lists.
  cloud_keywords:
    dependencies:
      - boto3
      - google-cloud
      - azure
      - web3         # Added: blockchain
      - ethers       # Added: blockchain
```

### Adding a new collector

1. Create a new file in `src/civic_tech_crawler/collectors/`
2. Define a dataclass in `models.py` for the new metrics
3. Add the collector call to `crawl_repository()` in `cli.py`
4. Add CSV export columns in `csv_exporter.py`
5. The JSON exporter handles new dataclasses automatically

### Project structure

```
civic_tech_git_crawler/
├── pyproject.toml                  # Dependencies and project metadata
├── config.example.yaml             # Example configuration
├── config.yaml                     # Your configuration (gitignored)
├── paper_draft.md                  # Research paper draft (n=57, 2026-05 corpus)
├── scripts/
│   ├── run_with_respawn.sh             # Resumable, auto-respawning crawl wrapper
│   ├── visualize.py                    # Visualization script (6 chart types)
│   ├── statistical_analysis.py         # Statistical testing (12 analysis types)
│   ├── weekly_activity_analysis.py     # Weekly elephant factor, churn ratio, effort Gini
│   ├── paper_figures.py                # Paper-ready figures
│   ├── recompute_burstiness.py         # Burstiness backfill from weekly_snapshots
│   └── build_repo_folders.py           # Per-repo folder + repo_results.md builder
├── src/
│   └── civic_tech_crawler/
│       ├── __init__.py             # Package version
│       ├── __main__.py             # python -m entry point
│       ├── cli.py                  # CLI argument parsing + orchestration
│       ├── cache.py                # Per-repo JSON cache (incremental runs)
│       ├── config.py               # YAML config loading + validation
│       ├── client.py               # GitHub API client (PyGithub + httpx)
│       ├── models.py               # All dataclass definitions
│       ├── collectors/
│       │   ├── repo_metrics.py     # Repository-level metrics
│       │   ├── person_metrics.py   # Per-contributor metrics
│       │   ├── temporal_metrics.py # PRs, tags, releases
│       │   ├── chaoss_metrics.py   # CHAOSS framework metrics
│       │   ├── commit_history.py   # Full commit history & contributor lifecycles
│       │   ├── issue_analytics.py  # Detailed issue analytics
│       │   └── detection.py        # Cloud/AI-ML detection
│       ├── exporters/
│       │   ├── csv_exporter.py     # CSV output (13 files)
│       │   └── json_exporter.py    # JSON output (full + per-repo)
│       └── utils/
│           ├── rate_limiter.py     # API rate limit monitoring
│           ├── retry.py            # 202 retry + backoff logic
│           └── osi_licenses.py     # OSI-approved SPDX license list
├── datasets/
│   └── 2026_05/                    # Canonical n=57 civic-tech corpus (version-controlled)
│       ├── README.md               # Manifest, selection rationale, methodology, file index
│       ├── *.csv                   # 14 crawl data CSVs
│       ├── <owner>_<repo>/         # One folder per repo (data.json, repo_results.md, plots)
│       ├── statistical_analysis/   # Statistical analysis CSVs
│       └── weekly_activity_analysis/ # Weekly analysis CSVs + summary.md
└── output/                         # Generated output (gitignored)
    ├── plots/                      # Generated visualizations
    └── statistical_analysis/       # Generated statistical analysis
```

---

## Citing This Tool and the Dataset

If you use this tool or the bundled dataset in academic research, please cite
both — the **tool** itself and the **2026-05 dataset** it produced. Machine-
readable metadata is in [`CITATION.cff`](CITATION.cff) (tool) and
[`datasets/2026_05/CITATION.cff`](datasets/2026_05/CITATION.cff) (dataset).

**Tool:**

```bibtex
@software{civic_tech_crawler,
  title  = {Civic Tech Git Crawler: GitHub Repository Metrics for Open Source Research},
  author = {Parkkila, Janne},
  year   = {2026},
  url    = {https://github.com/Japskua/civic-tech-git-crawler},
  note   = {Implements CHAOSS framework metrics for civic technology research}
}
```

**Dataset (n = 57, 2026-05):**

```bibtex
@dataset{civic_tech_corpus_2026_05,
  title     = {Civic-Tech Corpus — 2026-05 (n = 57)},
  author    = {Parkkila, Janne},
  year      = {2026},
  publisher = {Zenodo},
  version   = {2026.05},
  doi       = {10.5281/zenodo.20497015}
}
```

The dataset is archived on Zenodo:
[**doi.org/10.5281/zenodo.20497015**](https://doi.org/10.5281/zenodo.20497015).
The source files also live in this repository at
[`datasets/2026_05/`](datasets/2026_05/).

### Related frameworks and standards

- **CHAOSS Project**: https://chaoss.community/ -- The metrics framework implemented by this tool
- **GrimoireLab**: https://chaoss.github.io/grimoirelab/ -- Full-featured CHAOSS metrics platform
- **Augur**: https://github.com/chaoss/augur -- Python library for CHAOSS metrics

---

## License

- **Source code:** MIT — see [`LICENSE.txt`](LICENSE.txt).
- **Bundled dataset** (`datasets/2026_05/`): Creative Commons Attribution 4.0
  International (CC-BY-4.0) — see [`datasets/2026_05/LICENSE`](datasets/2026_05/LICENSE).

## Community

- Contributing: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Code of conduct: [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)
- Security policy: [`SECURITY.md`](SECURITY.md)
- Changelog: [`CHANGELOG.md`](CHANGELOG.md)
