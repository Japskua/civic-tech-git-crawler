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
- [Metrics Reference](#metrics-reference)
  - [Repository Metrics](#repository-metrics)
  - [Contributor Metrics](#contributor-metrics)
  - [Temporal Metrics](#temporal-metrics)
  - [CHAOSS Metrics](#chaoss-metrics)
  - [Technology Detection](#technology-detection)
- [Analysis Pipeline](#analysis-pipeline)
- [API Rate Limits](#api-rate-limits)
- [Examples](#examples)
- [Extending the Tool](#extending-the-tool)
- [Citing This Tool](#citing-this-tool)
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

# 4. Run against the example repositories
uv run civic-tech-crawler --config config.example.yaml

# 5. Find results in ./output/
ls output/
```

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
| [PyYAML](https://pyyaml.org/) | YAML configuration file parsing |
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

# Repositories to crawl (owner/repo format)
repositories:
  - "DemocracyClub/UK-Polling-Stations"
  - "DemocracyClub/WhoCanIVoteFor"
  - "fvialibre/edia"

# Output settings
output:
  directory: "./output"     # Where to write CSV and JSON files

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
                          [--skip-temporal] [--skip-detection] [--verbose]

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
  --verbose                Enable debug logging
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
| `--verbose` | Shows detailed debug output including every HTTP request and response. |

### Running with `python -m`

```bash
uv run python -m civic_tech_crawler --config config.yaml
```

---

## Output Files

All output files are written to the output directory (default: `./output/`). Both CSV and JSON formats are produced automatically.

### CSV files

| File | Rows | Description |
|------|------|-------------|
| `repo_metrics.csv` | 1 per repository | Repository-level metrics (stars, forks, languages, license, CI/CD, etc.) |
| `person_metrics.csv` | 1 per repository-contributor pair | Contributor commit counts, code additions/deletions, averages |
| `temporal_summary.csv` | 1 per repository | PR counts (total, merged, open, closed), tag and release counts |
| `chaoss_summary.csv` | 1 per repository | CHAOSS framework metrics (bus factor, burstiness, acceptance ratio, etc.) |
| `pull_requests.csv` | 1 per pull request | Individual PR records with timestamps and authors |
| `tags.csv` | 1 per tag | Git tags with commit SHAs and dates |

### JSON files

| File | Description |
|------|-------------|
| `full_results.json` | Complete nested data for all repositories in a single file |
| `{Owner}_{Repo}_data.json` | Individual deep-dive file per repository |

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
    }
  }
]
```

---

## Metrics Reference

### Repository Metrics

These are collected for each repository and exported to `repo_metrics.csv`.

| Metric | Column | Type | Description |
|--------|--------|------|-------------|
| Repository name | `full_name` | string | Full `owner/repo` identifier |
| Description | `description` | string | Repository description |
| Developers | `num_developers` | integer | Total number of unique contributors |
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
| Updated | `updated_at` | datetime | Last update date |
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
| Commits | `num_commits` | integer | Total commits by this contributor |
| Additions | `additions` | integer | Total lines of code added |
| Deletions | `deletions` | integer | Total lines of code deleted |
| Avg additions/commit | `avg_additions_per_commit` | float | Mean lines added per commit |
| Avg deletions/commit | `avg_deletions_per_commit` | float | Mean lines deleted per commit |

**Data source:** The GitHub [Repository Statistics API](https://docs.github.com/en/rest/metrics/statistics#get-all-contributor-commit-activity) (`/repos/{owner}/{repo}/stats/contributors`), which returns weekly breakdowns of commits, additions, and deletions per contributor. The tool aggregates all weeks to produce totals and averages.

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
                    |  +-----------------------------+   |
                    |                                    |
                    +------------------+-----------------+
                                       |
                          +------------v-------------+
                          |    EXPORT RESULTS        |
                          |    - 6 CSV files         |
                          |    - Full JSON + per-repo|
                          +--------------------------+
```

### Pipeline characteristics

- **Error isolation:** If one repository fails, the tool continues with the remaining repositories. Failed repositories are logged and excluded from the output.
- **Progress reporting:** A Rich progress bar shows current repository and collection step in the terminal.
- **Collector dependencies:** CHAOSS metrics depend on data from person metrics and temporal metrics. If temporal metrics are skipped (`--skip-temporal`), dependent CHAOSS metrics (acceptance ratio, release frequency) will be `null`.
- **User info caching:** Contributor profile lookups are cached in memory. If the same person contributes to multiple repositories, their profile is fetched only once.

### Retry mechanism

GitHub's statistics endpoints (`/stats/contributors`, `/stats/commit_activity`) are computed asynchronously. The API returns HTTP 202 while computing, which means the data is not yet ready. The tool handles this with:

- **Linear backoff**: Waits 3s, 6s, 9s, 12s, 15s between attempts
- **Maximum 5 retries** (configurable via `github.max_retries`)
- **Graceful degradation**: If stats are unavailable after all retries, the affected metrics are recorded as `null` rather than failing the entire repository

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
| **Total per repository** | **~25-150** |

### Planning your runs

| Repositories | Estimated API Calls | Time (approx.) |
|-------------|--------------------|----|
| 3 | 75-450 | 1-5 minutes |
| 10 | 250-1,500 | 5-15 minutes |
| 50 | 1,250-7,500 | 20-60 minutes |
| 100+ | 2,500+ | Consider multiple runs |

The tool monitors remaining API calls and automatically sleeps when the rate limit is nearly exhausted, resuming when the limit resets (every hour).

### Reducing API usage

Use skip flags to disable expensive collectors:

```bash
# Fastest: only repo-level metrics and person metrics
uv run civic-tech-crawler --skip-temporal --skip-chaoss --skip-detection

# Skip only CHAOSS (which depends on temporal data anyway)
uv run civic-tech-crawler --skip-chaoss
```

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

### Example 4: Debug mode

```bash
uv run civic-tech-crawler --config config.yaml --verbose 2>&1 | tee crawl.log
```

### Example 5: Loading results in Python for analysis

```python
import pandas as pd

# Load repository-level metrics
repos = pd.read_csv("output/repo_metrics.csv")
print(repos[["full_name", "stars", "forks", "num_developers", "total_commits"]])

# Load contributor metrics
contributors = pd.read_csv("output/person_metrics.csv")
top = contributors.sort_values("num_commits", ascending=False).head(10)
print(top[["repo_full_name", "login", "num_commits", "additions", "deletions"]])

# Load CHAOSS metrics
chaoss = pd.read_csv("output/chaoss_summary.csv")
print(chaoss[["repo_full_name", "bus_factor", "burstiness_cv", "change_request_acceptance_ratio"]])
```

### Example 6: Loading results in R

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

### Example 7: Full nested JSON analysis

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
├── src/
│   └── civic_tech_crawler/
│       ├── __init__.py             # Package version
│       ├── __main__.py             # python -m entry point
│       ├── cli.py                  # CLI argument parsing + orchestration
│       ├── config.py               # YAML config loading + validation
│       ├── client.py               # GitHub API client (PyGithub + httpx)
│       ├── models.py               # All dataclass definitions
│       ├── collectors/
│       │   ├── repo_metrics.py     # Repository-level metrics
│       │   ├── person_metrics.py   # Per-contributor metrics
│       │   ├── temporal_metrics.py # PRs, tags, releases
│       │   ├── chaoss_metrics.py   # CHAOSS framework metrics
│       │   └── detection.py        # Cloud/AI-ML detection
│       ├── exporters/
│       │   ├── csv_exporter.py     # CSV output (6 files)
│       │   └── json_exporter.py    # JSON output (full + per-repo)
│       └── utils/
│           ├── rate_limiter.py     # API rate limit monitoring
│           ├── retry.py            # 202 retry + backoff logic
│           └── osi_licenses.py     # OSI-approved SPDX license list
└── output/                         # Generated output (gitignored)
```

---

## Citing This Tool

If you use this tool in academic research, please cite it as:

```bibtex
@software{civic_tech_crawler,
  title = {Civic Tech Git Crawler: GitHub Repository Metrics for Open Source Research},
  author = {Parkkila, Janne},
  year = {2026},
  url = {https://github.com/your-username/civic_tech_git_crawler},
  note = {Implements CHAOSS framework metrics for civic technology research}
}
```

### Related frameworks and standards

- **CHAOSS Project**: https://chaoss.community/ -- The metrics framework implemented by this tool
- **GrimoireLab**: https://chaoss.github.io/grimoirelab/ -- Full-featured CHAOSS metrics platform
- **Augur**: https://github.com/chaoss/augur -- Python library for CHAOSS metrics

---

## License

This project is open source. See the LICENSE file for details.
