# Civic-Tech Corpus — 2026-06 Refresh (n = 55)

This is the **2026-06 snapshot** of the Civic Tech Git Crawler corpus. It re-crawls
the 2026-05 roster — minus `bikespace/parking-map-data` and `fvialibre/heseia-sentence-bias-dataset`, which were dropped (n = 55) — and adds a new
data layer: **AI-usage detection** — distinguishing whether (and how) AI/LLMs are
involved in each project. Everything downstream — analysis scripts, figures, and
any writeup — is generated against this folder.

| | |
|---|---|
| **Repositories** | 55 |
| **Organisations** | 24 |
| **Regions** | North America (US + Canada), Africa, Japan, Taiwan, Europe (Germany, UK, Sweden) |
| **Crawl tool** | `civic-tech-crawler` via `scripts/run_with_respawn.sh` |
| **Crawl config** | repository list in `config.yaml` / `config.example.yaml` |
| **Crawl date** | 2026-06-03 → 2026-06-04 (single logical run; per-repo cache, resumable) |
| **New in this refresh** | AI-usage detection (`ai_usage.csv`, `ai_signals.csv`, `ai_usage_analysis/`); traditional-ML detection narrowed to classical ML (LLM SDKs moved to the product-LLM group) |
| **Version** | 2026.06 |
| **License** | CC-BY-4.0 (see [`../2026_05/LICENSE`](../2026_05/LICENSE)) |
| **Maintainer** | Janne Parkkila — japskua@gmail.com |
| **Summary stats** | see "Dataset summary" below |

---

## What this corpus is

A curated, **internationally broad** set of open-source civic-technology
projects — software built with a public-interest *design intent*: civic
engagement, government services, public participation, transparency, open data,
or democratic process. The corpus deliberately spans a wide dynamic range on
project age, scale, contributor breadth, and language, and intentionally covers
several distinct civic-tech communities so that contributor dynamics can be
compared across regions and organisational cultures.

A project qualifies on the basis of its *design intent*, not whether its only or
primary use is civic. General-purpose tooling whose civic use is merely
downstream user behaviour is excluded. The roster is identical to the 2026-05
refresh (notably a substantial **German "Code for" / OK Lab** cluster and the
**Canadian CivicTechWR / Toronto** community), enabling month-over-month
comparison.

---

## The 55 repositories

Grouped by community / region (same grouping as `config.yaml`):

### Canada — Toronto / Waterloo Region (8)
- `bikespace/bikespace`
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

> Section subtotals: 8 + 9 + 9 + 2 + 1 + 18 + 2 + 4 + 2 = **55**.

---

## Data-quality caveats

- **Forks (3).** `CivicTechWR/connectedkw`, `CodeforLeipzig/weihnachtsmarktkarte`,
  and `CodeforLeipzig/leipziggiesst` inherit upstream commit/contributor history,
  so concentration and AI-usage signals may belong to the parent project, not the
  fork. (e.g. `connectedkw`'s product-LLM `openai` signal is likely inherited.)
- **Placeholder / very small repos.** Several entries are early-stage or
  near-empty; their metrics are valid but low-information.
- **Scale outliers.** `meshtastic/firmware` (~7.6k★), `iiab/iiab` (~1.9k★), and
  `meshtastic/Meshtastic-Android` (~1.6k★) dominate scale-sensitive aggregates.
- **⚠️ AI-usage detection is a lower bound.** The `dev_*` and `product_*` signals
  capture only AI involvement that leaves a **durable, disclosed, or automated
  trace** — agent config files, commit co-author trailers, AI-bot commits/PRs, CI
  agents, and LLM dependencies. AI assistance that leaves no artifact (inline
  autocomplete, code pasted from a chat UI) is undetectable from repository
  metadata. **Treat AI-adoption counts as a floor, not a true rate.** Evidence
  strength varies by `source` (config files / commit trailers / bot PRs = strong;
  CI refs and dependencies = medium; topics = weak) — see `ai_signals.csv`.

---

## How the data was collected

The crawler (`src/civic_tech_crawler/`) collects, per repository:

1. **Repository metrics** — languages, license (SPDX + OSI), topics,
   community-health files, stars/forks/watchers, CI/CD, cloud & traditional-ML
   detection.
2. **Person metrics** — per-(repo, contributor) commits, with a heuristic `is_bot`
   flag.
3. **Temporal metrics** — PR and tag/release counts and cadence.
4. **Full commit history** — weekly project snapshots, per-contributor weekly
   activity (commits + lines via GraphQL), and contributor lifecycles.
5. **CHAOSS metrics** — 45+ columns incl. bus factor, elephant factor, HHI, and
   burstiness (with a `weekly_snapshots` fallback when GitHub's stats endpoints
   time out).
6. **Issue analytics** — per-issue records (capped at 5,000/repo) and aggregates.
7. **AI-usage detection (new)** — two distinct, separately-reported groups:
   - **AI-assisted development** (`dev_*`) — agent config files (`CLAUDE.md`,
     `AGENTS.md`, `.cursorrules`, …), commit co-author trailers
     (`Co-authored-by: Claude`, etc.), AI agent-bot commits/PRs
     (`copilot-swe-agent[bot]`, `devin-ai-integration[bot]`, …), CI agents, and
     review bots. First-appearance is dated per signal.
   - **Product LLM** (`product_*`) — the project *ships* LLM/GenAI functionality
     (LLM SDK dependencies like `openai`/`anthropic`/`langchain`, GenAI topics).
   Vocabulary is config-driven (`detection.ai_dev_keywords` /
   `product_llm_keywords`; defaults in `src/civic_tech_crawler/utils/ai_detection.py`).
   Commit scanning piggybacks the existing commit-history walk (zero extra API
   calls); the PR body / review-bot scan covers the ≤200 most-recent PRs.

   > **Change from 2026-05:** `ai_ml_detected` now covers **classical ML only**
   > (TensorFlow, PyTorch, scikit-learn, Jupyter, …). LLM SDKs that were
   > previously counted there (`openai`, `langchain`) moved to the product-LLM
   > group, which is why this refresh reports **4** traditional-ML repos vs 6 in
   > 2026-05 — a reclassification, not a change in the underlying projects.

### Fault tolerance

The crawl runs through `scripts/run_with_respawn.sh`, which writes a per-repo JSON
cache (resumable; relaunches skip completed repos), **auto-respawns** on SIGKILL /
non-zero exit, and exits only once all 55 caches **and** `full_results.json` exist.
Inside the crawler: `retry_on_none` handles GitHub's HTTP 202 "computing" stats
responses, `retry_with_backoff` / a transient-error httpx retry layer handle
403/429/5xx with backoff, and the commit-history `weekly_snapshots` fallback
covers stats-endpoint outages. This refresh's crawl completed all 57 originally-listed
repos with **zero unrecovered faults**; `bikespace/parking-map-data` and
`fvialibre/heseia-sentence-bias-dataset` were subsequently dropped from the corpus,
leaving **n = 55**.

---

## Output files

### Dataset-level (one row per repo unless noted)

| File | Notes |
|------|-------|
| `repo_metrics.csv` | Repository-level metrics (cloud + traditional-ML detection) |
| `person_metrics.csv` | Per-(repo, contributor); includes `is_bot` |
| `temporal_summary.csv` | PR / tag / release counts |
| `chaoss_summary.csv` | 45+ CHAOSS columns |
| `pull_requests.csv` | Individual PR records |
| `tags.csv` | Git tags |
| `core_periphery.csv` | Per-contributor network role |
| `weekly_snapshots.csv` | Weekly commit/contributor snapshots |
| `contributor_weekly_activity.csv` | Per-(contributor, ISO-week) commits + lines |
| `contributor_lifecycles.csv` | Per-contributor first/last commit, active/departed |
| `issue_records.csv` | Individual issue records (≤5,000/repo) |
| `issue_summary.csv` | Aggregated issue analytics |
| `cross_project_overlap.csv` | Contributors active in multiple crawled repos |
| **`ai_usage.csv`** | **New.** One row/repo: dev-tooling + product-LLM detection, counts, first-appearance date |
| **`ai_signals.csv`** | **New.** One row per detected AI signal: `group`, `tool`, `source`, `evidence`, `count`, `first_seen` |
| `full_results.json` | Complete nested data for all 55 repos |
| `<owner>_<repo>/data.json` | Per-repo cache (inside each repo folder after the analysis pass) |

### Generated after the crawl (analysis pass)

- `statistical_analysis/` — `scripts/statistical_analysis.py`
- `weekly_activity_analysis/` — `scripts/weekly_activity_analysis.py`
- **`ai_usage_analysis/`** — **new**, `scripts/ai_usage_analysis.py` (adoption, tool/provider
  frequencies, evidence-tier breakdown, adoption timeline, adopter-vs-non comparison, `summary.md`)
- `<owner>_<repo>/repo_results.md` + plots — `scripts/build_repo_folders.py`
  (the At-a-glance table now includes **AI-assisted development** and **Ships LLM
  product feature** rows)

---

## Reproducing this dataset

```bash
# From the repo root, with a GitHub token available:
export GITHUB_TOKEN=$(gh auth token)

# Full crawl with auto-respawn (resumable; config.yaml output -> datasets/2026_06/)
scripts/run_with_respawn.sh config.yaml datasets/2026_06 55

# Analysis pass
uv run python scripts/statistical_analysis.py datasets/2026_06/
uv run python scripts/weekly_activity_analysis.py datasets/2026_06/
uv run python scripts/ai_usage_analysis.py datasets/2026_06/
uv run python scripts/visualize.py --output-dir datasets/2026_06
uv run python scripts/build_repo_folders.py datasets/2026_06/
```

---

## Dataset summary

| | |
|---|---|
| **Repositories** | 55 |
| **Organisations** | 24 |
| **Primary languages** | 16 (C++, Dart, Dockerfile, Elixir, HCL, HTML, Java, JavaScript, Jinja, Kotlin, PHP, Python, Ruby, Svelte, TypeScript, Vue) |
| **Contributors** | 660 (606 human, 54 bot) |
| **Total commits** | 90,468 |
| **Stars / forks** | 12,908 / 3,658 |
| **Repos with CI/CD** | 47 / 55 |
| **Repos w/ cloud signals** | 29 / 55 |
| **Repos w/ traditional-ML signals** | 3 / 55 |
| **Repos w/ OSI license** | 34 / 55 |
| **Median project age** | 3.5 years |
| **Repos w/ AI-assisted development** | **24 / 55 (44%)** |
| **Repos shipping an LLM product feature** | **2 / 55 (4%)** |
| **Repos w/ any AI signal** | **25 / 55 (45%)** |

### Headline findings

**Structural (from `statistical_analysis/` + `weekly_activity_analysis/`)**

- **Effort is highly concentrated.** Team size is strongly negatively correlated
  with concentration (`num_developers` vs `hhi_no_bots` ρ = −0.76, FDR-significant):
  larger teams spread effort, but most projects stay concentrated. Many small
  repos are **100% solo** across their entire active history.
- **Scale grows with age; single-maintainer risk barely moves.** Mature repos
  (≥3.5 yr) have far more developers (median 15 vs 4, p<0.001) and commits
  (1,359 vs 196, p<0.001) and are less concentrated (HHI 4,762 vs 7,575, p=0.038),
  yet the bus factor improves only marginally (median 2 vs 1, p=0.019, small
  effect).

**AI usage (from `ai_usage_analysis/`)**

- **43% of the corpus shows AI-assisted development**, dominated by **Claude Code
  (20 repos)** and **GitHub Copilot (12)**; `AGENTS.md` appears in 6. Only **2
  repos ship an LLM product feature** — civic-tech here mostly *uses* AI to build,
  rather than *shipping* AI.
- **Adoption is recent and accelerating.** The earliest datable AI-dev signal is
  2025-Q1; cumulative adopters climb to 23 by 2026-Q2 — essentially a 2025–2026
  phenomenon.
- **AI-adopters are bigger and busier, but not better-bussed.** Adopters have
  significantly more commits (median 575 vs 272, p=0.011) and developers (11 vs 5,
  p=0.001) than non-adopters, but show **no** difference in bus factor (1 vs 1) or
  project age (p=0.91). *This is correlational, not causal* — AI tooling co-varies
  with active, multi-contributor projects.
- **Most AI-active projects:** `meshtastic/Meshtastic-Android` (199 AI-coauthored
  commits), `meshtastic/firmware` (173), `codeforjapan/BirdXplorer` (52 + 15
  bot-authored + 7 Devin PRs), `openlegaldata/oldp` (62), `CivicTechWR/go-train-group-pass`
  (11 agent PRs).

See `ai_usage_analysis/summary.md` for the full AI digest and
`statistical_analysis/` for the complete structural analysis.

---

## License, citation, and versioning

**License.** Released under **Creative Commons Attribution 4.0 International**
(CC-BY-4.0). You may share and adapt with appropriate credit and indication of
changes.

**Versioning.** This is version **2026.06** of the corpus — a refresh of the
[2026.05](../2026_05/) snapshot on the same roster, adding the AI-usage layer. It
is intended to be deposited as a new Zenodo version under the same **Concept DOI**
as 2026.05, so a citation to the Concept DOI resolves to the latest version while
a version DOI pins this snapshot.

**How to cite.** Please cite both the dataset and the crawler.

```bibtex
@dataset{civic_tech_corpus_2026_06,
  title     = {Civic-Tech Corpus — 2026-06 Refresh (n = 55, with AI-usage detection)},
  author    = {Parkkila, Janne and Tran, Duc Thinh and Olshanskaia, Viktoriia},
  year      = {2026},
  publisher = {Zenodo},
  version   = {2026.06}
}

@software{civic_tech_crawler,
  title  = {Civic Tech Git Crawler: GitHub Repository Metrics for Open Source Research},
  author = {Parkkila, Janne},
  year   = {2026},
  url    = {https://github.com/Japskua/civic-tech-git-crawler}
}
```

**Contact.** Open an issue at
<https://github.com/Japskua/civic-tech-git-crawler/issues> or email
japskua@gmail.com.
