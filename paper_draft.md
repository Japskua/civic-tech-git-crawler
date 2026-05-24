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
analysis. We find that **contribution is overwhelmingly concentrated**: the
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
   organisations, 659 contributors, 90k commits) with per-contributor *weekly*
   contribution resolution, released alongside the crawler that produced it.
2. Evidence that contribution concentration — not size, popularity, or activity —
   is the dominant structural feature of civic-tech projects.
3. The finding that concentration does **not** attenuate with project age, which
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

### 3.2 Data collection

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

### 3.3 Statistics

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
