# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Open-source publication packaging: `LICENSE.txt` (MIT), `CITATION.cff`,
  `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md`,
  `.github/` issue and PR templates, GitHub Actions CI workflow, `Dockerfile`.
- Zenodo deposit metadata for the bundled dataset
  (`datasets/2026_05/LICENSE` (CC-BY-4.0), `datasets/2026_05/CITATION.cff`,
  `datasets/2026_05/.zenodo.json`). The artifact is archived on Zenodo:
  Concept DOI [10.5281/zenodo.20493287](https://doi.org/10.5281/zenodo.20493287)
  (resolves to the latest version), Version DOI for v1.0 (2026-05)
  [10.5281/zenodo.20493288](https://doi.org/10.5281/zenodo.20493288).
- Unit tests for `bot_detection`, `rate_limiter`, and `retry` utilities
  (joining the existing `test_osi_licenses`); 83 tests in total.

### Changed
- `pyproject.toml`: declare `license`, `keywords`, `classifiers`, and
  `[project.urls]` (Repository / Issues / Documentation / Dataset).
- `README.md`: replace placeholder `github.com/your-username/...` URL with the
  real repository URL; add a Docker section to Quick Start; add a "How to cite"
  block referencing `CITATION.cff` and the (forthcoming) dataset DOI.

### Removed
- `docs/history/` — three Feb-2026 status-COMPLETE recommendation notes,
  superseded by the current implementation on `master`.
- Working-tree-only artifacts: leftover `.claude/worktrees/` (~1 GB) and
  archived crawl logs.

## [0.1.0] — 2026-05-24

Initial public release accompanying the n=57 civic-tech corpus and the paper
"Sustainability Is Not Emergent: Contributor Concentration Across 57 Open-Source
Civic-Technology Projects."

### Added
- **Canonical 2026-05 dataset** at `datasets/2026_05/` — 57 repositories from 24
  organisations across five continents, 659 contributors, 90,178 commits, with
  per-repository folders, aggregate CSVs, statistical analysis, weekly-activity
  analysis, and synthesis figures.
- **GitHub crawler** (`civic-tech-crawler`) producing repository, contributor,
  temporal, CHAOSS, weekly-snapshot, contributor-weekly-activity, and issue
  analytics.
- **Resumable crawl wrapper** `scripts/run_with_respawn.sh` with per-repository
  caching, auto-respawn on SIGKILL / non-zero exit, and adaptive backoff on
  network outages.
- **Analysis pipeline**: `scripts/statistical_analysis.py` (Spearman+FDR,
  Mann–Whitney, partial correlations, bot impact, maturity, normality),
  `scripts/weekly_activity_analysis.py`, `scripts/paper_figures.py`,
  `scripts/build_repo_folders.py`, plus migration scripts
  `scripts/recompute_burstiness.py` and `scripts/recompute_osi.py`.
- **Paper draft** `paper_draft.md` and dataset writeup `analysis_n57.md`.

### Fixed
- `is_osi_approved` undercounted OSI-approved licenses because the allow-list
  only contained the disambiguated SPDX forms (`GPL-3.0-only`, …) and missed
  the deprecated short forms GitHub's Licenses API still emits (`GPL-3.0`,
  `AGPL-3.0`, `GPL-2.0`, `LGPL-2.1`, …). Adding the short forms raised the
  corpus's OSI-approved count from 20 to 34.
- Project age was computed three different ways in `statistical_analysis.py`
  (all from `created_at` + `pd.to_datetime("now")`) while `paper_figures.py`
  used `first_commit_date` to the crawl date. Standardised every age
  computation on first-commit age measured to the fixed crawl date
  (2026-05-24); regenerated the age-dependent CSVs and updated the prose.

[Unreleased]: https://github.com/Japskua/civic-tech-git-crawler/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Japskua/civic-tech-git-crawler/releases/tag/v0.1.0
