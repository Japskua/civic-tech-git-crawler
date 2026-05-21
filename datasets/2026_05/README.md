# Civic-Tech Corpus — 2026-05 Refresh (n = 57)

This is the **canonical dataset** for the Civic Tech Git Crawler. It supersedes
all earlier exploratory and example runs (the previous `output/` and
`example_results/` snapshots, and every earlier working set, have been removed
from the repository). Everything downstream — analysis scripts, figures, and any
paper writeup — is generated against this folder.

| | |
|---|---|
| **Repositories** | 57 |
| **Organisations** | 24 |
| **Regions** | North America (US + Canada), Africa, Japan, Taiwan, Europe (Germany, UK, Sweden) |
| **Crawl tool** | `civic-tech-crawler` via `scripts/run_with_respawn.sh` |
| **Crawl config** | repository list in `config.yaml` / `config.example.yaml` |
| **Crawl date** | _populated after the crawl completes_ |
| **Summary stats** | _see "Dataset summary" below — populated after the crawl_ |

---

## What this corpus is

A curated, **internationally broad** set of open-source civic-technology
projects — software built with a public-interest *design intent*: civic
engagement, government services, public participation, transparency, open data,
or democratic process. The corpus deliberately spans a wide dynamic range on
project age, scale, contributor breadth, and language, and intentionally covers
several distinct civic-tech communities so that contributor dynamics can be
compared across regions and organisational cultures.

The selection criterion follows the working definition used throughout this
project: a project qualifies on the basis of its *design intent*, not whether its
only or primary use is civic. General-purpose tooling whose civic use is merely
downstream user behaviour is excluded.

This 2026-05 roster is the authoritative crawl set; it replaced an earlier
exploratory working set and shifts the corpus toward a much larger and more
internationally diverse sample (notably a substantial **German "Code for" / OK
Lab** cluster and the **Canadian CivicTechWR / Toronto** community).

---

## The 57 repositories

Grouped by community / region (same grouping as `config.yaml`):

### Canada — Toronto / Waterloo Region (9)
- `bikespace/bikespace`
- `bikespace/parking-map-data`
- `choruslabs/chorus`
- `civic-dashboard/civic-dashboard-web`
- `CivicTechWR/accessible-housing-portal`
- `CivicTechWR/connectedkw` *(fork)*
- `CivicTechWR/go-train-group-pass`
- `CivicTechWR/project-pech`
- `CivicTechWR/WRVotesPlaceholder`

### USA — Code for America / CiviForm (9)
- `civiform/civiform`
- `codeforamerica/asap_pdf`
- `codeforamerica/cmr-maryland-eligibility-determination`
- `codeforamerica/document-transfer-service`
- `codeforamerica/efiler-api`
- `codeforamerica/form-flow`
- `codeforamerica/pya`
- `codeforamerica/tax-benefits-backend`
- `codeforamerica/vita-min`

### Africa — Code for Africa (9)
- `CodeForAfrica/academy.AFRICA`
- `CodeForAfrica/actNOW`
- `CodeForAfrica/Dominion.AFRICA`
- `CodeForAfrica/GenderGap.AFRICA`
- `CodeForAfrica/openAFRICA`
- `CodeForAfrica/outbreak.AFRICA`
- `CodeForAfrica/PromiseTracker`
- `CodeForAfrica/sensors.AFRICA`
- `CodeForAfrica/ui`

### Japan — Code for Japan (2)
- `codeforjapan/BirdXplorer`
- `codeforjapan/decidim-cfj`

### Taiwan — g0v (1)
- `g0v/tw-rental-house-data`

### Germany — Code for / OK Lab network (18)
- `codeforbielefeld/baumbie`
- `codeforbielefeld/losdb`
- `codeformuenster/klimawatch`
- `codeforberlin/we-count`
- `openlegaldata/oldp`
- `oklabflensburg/open-emergency-map`
- `oklabflensburg/oddfl`
- `oklabflensburg/open-parcel-map`
- `oklabflensburg/open-biotope-map`
- `oklabflensburg/open-school-map`
- `oklabflensburg/open-data-api`
- `oklabflensburg/open-recycling-map`
- `oklabflensburg/open-trees-map`
- `oklabflensburg/open-monuments-map`
- `codeforcologne/Denkmal-4D-Koeln`
- `CodeforLeipzig/weihnachtsmarktkarte` *(fork)*
- `CodeforLeipzig/leipziggiesst` *(fork)*
- `code-for-magdeburg/StadtratWatch-web`

### Participation / deliberation platforms (2)
- `VoteIT/voteit_frontend`
- `digidemlab/decidim-census`

### Networked / decentralised civic infrastructure (4)
- `meshtastic/firmware`
- `meshtastic/Meshtastic-Android`
- `meshtastic/web`
- `iiab/iiab`

### Transparency / scoring / other (2)
- `mysociety/ceuk-marking`
- `ton-An/station_reach`

### NLP / open-knowledge (1, borderline)
- `fvialibre/heseia-sentence-bias-dataset`

> Section subtotals: 9 + 9 + 9 + 2 + 1 + 18 + 2 + 4 + 2 + 1 = **57**.

---

## Data-quality caveats

- **Forks (3).** `CivicTechWR/connectedkw`, `CodeforLeipzig/weihnachtsmarktkarte`,
  and `CodeforLeipzig/leipziggiesst` are forks; their commit history and
  contributor lists inherit upstream activity, so bus-factor, contributor counts,
  and commit totals may be inflated relative to the civic-tech work actually done
  in the fork. Treat per-repo metrics for these with care.
- **Placeholder / very small repos.** Several entries are early-stage or
  near-empty (e.g. `CivicTechWR/WRVotesPlaceholder`, `CivicTechWR/project-pech`,
  `VoteIT/voteit_frontend`, several single-digit-star OK Lab maps). Their metrics
  are valid but low-information; aggregate statistics should be reported with and
  without a minimum-activity threshold.
- **Borderline civic.** `fvialibre/heseia-sentence-bias-dataset` is an NLP
  sentence-bias dataset (AI-fairness research); it is retained as a borderline
  member. Analyses sensitive to domain coherence may treat it as a separate
  sub-cohort.
- **Scale outliers.** `meshtastic/firmware` (~7.6k★), `iiab/iiab` (~1.9k★), and
  `meshtastic/Meshtastic-Android` (~1.6k★) dominate scale-sensitive aggregates;
  consider normalising or reporting medians.

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
- exits only once all 57 per-repo caches exist **and** `full_results.json` has been
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
| `full_results.json` | Complete nested data for all 57 repos |
| `<owner>_<repo>_data.json` | Per-repo cache (one per repository) |

The three **bold** files are the weekly-activity outputs verified present for this run.

### Generated after the crawl (analysis pass)

- `statistical_analysis/` — outputs of `scripts/statistical_analysis.py`
- `figures/` — outputs of `scripts/paper_figures.py`
- `weekly_activity_analysis/` — outputs of `scripts/weekly_activity_analysis.py`
- `<owner>_<repo>/repo_results.md` — per-repo folders from `scripts/build_repo_folders.py`
- `analysis_n57.md` — academic-style writeup of findings, methodology, threats to validity

---

## Reproducing this dataset

```bash
# From the repo root, with a GitHub token available:
export GITHUB_TOKEN=$(gh auth token)

# Full crawl with auto-respawn (resumable; output -> datasets/2026_05/)
scripts/run_with_respawn.sh config.yaml datasets/2026_05 57

# Then the analysis pass (see scripts/ and the "Generated after the crawl" list)
```

---

## Dataset summary

_This section is populated after the crawl + analysis pass completes (repo counts,
contributor counts, commit totals, date range, etc.)._
