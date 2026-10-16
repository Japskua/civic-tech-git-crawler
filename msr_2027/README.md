# MSR 2027 — Data and Tool Showcase

Submission target: [MSR 2027 Data and Tool Showcase Track](https://2027.msrconf.org/track/msr-2027-data-and-tool-showcase-track) (co-located with ICSE 2027, Dublin).

- **Abstract deadline:** Thursday, 5 November 2026 (AoE)
- **Paper deadline:** Tuesday, 10 November 2026 (AoE)
- **Notification:** 5 January 2027
- **Camera-ready:** 24 January 2027

## Format

- IEEE conference template, 10 pt, `\documentclass[10pt,conference]{IEEEtran}` without `compsoc` / `compsocconf`
- **4 pages main text + 1 page references**
- Single-anonymous (authors visible)
- PDF only, submitted via EasyChair

## Contents

- [`paper.tex`](paper.tex) — the paper (IEEEtran). Single source of truth; the earlier markdown draft is in git history at `53b3601`.
- [`references.bib`](references.bib) — BibTeX. DOIs are duplicated into `url` fields because `IEEEtran.bst` ignores `doi`.
- [`figures/fig1_architecture.pdf`](figures/fig1_architecture.pdf) — Fig. 1; regenerate with `uv run python msr_2027/figures/fig1_architecture.py`.

### Compiling on Overleaf

Upload `paper.tex`, `references.bib`, and `figures/fig1_architecture.pdf` (keeping the `figures/` folder), or upload the whole `msr_2027/` folder as a zip via *New Project → Upload Project*. `IEEEtran` ships with Overleaf's TeX Live; the compiler is pdfLaTeX. After the first compile, check the log for overfull `\hbox` warnings — the long `\texttt{}` file names in §II-D are the most likely culprits.

## Required artefacts

- ✅ Tool publicly available at submission: <https://github.com/Japskua/civic-tech-git-crawler> (MIT), release `1.2`
- ✅ Running example and setup instructions: README.md + Docker image (CI builds and smoke-tests it)
- ✅ Dataset DOI: Zenodo [10.5281/zenodo.20497015](https://doi.org/10.5281/zenodo.20497015) (Civic-Tech Corpus 06/2026, v1.0, MIT). Concept DOI for all versions: 10.5281/zenodo.20493287.
- ⚠️ **Software DOI: missing.** The CFP says the source code "must be citable, meaning it refers to a specific release with a DOI." The Zenodo dataset record links to GitHub tag `1.2`, but the crawler itself has no DOI. Fix before camera-ready: enable the Zenodo–GitHub integration for the repo and cut a release (e.g. `1.3`), or upload release `1.2` to Zenodo as *software*. Then add it to `references.bib` and cite it in the Availability section.

## Author list and order

| # | Author | Affiliation | ORCID |
|---|---|---|---|
| 1 | **Janne Parkkila** (corresponding) | LUT University | *needed* |
| 2 | Viktoriia Olshanskaia | LUT University | 0009-0000-3203-9944 |
| 3 | Duc Thinh Tran | LEGO, IMT Atlantique / LUT University | 0009-0008-2299-783X |
| 4 | Antti Knutas | LUT University | 0000-0002-6953-0021 |

ORCIDs 2–4 are taken from the Zenodo dataset record.

## Companion paper (already published)

Olshanskaia, V., Tran, D. T., Parkkila, J., Knutas, A. (2026). *Technological Landscape of Civic Tech: Current Practices and Lessons Learned.* GoodIT '26, ACM, pp. 402–410. [DOI: 10.1145/3794786.3830780](https://doi.org/10.1145/3794786.3830780).

That paper reports **empirical findings** derived from `civic-tech-crawler`. This MSR paper covers the **tool itself**: architecture, the coverage fallback, the AI-usage layer, and tool-level validation. The two are deliberately non-overlapping.

## Numbers used in the paper (all from `datasets/2026_06/` and `crawl_2026_06.log`)

| Claim | Value | Source |
|---|---|---|
| Repositories / GitHub orgs | 55 / 23 | `repo_metrics.csv` (`full_name` owner) |
| Contributor records (human / bot) | 660 (606 / 54) | `person_metrics.csv` |
| Commits | 90,468 | `repo_metrics.csv` `total_commits` sum |
| Repos where `/stats/commit_activity` failed → fallback | 50 of 55 | crawl log, distinct repos |
| Burstiness coverage | 54 of 54 with CHAOSS rows | `chaoss_summary.csv` |
| Median HHI with / without bots | 8,830 / 5,620; changes in 39 of 54; Wilcoxon p ≈ 4e-7 | `chaoss_summary.csv` |
| Bus factor with vs without bots | Spearman ρ = 0.92; median 1 / 1 | `chaoss_summary.csv` |
| civiform bot commit share | 58.6% | `person_metrics.csv` |
| AI: signals / tools / sources | 94 / 15 / 7 | `ai_signals.csv` |
| AI: dev adopters / active / intent-only / product | 24 / 21 / 3 / 2 | `ai_usage.csv` |
| Unit tests (bot / OSI / retry / rate limiter) | 83 (39 / 25 / 14 / 5) | `pytest` |
| Source size | ~5,000 lines | `src/**/*.py` |

**Heads-up:** `datasets/2026_06/analysis_n55.md` states 24 organisations, 661 contributors (607 human), and 90,669 commits. These differ slightly from the CSVs above, probably because they predate the final repository drops. The paper uses the CSV values. Worth reconciling the analysis doc, since it ships in the Zenodo archive.

## Pre-submission checklist

- [x] Fig. 1 (architecture diagram)
- [x] Table I (BirdXplorer `ai_signals` excerpt)
- [x] LaTeX conversion (`paper.tex`) and BibTeX (`references.bib`)
- [x] Every number re-verified against the n=55 data (table above)
- [ ] First Overleaf compile; confirm **≤ 4 pages + 1 page of references**; fix any overfull boxes
- [ ] Co-author sign-off on title, author order, and content
- [ ] Check entries marked `VERIFY` in `references.bib` against publisher pages
- [ ] Mint a software DOI for the crawler (see *Required artefacts*) and cite it
- [ ] Janne's ORCID (needed for IEEE publication workflow)
- [ ] Internal review (someone outside the author list reads it cold)
- [ ] Register abstract on EasyChair by **Thu 5 Nov 2026 AoE**
- [ ] Submit PDF by **Tue 10 Nov 2026 AoE**

## Scope separation

- **GoodIT '26 (published)** = *empirical findings*: contributor concentration, bus factor vs. project age, AI-adoption prevalence and community variation.
- **MSR 2027 (this paper)** = *the tool*: collector architecture, coverage fallback, AI-usage decomposition (dev/product × active/intent) with provenance, reproducibility infrastructure. Validation is about the tool working, not about what civic tech looks like.

If a reviewer asks why this isn't already in GoodIT: that paper's methodology section says *that* the tool was used; this paper explains *how it is built*, *why the design choices matter*, and *what makes it reusable*.
