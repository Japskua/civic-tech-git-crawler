# Implementation Plan: Recommended Metrics

> **Status: ALL COMPLETE** — All 10 recommended metrics (29+ fields) implemented, tested, and merged to `master` across three PRs.
>
> - **PR #1** (`improve_by_recommendations`): 7 metrics, 15 fields — ✅ Merged
> - **PR #2** (`add_future_metrics`): 4 metrics, 8 fields — ✅ Merged
> - **PR #3** (`add_core_periphery`): 1 metric, 6 fields + new dataclass + new CSV — ✅ Merged

## Phase 1: Core Metrics (PR #1)

Technical plan for adding 7 metrics (15 new fields) to the Civic Tech Git Crawler.

---

## Architecture Decision

**All new fields are added to the existing `ChaossMetrics` dataclass** with default values. This avoids creating new dataclasses, new collectors, or changes to `RepositoryData`, `cli.py`, or the JSON exporter. The established pattern of `try/except GithubException` with graceful `None` fallbacks is followed throughout.

---

## New Fields (added to `ChaossMetrics` in `models.py`)

```python
# Elephant Factor (org-level bus factor)
elephant_factor: int | None = None

# Contributor Retention Cohorts
contributor_new_count: int = 0       # 1 active week
contributor_casual_count: int = 0    # 2-12 active weeks
contributor_regular_count: int = 0   # 13+ active weeks

# Time to First Response
median_time_to_first_response_issues_hours: float | None = None
median_time_to_first_response_prs_hours: float | None = None
time_to_first_response_issues_sample_size: int = 0
time_to_first_response_prs_sample_size: int = 0

# Documentation Freshness
readme_last_updated: datetime | None = None
contributing_last_updated: datetime | None = None

# Stale Issue Ratio
stale_issue_ratio: float | None = None
stale_issue_count: int = 0
open_issue_count: int = 0

# PR Review Depth & Turnaround
median_pr_review_turnaround_hours: float | None = None
avg_review_comments_per_pr: float | None = None
```

---

## Implementation Details

### 1. Elephant Factor

**API cost:** 0 additional calls (piggybacks on existing org_diversity loop)

Modify the org_diversity section (lines 104-110 of `chaoss_metrics.py`) to also build `org_commits: dict[str, int]`:

```python
org_diversity: dict[str, int] = {}
org_commits: dict[str, int] = {}
for p in person_metrics:
    if p.login:
        user_info = client.get_user_info(p.login)
        company = user_info.get("company") or "Unknown"
        company = company.strip().lstrip("@")
        org_diversity[company] = org_diversity.get(company, 0) + 1
        org_commits[company] = org_commits.get(company, 0) + p.num_commits
```

New helper `_compute_elephant_factor(org_commits)` applies the same algorithm as `_compute_bus_factor()` but over organizations instead of individuals.

### 2. Contributor Retention Cohorts

**API cost:** ~1 call (stats/contributors likely cached server-side from person_metrics collection)

```python
stats = client.get_stats_contributors(repo)
for contributor in stats:
    active_weeks = sum(1 for w in contributor.weeks if w.c > 0)
    if active_weeks <= 1:     new_count += 1
    elif active_weeks <= 12:  casual_count += 1
    else:                     regular_count += 1
```

### 3. Time to First Response

**API cost:** ~200 calls per repo (100 issues + 100 PRs, each with 1 comment fetch)

New helper `_compute_median_first_response(repo, item_type, sample_size=100)`:
- Fetch last 100 items (`sort="created", direction="desc"`)
- For issues: skip items where `issue.pull_request is not None`
- For each item: `item.get_comments()`, find first comment where `comment.user.login != author_login`
- Compute delta in hours, return median

### 4. Documentation Freshness

**API cost:** 2 calls per repo

New client method `get_last_commit_date_for_path(slug, path)`:
```
GET /repos/{slug}/commits?path={path}&per_page=1
```
Returns the commit author date of the most recent commit touching that path.

### 5. Stale Issue Ratio

**API cost:** ~1-10 calls per repo (paginated at 100/page)

```python
open_issues = repo.get_issues(state="open")
for issue in open_issues:
    if issue.pull_request is not None: continue  # skip PRs
    open_issue_count += 1
    if issue.updated_at < (now - 90 days):
        stale_issue_count += 1
    if open_issue_count >= 1000: break  # safety cap
stale_issue_ratio = stale_issue_count / open_issue_count
```

### 6. PR Review Depth & Turnaround

**API cost:** ~100 calls per repo (1 per merged PR)

New helper `_compute_pr_review_metrics(repo, sample_size=100)`:
- Fetch last 100 closed PRs, filter to merged only
- For each: `pr.get_reviews()`, find earliest `submitted_at`
- Turnaround = `first_review.submitted_at - pr.created_at` (in hours)
- Depth = count of reviews with non-empty body
- Return (median turnaround, average depth)

---

## Cache Backward Compatibility

In `cache.py`, `_dict_to_chaoss_metrics()` uses `.get()` with defaults for all 15 new fields:

```python
elephant_factor=d.get("elephant_factor"),
contributor_new_count=d.get("contributor_new_count", 0),
# ... etc.
```

Old cache files (without new fields) will load with `None`/`0` defaults. Users who want new metrics for previously-crawled repos can run `--force`.

---

## Estimated API Budget Impact

| Metric | Extra API calls/repo | Notes |
|--------|---------------------|-------|
| Elephant Factor | 0 | Reuses existing data |
| Contributor Retention | ~1 | Server-side cached |
| Time to First Response (issues) | ~101 | 100 issues + comments |
| Time to First Response (PRs) | ~101 | 100 PRs + comments |
| Documentation Freshness | 2 | 2 commit lookups |
| Stale Issue Ratio | ~1-10 | Paginated open issues |
| PR Review Depth | ~101 | 100 PRs + reviews |
| **Total per repo** | **~310** | Within 5000/hr budget |

For 3 repos: ~930 additional calls. For 10 repos: ~3100 additional calls. Both fit within the 5000/hour rate limit.

---

## Phase 1 Files Modified

1. `src/civic_tech_crawler/models.py` -- 15 new fields on ChaossMetrics
2. `src/civic_tech_crawler/collectors/chaoss_metrics.py` -- 4 new helpers + 6 new sections
3. `src/civic_tech_crawler/client.py` -- 1 new method
4. `src/civic_tech_crawler/cache.py` -- 15 new `.get()` calls
5. `src/civic_tech_crawler/exporters/csv_exporter.py` -- 15 new CSV headers
6. `README.md` -- New metrics documentation

---

## Phase 2: Future Metrics (PR #2)

Added 4 additional metrics originally listed as "Future Work":

### 1. Herfindahl-Hirschman Index (HHI)

**API cost:** 0 additional calls (piggybacks on existing org diversity data)

Computes organizational commit concentration using the standard HHI formula: sum of squared market shares (commit percentages). Scale 0–10,000, where 10,000 = single-org monopoly.

### 2. Institutional Type Classification

**API cost:** 0 additional calls (reuses existing org diversity company field)

Pattern-matching on GitHub profile `company` field to classify contributors into: government, academic, nonprofit, company, or unknown. Uses keyword matching (e.g., ".gov", "university", "foundation").

### 3. Cross-Project Contributor Overlap

**API cost:** 0 additional calls (post-crawl analysis of person_metrics)

Identifies contributors active in multiple crawled repositories. Outputs to `cross_project_overlap.csv`. New `CrossProjectOverlap` dataclass in `models.py`.

### 4. DORA Metrics

**API cost:** 0 additional calls (computed from existing temporal metrics)

- **Deployment Frequency**: releases per month over repo lifetime
- **Median Lead Time**: median days between consecutive releases
- **Change Failure Rate**: ratio of revert/hotfix/bugfix PRs (detected by title pattern matching) to total merged PRs

### Phase 2 Files Modified

1. `src/civic_tech_crawler/models.py` -- 8 new fields on ChaossMetrics + `CrossProjectOverlap` dataclass
2. `src/civic_tech_crawler/collectors/chaoss_metrics.py` -- 4 new computation sections
3. `src/civic_tech_crawler/cli.py` -- Cross-project overlap computation + console summary
4. `src/civic_tech_crawler/cache.py` -- 8 new `.get()` calls
5. `src/civic_tech_crawler/exporters/csv_exporter.py` -- 8 new CSV headers + `cross_project_overlap.csv`
6. `README.md` -- New metrics documentation

---

## Phase 3: Core-Periphery Network Analysis (PR #3)

Added the final high-effort metric: Core-Periphery Network Analysis using NetworkX.

### Implementation

**API cost:** 0 additional calls (edges captured from existing `_compute_pr_review_metrics()` loop)

Builds an undirected collaboration graph where nodes = contributors and edges = PR author↔reviewer pairs (weighted by interaction count). Uses NetworkX for:
- `degree_centrality()` — normalized count of unique collaborators
- `betweenness_centrality()` — bridge position in the network
- `density()` — graph connectedness

**Classification:** Contributors with degree centrality above the median = "core", rest = "periphery". Strict `>` threshold means uniform graphs correctly classify all as periphery.

### New Data Structures

- `CorePeripheryContributor` dataclass (per-contributor network metrics)
- 6 new fields on `ChaossMetrics` (summary stats + cached edges)
- `core_periphery_contributors` field on `RepositoryData`
- New `core_periphery.csv` output file

### Phase 3 Files Modified

1. `pyproject.toml` -- Added `networkx>=3.0` dependency
2. `src/civic_tech_crawler/models.py` -- `CorePeripheryContributor` dataclass + 6 new ChaossMetrics fields + RepositoryData field
3. `src/civic_tech_crawler/collectors/chaoss_metrics.py` -- Modified `_compute_pr_review_metrics()` return + new `_compute_core_periphery()` + changed `collect_chaoss_metrics()` return type
4. `src/civic_tech_crawler/cli.py` -- Unpack tuple return + console summary
5. `src/civic_tech_crawler/cache.py` -- 6 new `.get()` calls + `CorePeripheryContributor` deserialization
6. `src/civic_tech_crawler/exporters/csv_exporter.py` -- 5 new chaoss_summary columns + `core_periphery.csv` export
7. `README.md` -- New metrics documentation

---

---

## Data Quality Fix: Anonymous Contributor Fallback

Fixes `num_developers=0` and empty `person_metrics` for repos where all commit authors use emails not linked to GitHub accounts (e.g., `codeforamerica/iac-transit-baseapp`).

### Root Cause

GitHub's `/contributors` and `/stats/contributors` endpoints only return contributors linked to GitHub user accounts. Commits made with unlinked emails (e.g., `user@MacBook.local`) produce `author: null` and are invisible to both endpoints.

### Fix

| File | Change |
|------|--------|
| `repo_metrics.py` | Added `anon=true` fallback: retries with `repo.get_contributors(anon="true")` when count is 0 but commits exist (1 extra API call, edge case only) |
| `person_metrics.py` | Added `_fallback_person_metrics()`: iterates commits (capped at 500), groups by author email to build `PersonMetrics` records |
| `cli.py` | Passes `repo_metrics` to `collect_person_metrics()` so fallback can check `total_commits` |

---

## All Files Modified (Cumulative)

| File | PR #1 | PR #2 | PR #3 | Post-merge |
|------|-------|-------|-------|------------|
| `pyproject.toml` | | | ✅ networkx | |
| `models.py` | 15 fields | 8 fields + CrossProjectOverlap | 6 fields + CorePeripheryContributor | |
| `chaoss_metrics.py` | 4 helpers + 6 sections | 4 sections | Modified return types + core-periphery | |
| `client.py` | 1 new method | | | |
| `cache.py` | 15 `.get()` calls | 8 `.get()` calls | 6 `.get()` calls + CorePeripheryContributor | |
| `csv_exporter.py` | 15 headers | 8 headers + overlap CSV | 5 headers + core_periphery CSV | |
| `cli.py` | | Overlap computation | Tuple unpack + summary | Pass repo_metrics to person_metrics |
| `repo_metrics.py` | | | | anon=true fallback |
| `person_metrics.py` | | | | Commit-based fallback |
| `README.md` | ✅ | ✅ | ✅ | ✅ |
