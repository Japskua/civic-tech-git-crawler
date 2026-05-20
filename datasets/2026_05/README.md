# Civic-Tech Corpus — 2026-05 Refresh (n = 38)

This is the **canonical dataset** for the Civic Tech Git Crawler. It supersedes
all earlier exploratory and example runs (the previous `output/` and
`example_results/` snapshots, and the `n=37` May 2026 dataset, have been removed
from the repository). Everything downstream — analysis scripts, figures, and any
paper writeup — is generated against this folder.

| | |
|---|---|
| **Repositories** | 38 |
| **Selection** | 33 retained from the prior `n=37` set, − 4 removed, + 5 added |
| **Crawl tool** | `civic-tech-crawler` via `scripts/run_with_respawn.sh` |
| **Crawl config** | repository list in `config.yaml` / `config.example.yaml` |
| **Crawl date** | _populated after the crawl completes_ |
| **Summary stats** | _see "Dataset summary" below — populated after the crawl_ |

---

## What this corpus is

A curated set of **open-source civic-technology projects** — software built with a
public-interest *design intent*: civic engagement, government services, public
participation, transparency, or democratic process. The corpus deliberately spans
a wide dynamic range on project age, scale, contributor breadth, and language so
that contributor-dynamics and project-health metrics can be studied across very
different kinds of civic-tech projects.

The selection criterion follows the working definition used throughout this
project: a project qualifies on the basis of its *design intent*, not whether its
only or primary use is civic. General-purpose tooling whose civic use is merely
downstream user behaviour is excluded.

---

## Changes vs. the prior n=37 set

### ➖ Removed (4) — tiny / archived / inactive

| Repository | Reason |
|------------|--------|
| `codeforamerica/recordtrac` | Archived; last commit 2021 |
| `markov-root/atlas` | Very small (2 devs, ~48 commits) |
| `fvialibre/edia` | Inactive; last commit 2023 |
| `luftdata/luftdata.se` | Tiny/inactive; last commit 2025-04 |

### ➕ Added (5)

| Repository | Civic-tech fit | Description |
|------------|----------------|-------------|
| `codeforjapan/decidim-cfj` | Strong | Decidim participatory-democracy platform (Code for Japan deployment) |
| `compdemocracy/polis` | Strong | Polis — large-scale deliberation / collective-input tool |
| `g0v/tw-rental-house-data` | Solid | Taiwan rental-housing market transparency / open data |
| `g0v/moedict.tw` | Borderline | Ministry of Education dictionary — open-knowledge / digital humanities |
| `g0v/amis-moedict` | Borderline | Amis indigenous-language dictionary — language preservation |

**On the two borderline g0v dictionaries.** `moedict.tw` and `amis-moedict` come
from g0v, a civic-tech *community*, but a dictionary is open-knowledge / language
preservation rather than civic engagement, government services, or democratic
process in the strict sense. They are included by explicit decision to widen the
corpus toward the g0v open-knowledge tradition; readers running domain-restricted
analyses may wish to treat them as a separate sub-cohort. (One existing member,
`fvialibre/heseia-sentence-bias-dataset`, is similarly borderline — an NLP
sentence-bias dataset — and is retained for the same reason.)

---

## The 38 repositories

Grouped by organisation / role (same grouping as `config.yaml`):

### DemocracyClub — UK elections (2)
- `DemocracyClub/UK-Polling-Stations`
- `DemocracyClub/WhoCanIVoteFor`

### Code for Africa (9)
- `CodeForAfrica/PromiseTracker`
- `CodeForAfrica/academy.AFRICA`
- `CodeForAfrica/Dominion.AFRICA`
- `CodeForAfrica/GenderGap.AFRICA`
- `CodeForAfrica/openAFRICA`
- `CodeForAfrica/outbreak.AFRICA`
- `CodeForAfrica/ui`
- `CodeForAfrica/sensors.AFRICA`
- `CodeForAfrica/actNOW`

### Code for America (9)
- `codeforamerica/form-flow`
- `codeforamerica/vita-min`
- `codeforamerica/tofu-modules-aws-serverless-database`
- `codeforamerica/tax-benefits-backend`
- `codeforamerica/pya`
- `codeforamerica/honeycrisp-gem`
- `codeforamerica/asap_pdf`
- `codeforamerica/cmr-maryland-eligibility-determination`
- `codeforamerica/document-transfer-service`

### Code for Japan (2)
- `codeforjapan/BirdXplorer`
- `codeforjapan/decidim-cfj` ⬅ *added 2026-05*

### g0v — Taiwan (3, all added 2026-05)
- `g0v/moedict.tw` ⬅
- `g0v/amis-moedict` ⬅
- `g0v/tw-rental-house-data` ⬅

### Deliberation / participation platforms (3)
- `CitizensFoundation/your-priorities-app`
- `compdemocracy/polis` ⬅ *added 2026-05*
- `ForumMagnum/ForumMagnum`

### Transparency / FOI / civic services (4)
- `okfde/froide`
- `mysociety/ceuk-marking`
- `openplans/shareabouts`
- `civiform/civiform`

### Networked / decentralised civic infrastructure (5)
- `mastodon/mastodon`
- `meshtastic/firmware`
- `meshtastic/Meshtastic-Android`
- `meshtastic/web`
- `iiab/iiab`

### NLP / open-knowledge (1, borderline)
- `fvialibre/heseia-sentence-bias-dataset`

---

## How the data was collected

The crawler (`src/civic_tech_crawler/`) collects, per repository:

1. **Repository metrics** — languages, license (SPDX + OSI status), topics,
   community-health files, stars/forks/watchers, CI/CD, cloud & AI/ML detection.
2. **Person metrics** — per-(repo, contributor) commits, with a heuristic `is_bot`
   flag.
3. **Temporal metrics** — PR and tag/release counts and cadence.
4. **Full commit history** — *weekly project snapshots*, *per-contributor weekly
   activity* (commits + lines added/removed via GraphQL), and *contributor
   lifecycles* (first/last commit, active vs. departed). This is the weekly-commit
   data added in the recent crawler updates; see the file list below.
5. **CHAOSS metrics** — 45+ columns including bus factor, elephant factor, HHI
   concentration, and burstiness (with a `weekly_snapshots` fallback when GitHub's
   stats endpoints time out).
6. **Issue analytics** — per-issue records (capped at 5,000/repo) and aggregates.

### Fault tolerance

The crawl is run through `scripts/run_with_respawn.sh`, which:

- writes a per-repo JSON cache so a relaunch **skips already-completed repos**
  (idempotent, resumable);
- **auto-respawns** if the crawler is SIGKILLed (e.g. sandbox OOM, exit 137) or
  exits non-zero, sleeping 10 s between attempts;
- exits only once all 38 per-repo caches exist **and** `full_results.json` has been
  written.

Inside the crawler, `retry_on_none` handles GitHub's HTTP 202 "computing"
responses on stats endpoints, and `retry_with_backoff` handles 403/429/5xx with
exponential backoff.

---

## Output files

### Dataset-level (one row per repo unless noted)

| File | Notes |
|------|-------|
| `repo_metrics.csv` | Repository-level metrics |
| `person_metrics.csv` | Per-(repo, contributor); includes `is_bot` |
| `temporal_summary.csv` | PR / tag / release counts |
| `chaoss_summary.csv` | 45+ CHAOSS columns incl. `burstiness_cv` |
| `pull_requests.csv` | Individual PR records |
| `tags.csv` | Git tags |
| `core_periphery.csv` | Per-contributor network role |
| **`weekly_snapshots.csv`** | Weekly commit/contributor snapshots |
| **`contributor_weekly_activity.csv`** | Per-(contributor, ISO-week) commits + lines added/removed |
| **`contributor_lifecycles.csv`** | Per-contributor first/last commit, active/departed |
| `issue_records.csv` | Individual issue records (≤5,000/repo) |
| `issue_summary.csv` | Aggregated issue analytics |
| `cross_project_overlap.csv` | Contributors active in multiple crawled repos |
| `full_results.json` | Complete nested data for all 38 repos |
| `<owner>_<repo>_data.json` | Per-repo cache (one per repository) |

The three **bold** files are the weekly-activity outputs verified present for this run.

### Generated after the crawl (analysis pass)

- `statistical_analysis/` — outputs of `scripts/statistical_analysis.py`
- `figures/` — outputs of `scripts/paper_figures.py`
- `weekly_activity_analysis/` — outputs of `scripts/weekly_activity_analysis.py`
- `<owner>_<repo>/repo_results.md` — per-repo folders from `scripts/build_repo_folders.py`
- `analysis_n38.md` — academic-style writeup of findings, methodology, threats to validity

---

## Reproducing this dataset

```bash
# From the repo root, with a GitHub token available:
export GITHUB_TOKEN=$(gh auth token)

# Full crawl with auto-respawn (resumable; output -> datasets/2026_05/)
scripts/run_with_respawn.sh config.yaml datasets/2026_05 38

# Then the analysis pass (see scripts/ and the "Generated after the crawl" list)
```

---

## Dataset summary

_This section is populated after the crawl + analysis pass completes (repo counts,
contributor counts, commit totals, date range, etc.)._
