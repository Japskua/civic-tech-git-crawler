# ESEM 2026 — Emerging Results submission package

Self-contained submission package for the ESEM 2026 Emerging Results, Vision, and Reflection Papers track. Track: **Emerging Results (10p + 2p)**. Status: **anonymous draft for double-anonymous review**.

**Current title:** *Coverage-Biased Correlations in OSS Repository Health Studies: A Self-Correction from 37 Civic-Tech Projects*

**Framing (round 2):** measurement-coverage bias is the lead methodological contribution; the 37-repository civic-tech panel is the case. Bus-factor↔HHI is demoted to a sanity check. The Wilcoxon paired-design results (bot-impact on HHI; line-Gini vs commit-Gini) are the well-powered headline findings.

## Contents

```
paper_esem/
├── README.md                  (this file)
├── paper_esem.md              prose draft (Markdown, mirrors paper_esem.tex)
├── paper_esem.tex             LIPIcs v2021 LaTeX source (canonical)
├── references.bib             BibTeX database
└── figures/
    ├── fig1_busfactor_vs_hhi.png       Figure 3 in rendered LaTeX — bus factor vs HHI (sanity check)
    ├── fig2_effort_gini.png            Figure 2 in rendered LaTeX — line-Gini vs commit-Gini (headline finding)
    ├── fig3_burstiness_vs_stale.png    Figure 1 in rendered LaTeX — burstiness vs stale (self-correction)
    └── fig4_maturity_split.png         Figure 4 in rendered LaTeX — maturity split
```

File names follow topical naming `fig1..fig4`; LaTeX auto-numbers by document order, so `\ref{fig:bf-hhi}` may print as "Figure 3" even though the file is `fig1_...`.

## Building locally

```bash
pdflatex paper_esem
bibtex   paper_esem
pdflatex paper_esem
pdflatex paper_esem
```

This requires the LIPIcs v2021 class (`lipics-v2021.cls`), which is bundled with the Overleaf LIPIcs template. If building outside Overleaf, download the class from <https://submission.dagstuhl.de/styles/>.

## Moving to Overleaf

1. Create a new project from the **LIPIcs 2021** template.
2. Upload `paper_esem.tex`, `references.bib`, and the `figures/` directory.
3. Set the main document to `paper_esem.tex`. Build.

## Open TODOs before submission (search the .tex for `TODO(author)`)

1. **Recent references** — add 1–2 OSS-health/sustainability papers from 2023–2025 to address the reviewer's currency point. Currently nothing 2022+ in the bibliography.
2. **Inter-rater reliability** — the dual-coder C1–C3 coding is currently a placeholder (`Cohen's κ = [TBD: see Data Availability]` in §3.2). Run the IRR before submission and substitute the actual κ value plus the agreement table in the artefact.
3. **Figure 1 label collision** — the reviewer flagged overlapping repository labels at the top of the bus-factor vs HHI scatter (e.g. "Forum/MagicGisp-gem" appears glued to another label). Regenerate the figure with collision avoidance (matplotlib `adjustText` or similar) before camera-ready.
4. **Anonymous mirror URL** — replace `[anonymous-url-redacted-for-double-blind-review]` in §Data Availability with the actual anonymous-Zenodo / anonymous-github.com link before submission; substitute persistent Zenodo DOI in camera-ready.
5. **Author block / funding / acknowledgements** — currently say "Anonymised for double-anonymous review"; fill in for camera-ready only.

## Editing notes

- The paper is anonymised throughout per the ESEM 2026 double-anonymous policy.
- The 10-page LIPIcs limit applies to main content (sections 1–7 + figures + tables). Data Availability and References live in the 2-page allowance on top.
- Word count: body ~4,000 prose words, ~5–6 figures+tables ≈ 9–9.5 rendered LIPIcs pages. The first compile in Overleaf will give the definitive page count; if it overruns, cheapest cuts are the §4.5 maturity paragraph and the Table 1 row-set.

## Important dates

- **Mandatory abstract:** May 22, 2026
- **Submission:** May 29, 2026
- **Notification:** July 10, 2026
- **Camera-ready:** August 5, 2026

Submission URL: <https://esem26-ervr.hotcrp.com/>
