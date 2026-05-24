# Contributor Dynamics and Sustainability in Open-Source Civic Technology: An Analysis of 57 Projects

_Companion analysis to the `datasets/2026_05` crawl. All figures are in
`figures/`; all statistics are reproducible from the CSVs in
`statistical_analysis/` and `weekly_activity_analysis/`._

---

## 1. Dataset

The corpus is **57 open-source civic-technology repositories** crawled
2026-05-21 → 2026-05-24 from the GitHub REST and GraphQL APIs. Repositories were
selected on the basis of *public-interest design intent* — civic engagement,
government services, public participation, transparency, open data, or
democratic process — and span 24 organisations across North America (Code for
America, CivicTechWR/Toronto), Africa (Code for Africa), Japan (Code for Japan),
Taiwan (g0v), and a large German "Code for"/OK-Lab cluster (Bielefeld, Münster,
Berlin, Flensburg, Cologne, Leipzig, Magdeburg, OpenLegalData), plus
participation platforms (Decidim, VoteIT, DigiDemLab) and decentralised
infrastructure (Meshtastic, IIAB). See the dataset `README.md` for the full
manifest and selection rationale.

| Property | Value |
|---|---|
| Repositories | 57 |
| Organisations | 24 |
| Primary languages | 17 |
| Contributors | 659 (605 human, 54 bot — 8.2%) |
| Total commits | 90,178 |
| Stars / forks | 12,765 / 3,611 |
| Repos with CI/CD | 48 / 57 |
| Repos with OSI-approved license | 34 / 57 |
| Median project age | 3.4 years (since first commit) |
| Weekly-activity records | 15,346 (56 repos, 1,093 contributors) |
| PR records | 37,220 |

The corpus deliberately spans a wide dynamic range: from single-developer,
zero-star prototypes (`CivicTechWR/WRVotesPlaceholder`, `VoteIT/voteit_frontend`)
to large infrastructure projects (`meshtastic/firmware` ~7.6k★ 11,910 commits,
`iiab/iiab` ~1.9k★).

### 1.1 Methodology

Per repository the crawler collects: repository metrics (languages, license,
community-health files, CI/CD, cloud & AI/ML detection); per-contributor commit
counts with a heuristic `is_bot` flag; PR and tag/release cadence; the **full
commit history** parsed into weekly snapshots, per-contributor weekly activity
(commits + lines added/removed via GraphQL) and contributor lifecycles; 45+
CHAOSS metrics (bus factor, elephant factor, HHI concentration, burstiness); and
issue analytics (capped at 5,000 issues/repo). The crawl ran through an
auto-respawning, per-repo-cached wrapper; a transient network outage and two
read-timeouts on the largest repositories were absorbed by automatic retries
with no loss of data.

Because Shapiro–Wilk tests reject normality for most metrics, all hypothesis
tests are **non-parametric** (Spearman correlation, Mann–Whitney U, Wilcoxon
signed-rank), with Benjamini–Hochberg FDR control on the correlation family.

---

## 2. Results

### 2.1 Concentration of effort is the dominant structural fact (Figure 1)

Across the 56 repositories with computable concentration metrics, **bus factor is
strongly, negatively correlated with HHI** (humans only): Spearman ρ = **−0.757**,
p = 1.5 × 10⁻¹¹. The relationship survives controlling for team size: the partial
Spearman correlation of `bus_factor_no_bots` with `hhi_no_bots` controlling for
`num_developers` is **−0.638** (classified "robust" in
`partial_correlations.csv`). Team size itself is the strongest single correlate
of concentration (`num_developers` vs `hhi_no_bots`, ρ = −0.773, FDR-significant):
larger teams spread effort, but most projects do not have larger teams.

The corpus is overwhelmingly concentrated: **median bus factor is 1** and median
HHI (no bots) is **5,374** (Figure 4) — i.e. the typical civic-tech project would
lose its institutional knowledge if a single contributor left.

### 2.2 Effort concentration exceeds commit-count concentration (Figure 2)

Counting commits understates how concentrated the *work* is. Comparing the Gini
coefficient of lines-changed per contributor against the Gini of commits per
contributor, the line-based Gini is **≥** the commit-based Gini in **41 of 56**
repositories (mean gap +0.059). A contributor who makes few but very large
commits (a lead architect, a vendored-dependency bump) concentrates effort more
than a commit count reveals.

### 2.3 Scale grows with age; the bus factor does not (Figure 5)

Splitting the corpus at its median age (3.4 years; 29 mature, 28 young), mature
projects have dramatically more **developers** (median 15 vs 3.5, Mann–Whitney
p < 0.001, large effect) and more **commits** (median 1,352 vs 189, p < 0.001,
large effect), and they are significantly **less concentrated** (HHI no-bots
4,374 vs 7,575, p = 0.008, medium effect) — effort does spread as projects age.
Yet their **bus factor is not significantly different** from young projects
(median 1 vs 1, p ≈ 0.07–0.09): the number of contributors who could leave before
the project stalls does not improve. **Civic-tech projects accumulate scale and
deconcentrate as they age without reducing the underlying single-maintainer
risk.**

### 2.4 Most weeks are solo-dominated (weekly elephant factor)

Resolving effort by week tells the same story more starkly. Weighted by active
weeks, **89% of all active weeks had a single contributor responsible for ≥50% of
the lines changed.** Many projects are 100% solo across their entire history
(`ton-An/station_reach`, `fvialibre/heseia-sentence-bias-dataset`,
`digidemlab/decidim-census`, `codeforamerica/document-transfer-service`). Only a
handful sustain genuinely distributed weekly effort — `civiform/civiform`
(mean top-contributor share 50.6%), `codeforamerica/vita-min` (55.8%),
`CodeForAfrica/actNOW` (61.3%), and `meshtastic/firmware` (65.1%) — and these are
precisely the institutionally-backed, highest-activity projects.

### 2.5 Bots inflate concentration but not the bus factor

54 of 659 contributors (8.2%) are automation accounts; in some projects they
dominate commit volume (`civiform/civiform` 56.8% bot commits). Removing bots
substantially lowers measured HHI (e.g. `bikespace/bikespace` 5,511 → 2,560;
`civic-dashboard/civic-dashboard-web` 5,368 → 2,032) but leaves the bus factor
essentially unchanged. **Bot filtering is therefore essential for any HHI-based
concentration claim and largely irrelevant for bus-factor claims** — see
`bot_impact.csv`. (`bus_factor` and `bus_factor_no_bots` correlate at ρ = 0.970.)

### 2.6 A null result: burstiness and stale issues (Figure 3)

Development burstiness (coefficient of variation of weekly commit counts) shows
**no significant relationship** with the stale-issue ratio across the 34
repositories where both are computable (Spearman ρ = 0.161, p = 0.362). Bursty
development is not associated with issue neglect in this corpus.

### 2.7 Two projects are net-negative in lines of code

Over their full default-branch history, two repositories have deleted more than
they have added — led by `CodeforLeipzig/leipziggiesst` (+4.22M / −5.90M → net
−1.68M lines, overall churn 0.58) — typically the signature of a large vendored
asset or data file being removed, and a reminder to treat raw LOC trajectories
with care.

---

## 3. Threats to validity

- **Forks (3).** `CivicTechWR/connectedkw`, `CodeforLeipzig/weihnachtsmarktkarte`,
  and `CodeforLeipzig/leipziggiesst` inherit upstream commit history and
  contributors; their concentration and bus-factor figures may be distorted.
- **Placeholder / very small repos.** Several entries are early-stage or
  near-empty; their metrics are valid but low-information. Aggregate claims should
  be checked with and without a minimum-activity threshold.
- **GitHub-only.** Every metric derives from the GitHub API. Projects that mirror
  to GitHub but develop primarily elsewhere (GitLab, Codeberg, self-hosted) would
  be misrepresented.
- **Stats-endpoint fallback.** For repositories where GitHub's `/stats` endpoints
  never returned (HTTP 202), burstiness is computed from a separately-collected
  GraphQL weekly snapshot; coverage is therefore partial (burstiness available for
  34 repos).
- **Issue cap.** Issue analytics are right-censored at 5,000 issues/repo.
- **Bot detection is heuristic.** The `is_bot` flag is login-pattern based and
  will miss org-specific bots and may misclassify human accounts.
- **Selection.** Civic-tech membership is a design-intent judgment;
  `fvialibre/heseia-sentence-bias-dataset` is a borderline (NLP-fairness) member
  and other reasonable definitions would include/exclude different projects.

---

## 4. Conclusion

Across 57 civic-tech projects spanning five continents and 24 organisations, the
dominant structural fact is **concentration**: the median project has a bus factor
of 1, effort is more concentrated than commit counts imply, and 89% of active
weeks run through a single contributor. Crucially, this does **not** resolve with
age — projects grow in developers and commits as they mature but do not become
less single-maintainer-dependent. The projects that escape this pattern are the
small minority with sustained institutional backing. For civic-tech funders and
maintainers, the actionable implication is that **sustainability is not an
emergent property of time or popularity** — it requires deliberate investment in
distributing contribution.
