# Sustainability Is Not Emergent: Contributor Concentration Across 57 Open-Source Civic-Technology Projects

**Draft — 2026-05.** Grounded entirely in the `datasets/2026_05` corpus (n = 57).
Figures: `datasets/2026_05/figures/`. Reproducible statistics:
`datasets/2026_05/statistical_analysis/` and `.../weekly_activity_analysis/`.

---

## Abstract

Open-source civic technology — software built to support civic engagement,
government services, transparency, and democratic participation — is widely
promoted as a sustainable, community-owned alternative to proprietary govtech.
We test that premise empirically. We crawl 57 civic-tech repositories from 24
organisations across five continents and compute repository, contributor, and
CHAOSS sustainability metrics, including a time-resolved weekly contribution
analysis. The landscape is heterogeneous and long-tailed: the median project has
7 developers, 389 commits, and 4 stars, yet four infrastructure projects supply
39% of all commits and 93% of all stars; 12 of 57 repositories carry no
open-source license and none publishes a governance document. Against that
backdrop we find that **contribution is overwhelmingly concentrated**: the
median project has a bus factor of 1, effort measured in lines changed is more
concentrated than commit counts suggest (lines-Gini ≥ commits-Gini in 41 of 56
repositories), and 89% of all active project-weeks are dominated by a single
contributor. Most importantly, **concentration does not resolve with age**:
mature projects accumulate significantly more developers and commits than young
ones (p < 0.01) but show no significant improvement in bus factor or
concentration. The projects that escape single-maintainer dependence are a small
minority with sustained institutional backing. We conclude that civic-tech
sustainability is not an emergent property of time or popularity and must be
deliberately engineered.

---

## 1. Introduction

Civic technology occupies an unusual position in the open-source landscape: it is
frequently public-interest infrastructure (election information, freedom-of-
information portals, participatory-budgeting platforms, open environmental data)
maintained by volunteer communities, civic-tech non-profits, and occasional
government sponsorship. A recurring claim in the civic-tech movement is that open
development confers *sustainability* — that community ownership protects these
tools from the abandonment that plagues single-vendor govtech.

This paper asks whether the data support that claim. Using a 57-repository corpus
spanning the major civic-tech communities, we characterise how contribution is
distributed within projects, whether that distribution improves as projects
mature, and what distinguishes the projects that achieve genuinely distributed
maintenance.

Our contributions are:

1. A reproducible, multi-community civic-tech dataset (57 repositories, 24
   organisations, 659 contributors, 90,178 commits) with per-contributor *weekly*
   contribution resolution, released alongside the crawler that produced it.
2. A quantitative description of the open-source civic-tech landscape — its
   composition by region and language, its scale distribution, and its licensing
   and engineering-practice norms — across five continents.
3. Evidence that contribution concentration — not size, popularity, or activity —
   is the dominant structural feature of civic-tech projects.
4. The finding that concentration does **not** attenuate with project age, which
   challenges the "sustainability through longevity" intuition.

## 2. Related work (stub)

Prior work on open-source sustainability has established the *bus factor* and
*truck factor* as measures of knowledge concentration, the *elephant factor* and
Herfindahl–Hirschman Index (HHI) as measures of organisational concentration, and
the CHAOSS metrics family as a standard for community health. Civic technology
specifically has been studied more qualitatively (movement histories, case
studies of Code for America / mySociety / g0v). This paper contributes a
quantitative, cross-community measurement. _[Full citations to be added.]_

## 3. Dataset and methodology

### 3.1 Corpus selection

Repositories were selected on the basis of **public-interest design intent** —
the software must be designed for civic engagement, government services, public
participation, transparency, open data, or democratic process, rather than merely
admitting incidental civic use. The 57 repositories span 24 organisations:

- **North America** — Code for America (9), CiviForm, and the Canadian
  CivicTechWR / Toronto community (bikespace, choruslabs, civic-dashboard,
  CivicTechWR).
- **Africa** — Code for Africa (9).
- **Japan / Taiwan** — Code for Japan (incl. a Decidim deployment), g0v.
- **Germany** — a large "Code for"/OK-Lab cluster: Bielefeld, Münster, Berlin,
  Flensburg (nine OK-Lab open-data maps), Cologne, Leipzig, Magdeburg, and
  OpenLegalData.
- **Participation platforms & infrastructure** — VoteIT, DigiDemLab/Decidim,
  Meshtastic (firmware/Android/web), Internet-in-a-Box (IIAB).

The corpus deliberately spans a wide dynamic range — from single-developer
prototypes to 7,600-star infrastructure — so that contributor-dynamics findings
are not artefacts of a single project scale. Three repositories are forks and one
(`fvialibre/heseia-sentence-bias-dataset`) is a borderline NLP-fairness member;
both are flagged in the threats to validity.

### 3.2 The civic-tech landscape

The corpus is heterogeneous on every axis, and describing that heterogeneity is
itself a contribution: there is no single "typical" civic-tech project.

**Scale is heavily right-skewed.** The median repository has 389 commits, 7
developers, 4 stars, and 2 forks, but the means (1,582 commits, 21 developers, 224
stars) are pulled up by a few large infrastructure projects. The four
infrastructure repositories — Meshtastic (firmware/Android/web) and IIAB — alone
account for **34,823 of the corpus's 90,178 commits (39%) and 11,916 of its 12,765
stars (93%)**; `meshtastic/firmware` by itself has 414 developers, 7,632 stars,
and 11,910 commits. At the other end, a quarter of repositories have ≤1 star and
≤154 commits, and 11 are essentially single-developer efforts. Civic tech is thus
a long tail of small projects under a few large ones, and any unweighted mean is
misleading — we report medians throughout.

**Age** spans 0.6–9.2 years (median 3.4). The oldest projects are
`CodeForAfrica/GenderGap.AFRICA` (9.2 y), `iiab/iiab` (9.0 y), and
`CodeForAfrica/openAFRICA` (8.7 y); the youngest are recent CivicTechWR tools and
single-contributor prototypes.

**Geography.** The corpus spans five continents and 24 organisations. The German
"Code for"/OK-Lab cluster contributes the most repositories (18) but they are
individually small — many are single-purpose open-data maps — whereas the
international infrastructure projects are few but vastly larger:

| Region / cluster | Repos | Total commits | Median devs | Total stars |
|---|---:|---:|---:|---:|
| Germany (Code for / OK Lab) | 18 | 4,787 | 3.5 | 227 |
| Africa (Code for Africa) | 9 | 17,854 | 7 | 76 |
| USA (Code for America, CiviForm) | 9 | 17,726 | 10 | 223 |
| Canada (CivicTechWR / Toronto) | 9 | 7,461 | 15 | 76 |
| Intl. infrastructure (Meshtastic, IIAB) | 4 | 34,823 | 91 | 11,916 |
| Japan, Taiwan, UK, Sweden, others | 8 | 7,527 | — | 247 |

Notably, the Canadian CivicTechWR projects have the **highest median team size**
(15) of any regional cluster despite modest commit volumes — a community-driven,
many-hands pattern — while the US and African projects are the most
commit-dense among the non-infrastructure clusters.

**Languages** reflect civic tech's web-and-data orientation. Web-stack languages
(HTML, TypeScript, JavaScript, Vue, Svelte) are the *primary* language of **29 of
57** repositories; Python (10) and Ruby (6) dominate the backends, with a long
polyglot tail (Java, C++, Kotlin, Dart, Elixir, Jinja, HCL, Jupyter, PHP, Dart).

**Licensing is inconsistent — a governance risk for public-interest software.**
**12 of 57 repositories carry no detectable license at all**, leaving their legal
reusability ambiguous. Among the 45 that do: permissive licenses lead (MIT 16,
Apache-2.0 3, BSD 1 = 20), copyleft is well represented (GPL-3.0 9, AGPL-3.0 4,
GPL-2.0 1 = 14), and **9 repositories — almost all open-data projects — use the
CC0 public-domain dedication**, a signature of the open-data wing of the movement.

**Engineering practice is mature on the surface but thin underneath.** CI/CD is
near-ubiquitous (48/57, 84%) and READMEs are almost universal (54/57), but the
deeper community-health scaffolding that supports *distributed* maintenance is
sparse: CONTRIBUTING guides 20/57, codes of conduct 8/57, issue templates 4/57,
and **explicit governance documents 0/57**. Only **23 of 57** repositories have
ever cut a tagged release. The median GitHub community-health score is 50%. Cloud-
deployment signals appear in 29/57 repositories; AI/ML signals in just 6/57.

In aggregate the corpus comprises 659 contributors (605 human, 54 bots) producing
90,178 commits, 37,220 pull requests (85% merged), 14,032 issues (85% closed), and
1,979 releases. This is the backdrop against which the concentration findings
below should be read: a movement that has adopted modern tooling (CI, PRs) but not
the governance and contributor-distribution practices that sustain it.

### 3.3 Data collection

For each repository we collect, via the GitHub REST and GraphQL APIs:
repository-level metrics (languages, license and OSI status, community-health
files, CI/CD, cloud and AI/ML signal detection); per-contributor commit counts
with a heuristic bot flag; PR and tag/release cadence; the **full commit history**
parsed into weekly project snapshots, per-contributor weekly activity (commits
and lines added/removed), and contributor lifecycles; 45+ CHAOSS metrics
including bus factor, elephant factor, HHI, and burstiness; and issue analytics
(capped at 5,000 issues per repository). Collection ran through an
auto-respawning, per-repository-cached wrapper; one transient network outage and
two read-timeouts on the largest repositories were absorbed by automatic retries
with no data loss.

### 3.4 Statistics

Shapiro–Wilk tests reject normality for most metrics, so all hypothesis tests are
non-parametric: Spearman rank correlation (with Benjamini–Hochberg FDR control on
the correlation family), Mann–Whitney U for group comparisons, and Wilcoxon
signed-rank for paired bot-impact tests. Concentration metrics are reported both
with and without bot contributors.

## 4. Results

### 4.1 Concentration is the dominant structural fact (Fig. 1, Fig. 4)

Bus factor is strongly, negatively correlated with organisational concentration
(HHI, humans only): Spearman ρ = −0.757 (p = 1.5 × 10⁻¹¹, n = 56). The
relationship is robust to team size — the partial correlation controlling for
`num_developers` is −0.638 — and team size is itself the strongest correlate of
concentration (ρ = −0.773). The corpus is overwhelmingly concentrated: the median
bus factor is **1** and the median HHI is **5,374** (Fig. 4). The typical
civic-tech project would lose its working knowledge with the departure of one
person.

### 4.2 Effort concentration exceeds commit-count concentration (Fig. 2)

The Gini coefficient of lines-changed per contributor is ≥ the Gini of commits
per contributor in 41 of 56 repositories (mean gap +0.059). Commit counts
*understate* how concentrated the substantive work is.

### 4.3 Scale grows with age; sustainability does not (Fig. 5)

Split at the corpus median age, mature projects have far more developers (median
11 vs 3.5, p = 0.002) and commits (1,274 vs 193, p < 0.001) than young ones — but
their bus factor is statistically indistinguishable (p > 0.05 at every reasonable
threshold) and their concentration does not improve. Age buys scale, not
resilience.

### 4.4 Most weeks run through one person (weekly elephant factor)

Weighted by active weeks, 89% of project-weeks had one contributor responsible
for ≥50% of lines changed. Many projects are 100% solo across their whole history.
The exceptions — `civiform/civiform`, `codeforamerica/vita-min`,
`CodeForAfrica/actNOW`, `meshtastic/firmware` — are the institutionally-backed,
highest-activity projects, suggesting distributed maintenance is purchased, not
grown.

### 4.5 Bots inflate concentration but not the bus factor

Automation accounts (8.2% of contributors) can dominate commit volume (e.g.
`civiform` 56.8% bot commits). Removing them sharply lowers measured HHI but
leaves the bus factor essentially unchanged (`bus_factor` vs `bus_factor_no_bots`
ρ = 0.970). Bot filtering is essential for HHI-based claims and largely irrelevant
for bus-factor claims.

### 4.6 A null result (Fig. 3)

Development burstiness shows no significant association with the stale-issue ratio
(ρ = 0.161, p = 0.362, n = 34). Bursty development does not predict issue neglect
in this corpus.

## 5. Discussion

The consistent finding across repository-level, effort-weighted, and
weekly-resolved analyses is that civic-tech contribution is concentrated and stays
concentrated. The movement's "sustainability through openness" narrative is not
borne out at the level of contributor distribution: openness has not, by itself,
distributed the work. Because concentration does not improve with age, waiting for
projects to mature is not a sustainability strategy. The projects that achieve
distributed maintenance share an institutional sponsor (a civic-tech non-profit or
a well-funded infrastructure project), which points to organisational investment —
not community size or longevity — as the operative lever.

## 6. Threats to validity

Forks (3) inherit upstream history; several repositories are placeholders or very
small; all metrics are GitHub-only; burstiness coverage is partial where GitHub's
`/stats` endpoints never returned; issue analytics are right-censored at 5,000
issues/repo; the bot flag is heuristic; and civic-tech membership is a
design-intent judgment. See `datasets/2026_05/analysis_n57.md` §3 for detail.

## 7. Conclusion

Across 57 civic-tech projects on five continents, sustainability is not an
emergent property of time or popularity. The median project depends on a single
maintainer, effort is more concentrated than commit counts reveal, and age brings
scale without resilience. Distributing contribution appears to require deliberate
institutional investment. For funders and maintainers, the implication is direct:
treat bus factor as a first-class, actively-managed risk rather than something the
open-source process will resolve on its own.

---

_Data, figures, and reproducible analysis: `datasets/2026_05/`. Crawler and
methodology: repository root `README.md`._
