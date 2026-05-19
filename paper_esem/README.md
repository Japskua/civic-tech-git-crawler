# ESEM 2026 — Emerging Results submission package

Self-contained submission package for the ESEM 2026 Emerging Results, Vision, and Reflection Papers track. Track: **Emerging Results (10p + 2p)**. Status: **anonymous draft for double-anonymous review**.

**Current title:** *The Civic-Tech Open-Source Landscape: Sustainability Challenges Across 37 Projects*

**Round-5 revision (responding to third peer review — reviewer moved recommendation to ACCEPT).** The paper is organised around six sustainability challenges. Round 5 addressed the remaining accept-conditional concerns:

- Reconciled the 113-vs-59 cross-project number inconsistency the reviewer caught. The two prior figures came from two CSVs with different contributor-dedup conventions (`cross_project_overlap.csv` uses a stricter GraphQL-author key, 511 logins; `contributor_lifecycles.csv` uses per-repo attribution, 2,055 humans). The paper now uses `contributor_lifecycles.csv` throughout for internal consistency. Updated abstract, §1, §4.6, §5, §6 to all use the same denominator (2,055 humans → 5.5% cross-project → 8.9% of those cross-organisational → 0.5% of all panel humans).
- Rewrote §5's discussion paragraph on the ecosystem finding to match the sharpened §4.6 framing ("umbrella-bounded" with explicit sensitivity-survival reasoning rather than the looser "umbrella-shaped, not panel-shaped").
- Compressed §1 contribution list (was 7 items: 3 novel + 2 confirmatory + 2 infra; now 2 novel bullets + 1 confirmatory sentence + 1 infrastructure sentence).
- Compressed §2 Related Work (was 5 paragraphs by topic; now 2 dense paragraphs: OSS-health-and-contributor-dynamics + civic-technology).
- Compressed Challenge 1 "Are they coming back" + "Implication" into one paragraph.
- Downgraded "very large effect" → "large effect" (reviewer flagged this invites a pedantic threshold-table reviewer).
- Sharpened the recent-refs TODO comment to call out the reviewer's specific suggestions (Schrock, Saldivar et al., post-2013 Knight Foundation).
- Verified all cross-references resolve correctly.

**Previous rounds:**

**Round-4 revision (responding to second peer review).**

- Abstract and §1 reweighted to lead with **novel contributions** (effort-Gini paired comparison, elephant-week metric, sensitivity-aware cross-project ecosystem). Confirmatory findings (drive-by, low bus factor) are marked as confirming prior small-team-OSS literature.
- §4.6 expanded with a **sensitivity check** addressing umbrella-network sampling bias: of 113 cross-project humans, only 11 (9.7%) span ≥ 2 stewarding organisations. The "umbrella-bounded" pattern survives the sensitivity check.
- §3.3 added bus-factor methodology (Avelino cumulative-share) and clarified **elephant-factor as borrowed from CHAOSS; elephant-week as this paper's contribution**.
- All Wilcoxon tests now include matched-pairs rank-biserial r effect sizes. Cliff's δ added to the maturity Mann–Whitney tests.
- §4.4 added a coverage caveat on the PR-turnaround vs issue-first-response comparison (29/37 vs 24/37).
- §5 softened "more fragile than commercial OSS" to "consistent with prior findings on small-team OSS" + planned (L4) matched commercial-OSS comparison panel.
- §6 added per-metric coverage table.
- §6 added explicit sampling-frame selection acknowledgment.
- Figure 3 (effort Gini) regenerated with non-overlapping labels (`fig_effort_gini_clean.png`).
- Figure 5 (cross-project) regenerated with intra-umbrella vs cross-umbrella color coding (`fig_cross_project_v2.png`).
- Added `gitter-badger` to the bot filter (was leaking into cross-project results).

## Contents

```
paper_esem/
├── README.md                          (this file)
├── paper_esem.md                      prose draft (Markdown, mirrors .tex)
├── paper_esem.tex                     LIPIcs v2021 LaTeX source (canonical)
├── references.bib                     BibTeX database (19 entries)
├── slides/
│   ├── build_slides.js                pptxgenjs script (round-3 framing)
│   └── colleague_briefing.pptx        9-slide briefing for colleagues
└── figures/
    Active (used by the .tex):
    ├── fig_challenges_dashboard.png   Figure 1 — 4-panel challenges overview
    ├── fig_contributor_duration.png   Figure 2 — contributor engagement histogram
    ├── fig_effort_gini_clean.png      Figure 3 — line-Gini vs commit-Gini (cleaned labels)
    ├── fig_activity_vs_age.png        Figure 4 — weekly commits vs project age
    └── fig_cross_project_v2.png       Figure 5 — top-15 cross-project humans, umbrella-colored
    Superseded (not used by current .tex):
    ├── fig1_busfactor_vs_hhi.png      (used in rounds 1/2; cut)
    ├── fig2_effort_gini.png           (round-3 figure 3 with overlapping labels; replaced)
    ├── fig3_burstiness_vs_stale.png   (used in rounds 1/2; cut)
    ├── fig4_maturity_split.png        (used in rounds 1/2; cut)
    └── fig_cross_project.png          (round-3 figure 5 without umbrella coloring; replaced)
```

## Open TODOs before submission

### Critical (reviewer's desk-reject risk)
1. **Inter-rater reliability — RUN THE ACTUAL DUAL-CODING.** §3.1 commits to a dual-coder pass on the 64-candidate pool. Recruit a colleague (estimated 2–3 hours of work). Substitute the κ value in §3.1 before the May 22 abstract deadline. The supplementary artefact also needs the dual-coder decision table.

### Important
2. ~~Recent (2023–2025) references.~~ **DONE in round-6** — added 5 verified refs: Knutas2023 (ICSE-SEIS), Saldivar2019 (CSCW), Schrock2019 (Emerald chapter), Knight2017 (Knight Foundation sustainability report), Lumbard2024 (Information Systems Journal). See `recent_refs_candidates.md` for the rationale per cite.
3. **Anonymous mirror URL** — replace `[anonymous-url-redacted-for-double-blind-review]` in the Data Availability statement with the actual anonymous-Zenodo / anonymous-github.com link before submission.
4. **Author block / funding / acknowledgements** — currently anonymised; fill in for camera-ready only.

## Building locally

```bash
pdflatex paper_esem
bibtex   paper_esem
pdflatex paper_esem
pdflatex paper_esem
```

Requires the LIPIcs v2021 class (`lipics-v2021.cls`), bundled with the Overleaf LIPIcs template.

## Moving to Overleaf

1. New project from the **LIPIcs 2021** template.
2. Upload `paper_esem.tex`, `references.bib`, and the `figures/` directory.
3. Set the main document to `paper_esem.tex`. Build.

## Word count / page budget

- Body prose ~4,500 words after round-4 expansion (was ~3,600 in round 3)
- 5 figures, 1 new coverage table
- Estimated 9.5–10 LIPIcs pages of main content

If the first Overleaf compile overruns the 10p main-content limit, the cheapest cuts are:
- Trim the expanded contributions list in §1 (currently 7 items split novel/confirming/infrastructure; could collapse to 4)
- Drop the maturity Cliff's δ details from §4.5 paragraph 2 (move to artefact)
- Tighten §3.1 sampling-frame description (the funnel can go into a single sentence)

## Important dates

- **Mandatory abstract:** May 22, 2026
- **Submission:** May 29, 2026
- **Notification:** July 10, 2026
- **Camera-ready:** August 5, 2026

Submission URL: <https://esem26-ervr.hotcrp.com/>
