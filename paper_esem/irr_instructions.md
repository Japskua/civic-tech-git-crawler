# Inter-Rater Reliability (Cohen's κ) — practical instructions

**Goal:** before May 22 abstract submission, run an independent second-coder pass on the 64-candidate civic-tech pool, compute Cohen's κ for C1 and for the conjunction C1∧C2∧C3, and substitute the value in `paper_esem.tex` §3.1.

**Time estimate:** 2–3 hours of your colleague's time + ~30 min of your time to prep materials and compute κ.

**Reviewer signal:** the third peer review moved to **accept** conditional on κ being filled in. This is the single highest-leverage thing you can do before submission.

---

## Step 1 — Recruit a second coder (~5 min)

Ideal: a researcher familiar with software engineering or civic-tech research, but **not** previously involved in this paper's panel construction. They need not be a civic-tech expert; the criteria are explicit binary judgments.

Plausible candidates at LUT:
- A colleague in your research group who reads your work
- A PhD student (yours or a colleague's) who needs IRR experience anyway
- Antti Knutas (per the ICSE-SEIS 2023 paper) — civic-tech expert, would be a strong choice, though check for conflict-of-interest if you end up citing his paper

Make sure they understand the deal: 2–3 hours, anonymously credited in the paper's acknowledgements (after camera-ready), and we will publish the dual-coding spreadsheet as a supplementary artefact.

---

## Step 2 — Prepare the candidate spreadsheet (~20 min)

You need a 64-row spreadsheet that gives your colleague enough metadata to apply C1–C3 **without revealing which 37 ended up in the panel**. Include for each candidate:

| Column | Source |
|---|---|
| `candidate_id` | sequential integer 1–64 |
| `repo_full_name` | `owner/repo` from GitHub |
| `github_url` | `https://github.com/{owner}/{repo}` |
| `description` | repository `description` field from GitHub API |
| `organisation_name` | organisation display name |
| `organisation_description` | organisation's "About" text from GitHub |
| `readme_first_500_words` | first ~500 words of the repo README at crawl time |
| `topics` | GitHub topic tags |
| `language` | primary language |
| `latest_commit_date` | for C3 (proves public history exists) |

You probably already have the 37 panel repos with this metadata. For the 27 excluded candidates, you need to either:

- (a) **Reconstruct from your decision log** — if you kept notes when you screened the candidates, just pull the metadata for each excluded repo using the crawler.
- (b) **Re-screen now** — if you didn't keep the full 64-candidate list, you can rebuild it: query the umbrella organisations' repository lists and re-derive which ones failed C1 vs C3. The exact reconstruction might miss one or two, but ~60 candidates total is enough for a meaningful κ.

If you have neither (a) nor (b), the fallback is to assemble a fresh comparison set: take ~30 borderline repositories (e.g., the next-most-starred candidates from civic-tech umbrellas plus a small sample of general-purpose OSS projects from civic-adjacent topics) and have both coders re-screen those alongside the 37 included repos. The κ on that 67-repo set will be a defensible substitute.

**Format:** a Google Sheet or CSV is fine. Spreadsheet should have **two empty columns the colleague will fill in**:

- `C1_include` — Y / N (public-interest design intent satisfied?)
- `C2_include` — Y / N (public-interest steward?)
- `C3_include` — Y / N (open development with public history?)

Add one more column they fill in: `notes` (free text, used in disagreement resolution).

**Crucially: shuffle the row order.** Do not put the 37 included repos first and the excluded ones second — that signals the answer. Use a random shuffle, save the row→panel-membership mapping separately.

---

## Step 3 — Write the briefing for your colleague (~10 min)

Send them this exact text (or paste into the spreadsheet's first sheet):

> # Civic-tech inclusion-criteria coding task
>
> ## What you're doing
>
> You're independently re-coding 64 candidate GitHub repositories against three inclusion criteria for a paper on civic-tech open-source sustainability. For each repository, decide Y/N on each criterion based **only** on the metadata in this spreadsheet (repository description, organisation description, README excerpt, topics). Do not look up additional information — the goal is to test whether two researchers reading the same metadata would agree.
>
> ## The criteria
>
> **C1 — Public-interest design intent.** Code Y if the repository's stated purpose is to:
> - enable civic engagement, or
> - improve a government service, or
> - deliver public-interest information (electoral, environmental, transparency, freedom-of-information), or
> - facilitate deliberation or participation, or
> - support a democratic or public-service function.
>
> Code N if the repository is general-purpose, commercial, or its civic use is incidental to a non-civic mission. **Tiebreaker rule:** judge design intent *at project inception*, not contemporary use. A tool repurposed for civic ends but originally built as a general-purpose product is N on C1.
>
> **C2 — Public-interest steward.** Code Y if the maintaining organisation is:
> - a non-profit, government, academic, or civic-mission organisation, or
> - an independent collective whose public mission is civic technology.
>
> Code N if the steward is a commercial vendor selling civic-tech as a product to customers.
>
> **C3 — Open development.** Code Y if the repository is on a public Git forge with public commit history. Code N if it's archived without commit history, or marked private at crawl time.
>
> ## How to record decisions
>
> Fill in `C1_include`, `C2_include`, `C3_include` with Y or N. Leave a brief `notes` entry when your decision is borderline or you'd want to discuss.
>
> ## Time and access
>
> ~2–3 hours total. The spreadsheet is at [LINK]. Reach me at [EMAIL] if a candidate is genuinely ambiguous.
>
> ## What we do with your decisions
>
> We compute Cohen's κ on (i) C1 alone and (ii) the conjunction C1∧C2∧C3 (the inclusion decision actually used). Disagreements are resolved by discussion. Your final coded spreadsheet plus the disagreement-resolution notes will be published with the paper as a supplementary artefact under a CC-BY-4.0 licence; you'll be credited in the acknowledgements once camera-ready.

---

## Step 4 — Wait for the colleague to code (variable, plan ~1 week)

Don't watch them. Don't peek. Once they return the filled-in sheet, archive it as `dual_coder_round1.csv` — this is the raw second-pass data you'll publish.

---

## Step 5 — Compute Cohen's κ (~15 min)

Run this Python in the project root:

```python
import pandas as pd
from sklearn.metrics import cohen_kappa_score

# Load your decisions (the original first-pass) and the colleague's
mine = pd.read_csv("dual_coder_first_pass.csv")     # has C1_include, C2_include, C3_include
them = pd.read_csv("dual_coder_round1.csv")         # same schema
merged = mine.merge(them, on="candidate_id", suffixes=("_a","_b"))

# κ for C1 (most subjective criterion — this is the one the reviewer cares about most)
k_c1 = cohen_kappa_score(merged["C1_include_a"], merged["C1_include_b"])
print(f"Cohen's kappa, C1 only:           {k_c1:.3f}")

# κ for the conjunction (the include decision actually used in the panel)
mine_inc = (merged["C1_include_a"]=="Y") & (merged["C2_include_a"]=="Y") & (merged["C3_include_a"]=="Y")
them_inc = (merged["C1_include_b"]=="Y") & (merged["C2_include_b"]=="Y") & (merged["C3_include_b"]=="Y")
k_all = cohen_kappa_score(mine_inc, them_inc)
print(f"Cohen's kappa, C1 AND C2 AND C3:  {k_all:.3f}")

# Disagreement count, useful for the artefact write-up
print(f"\nC1 disagreements: {(merged['C1_include_a']!=merged['C1_include_b']).sum()} of {len(merged)}")
print(f"C2 disagreements: {(merged['C2_include_a']!=merged['C2_include_b']).sum()} of {len(merged)}")
print(f"C3 disagreements: {(merged['C3_include_a']!=merged['C3_include_b']).sum()} of {len(merged)}")
print(f"Inclusion (conjunction) disagreements: {(mine_inc != them_inc).sum()} of {len(merged)}")

# Print disagreement cases for resolution discussion
disagree = merged[merged["C1_include_a"] != merged["C1_include_b"]]
print(f"\nC1 disagreement details (for resolution):")
print(disagree[["candidate_id","repo_full_name","C1_include_a","C1_include_b","notes_b"]].to_string(index=False))
```

If `scikit-learn` is not in your env, install it: `uv add scikit-learn` or `pip install scikit-learn`. Or compute κ by hand from the 2×2 confusion matrix:

```
κ = (p_o - p_e) / (1 - p_e)
where p_o = observed agreement = (a + d) / n
      p_e = expected agreement = [(a+b)(a+c) + (b+d)(c+d)] / n²
with the 2×2 confusion matrix:
              Coder B: Y    Coder B: N
Coder A: Y       a            b
Coder A: N       c            d
```

---

## Step 6 — Resolve disagreements (~30 min meeting with colleague)

For each candidate where you and your colleague disagreed:

1. Look at the repository together (full README, organisation page, any project documentation).
2. Discuss which criterion is the sticking point and why.
3. Agree on a final coding. Update the panel composition if the resolution changes which 37 repositories are in.
4. Log the resolution in a `disagreement_resolutions.md` artefact file (one paragraph per disagreement: which candidate, what each coder said, what the resolution was, why).

**If the resolution changes any repository's inclusion status:** you'll need to re-run the panel-level analyses (it's just rerunning `analysis_n37.md`'s pipeline; the κ value is reported on the original independent codings, not the resolved version).

---

## Step 7 — Update the paper (~5 min)

In `paper_esem.tex` §3.1, find this paragraph:

```latex
We report Cohen's $\kappa$ on the binary include/exclude decision for C1
(the most subjective criterion) and on the conjunction C1$\wedge$C2$\wedge$C3
(the inclusion decision actually used). \textbf{Cohen's $\kappa$ = \textit{[TBD:
substituted in the camera-ready after completion of the 64-candidate dual-coding
pass]}}; until that value is reported, the single-coder operationalisation of
``design intent at project inception'' remains a residual construct-validity
threat (\S\ref{sec:threats}).
```

Replace with (substituting your actual computed values):

```latex
We report Cohen's $\kappa$ on the binary include/exclude decision for C1
(the most subjective criterion) and on the conjunction C1$\wedge$C2$\wedge$C3
(the inclusion decision actually used). \textbf{Cohen's $\kappa_{\text{C1}}$
= 0.XX; $\kappa_{\text{conjunction}}$ = 0.XX} (N disagreements out of 64,
resolved by discussion). Both values exceed the [adjective] threshold of
[citation if you want].
```

Common κ thresholds (Landis & Koch 1977):
- < 0.40 = poor / fair
- 0.40–0.60 = moderate
- 0.60–0.80 = substantial
- > 0.80 = almost perfect

For an inclusion-criteria construct like C1, **expect κ in the 0.65–0.85 range**. If you land below 0.6 the reviewer will push back; if that happens the right response is to discuss the disagreement cases in §6 and clarify whether the criteria need refinement.

In §6 Threats, also remove the residual-threat sentence ("until κ is reported..."), since it's no longer residual.

---

## Step 8 — Update the artefact (~10 min)

Add to the Zenodo deposit:
- `dual_coder_round1_independent.csv` — the colleague's independent coding (your first pass + their first pass, before resolution)
- `disagreement_resolutions.md` — the discussion log
- `dual_coder_final.csv` — the resolved coding (this is the panel as actually used)
- Append a brief "Inter-rater reliability" section to `analysis_n37.md` documenting the procedure and computed κ values.

Mention the dual-coder artefact in §3.1 ("The supplementary artefact will contain the full dual-coder decision table and the disagreement-resolution notes" — update "will contain" → "contains").

---

## Common pitfalls to avoid

- **Don't tell the colleague which 37 are in the panel until after they code.** That defeats the purpose.
- **Don't average κ values across criteria.** Report each separately. The conjunction κ is the most important.
- **Don't sweat a κ slightly below 0.60.** Discuss it honestly — the reviewer will accept "we observed moderate agreement, primarily disagreement on the design-intent-at-inception tiebreaker; following resolution discussion we refined the criterion and the final panel reflects consensus" much better than a fabricated higher value.
- **Don't skip publishing the disagreement details.** That's how reviewers verify the procedure was real.

---

## Timeline check

If today is May 17 2026 and submission is May 29:

| Day | Action |
|---|---|
| Today | Prepare spreadsheet (Step 2), recruit colleague (Step 1), send briefing (Step 3) |
| Day 1–7 | Colleague codes |
| Day 8 | Compute κ (Step 5), schedule resolution meeting |
| Day 8–10 | Resolution meeting (Step 6) |
| Day 10 | Update paper (Step 7), update artefact (Step 8) |
| Day 10–12 | Final paper read-through |
| May 22 (Day 5 of this window) | **Mandatory abstract deadline** |
| May 29 | Submission |

The mandatory abstract on May 22 only needs the abstract text; the κ value need not be in by then. But the full paper on May 29 should have it.
