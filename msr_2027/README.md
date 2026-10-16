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

## Required artefacts

- ✅ Tool publicly available at submission: <https://github.com/Japskua/civic-tech-git-crawler> (MIT)
- ✅ Running example and setup instructions: README.md + Docker image
- ✅ Dataset DOI at publication: Zenodo [10.5281/zenodo.20497015](https://doi.org/10.5281/zenodo.20497015)
- ✅ Open-source license: MIT

## Author list and order

1. **Janne Parkkila** — LUT University (corresponding)
2. **Viktoriia Olshanskaia** — LUT University
3. **Duc Thinh Tran** — IMT Atlantique / LUT University
4. **Antti Knutas** — LUT University

## Companion paper (already published)

Olshanskaia, V., Tran, D. T., Parkkila, J., Knutas, A. (2026). *Technological Landscape of Civic Tech: Current Practices and Lessons Learned.* GoodIT '26, ACM. [DOI: 10.1145/3794786.3830780](https://doi.org/10.1145/3794786.3830780).

That paper reports **empirical findings** derived from `civic-tech-crawler`. This MSR paper covers the **tool itself** — architecture, novel features (notably AI-usage detection), and tool-level validation. The two are deliberately scoped to be non-overlapping, per the MSR CFP's "substantial contribution beyond what the original paper provides" expectation.

## Contents

- [`paper.md`](paper.md) — full 4+1 page draft in markdown. Will be converted to LaTeX (`IEEEtran`) closer to submission.

## Pre-submission checklist

- [ ] Verify co-author approval on title, author order, and content
- [ ] Convert `paper.md` to IEEEtran LaTeX
- [ ] Confirm fits 4 pages main text + 1 page references
- [ ] Render Fig. 1 (architecture diagram) and Fig. 2 (AI-usage signal flow)
- [ ] Fill in proper BibTeX for all `[key]` references
- [ ] Confirm Zenodo DOI 10.5281/zenodo.20497015 is still the current record
- [ ] Add ORCID iDs for all authors
- [ ] Tag `v0.2.0` release on GitHub (ideally pinned to the submitted version)
- [ ] Internal review (someone outside author list reads it cold)
- [ ] Submit via EasyChair by Tue 10 November 2026 AoE

## Scope separation (critical)

The MSR CFP expects clear positioning. Our two-paper separation:

- **GoodIT 2026 (published)** = *empirical findings*: contributor concentration patterns, the bus-factor-does-not-improve-with-age result, AI-usage prevalence/community-variation findings.
- **MSR 2027 (this paper)** = *the tool itself*: multi-layer collector architecture, measurement-coverage-bias fallback design, novel AI-usage detection module (dev/product × active-use/intent decomposition), reproducibility infrastructure (Docker, CI, Zenodo, tests). Validation evidence is about the **tool working at scale**, not about what civic tech looks like.

If a reviewer asks "why isn't this already in GoodIT," the answer: the GoodIT paper had one methodology section describing *that* the tool was used; this paper describes *how it is built*, *why those design choices matter*, and *what makes it reusable* for other researchers.
