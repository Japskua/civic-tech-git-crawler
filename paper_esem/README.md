# ESEM 2026 — Emerging Results submission package

Self-contained submission package for the ESEM 2026 Emerging Results, Vision, and Reflection Papers track. Track: **Emerging Results (10p + 2p)**. Status: **anonymous draft for double-anonymous review**.

## Contents

```
paper_esem/
├── README.md                  (this file)
├── paper_esem.md              prose draft (Markdown)
├── paper_esem.tex             LIPIcs v2021 LaTeX source
├── references.bib             BibTeX database (12 entries)
└── figures/
    ├── fig1_busfactor_vs_hhi.png       Figure 1 — bus factor vs HHI
    ├── fig2_effort_gini.png            Figure 2 — line-Gini vs commit-Gini
    ├── fig3_burstiness_vs_stale.png    Figure 3 — burstiness vs stale-issue ratio
    └── fig5_maturity_split.png         Figure 4 in the LaTeX (mature vs young projects)
```

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

## Editing notes

- The paper is anonymised throughout per the ESEM 2026 double-anonymous policy. Author block, funding, and acknowledgements all say "anonymised for double-anonymous review" — fill these in for the camera-ready version only.
- The Data Availability statement points at `[anonymous-url-redacted-for-double-blind-review]`. Replace this with the actual anonymous-mirror URL (Zenodo deposit + anonymous-github.com link or similar) before submission; the persistent Zenodo DOI replaces it in the camera-ready.
- Figures 1, 2, 3, and the maturity-split figure are referenced by the LaTeX. `fig4_cohort_boxplots.png` from the source repository is intentionally not included — it would only fit in a longer paper.
- The 10-page LIPIcs limit applies to main content (sections 1–7 + figures + tables). Data Availability and References live in the 2-page allowance on top.

## Important dates

- **Mandatory abstract:** May 22, 2026
- **Submission:** May 29, 2026
- **Notification:** July 10, 2026
- **Camera-ready:** August 5, 2026

Submission URL: <https://esem26-ervr.hotcrp.com/>
