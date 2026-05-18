---
title: "Coverage-Biased Correlations in OSS Repository Health Studies: A Self-Correction from 37 Civic-Tech Projects"
track: ESEM 2026 — Emerging Results
format: LIPIcs (10p main + 2p references/Data Availability)
anonymous: true
note: This markdown mirrors paper_esem.tex (canonical). Round-2 revision — measurement-bias-first framing pivot.
---

# Coverage-Biased Correlations in OSS Repository Health Studies: A Self-Correction from 37 Civic-Tech Projects

**Anonymous submission for double-anonymous review (ESEM 2026 ER track).**

## Abstract

Open-source-software (OSS) repository health studies routinely depend on aggregate GitHub endpoints (`/stats/contributors`, `/stats/commit_activity`) whose coverage is incomplete in ways that correlate with the variables of interest. We report emerging results from an in-progress multi-dimensional study of 37 civic-technology repositories that documents one such failure mode and a triangulation-based fix. During an internal 29-repository pilot phase we observed an apparently FDR-significant correlation between development burstiness and stale-issue ratio (ρ = 0.685, n = 17 pairs). Expanding to a 37-repository panel and recomputing burstiness from an independently-collected GraphQL bulk-fetch source raised coverage from 17/29 to 37/37 and attenuated the correlation to ρ = 0.444 (n = 26, uncorrected significant but not FDR-significant). Decomposing the change shows it is not driven by sample composition: the original 17 `/stats`-populated repositories were a positively-biased subset for which GitHub had pre-computed stats results, and that pre-computation itself correlates with project activity. We further show that even the corrected ρ = 0.444 is partly coverage-biased: the stale-issue ratio remains undefined for 11 of 37 repositories (all have zero open issues), and the populated subset is ~8× larger by commit count than the missing subset. Alongside the methodological case study we report two well-powered paired-design findings on the same panel: bot contributors significantly inflate the Herfindahl–Hirschman Index of organisational concentration (Wilcoxon W = 2.0, p = 7 × 10⁻⁶), and effort-weighted contribution Gini systematically exceeds commit-count Gini (mean Δ = +0.052, positive in 27/37 repositories, Wilcoxon p = 4.8 × 10⁻⁵). We argue that future OSS health studies that depend on aggregate endpoints should report per-metric coverage, document the missingness mechanism, and triangulate from independent sources where feasible. The toolchain implementing these recommendations is open-source.

**Keywords:** measurement-coverage bias; open-source sustainability; CHAOSS metrics; civic technology; repository mining; empirical software engineering; negative findings.

---

## 1. Introduction

Repository-mining studies of open-source health and sustainability routinely combine multiple metrics computed across many projects, then summarise pairwise associations to characterise project landscapes or to identify candidate intervention points [8, 1, 3]. Many of those metrics depend, in practice, on aggregate endpoints that GitHub computes asynchronously and serves from a cache: `/stats/contributors`, `/stats/commit_activity`, and similar. These endpoints time out (returning HTTP 202 indefinitely) for repositories whose computation has not been recently triggered server-side, and they tend to be *warm* for repositories that already receive heavy external API traffic — exactly the repositories that downstream studies disproportionately care about. The result is a non-random missingness mechanism: the repositories for which a given metric is populated are not a random subsample of the panel, and the bias correlates with the very variables of interest (activity, popularity, contributor count).

This paper reports emerging results that surfaced this failure mode in an in-progress multi-dimensional study of 37 civic-tech repositories. Civic technology — software designed to enhance civic engagement, government services, transparency, or democratic participation [11, 9] — is a small-scale OSS subdomain whose sustainability characteristics deserve their own analysis, but for the present paper its primary role is as a case where measurement-coverage bias materially altered a headline finding.

The work proceeded in two phases. In an autumn 2025 pilot we crawled 29 civic-tech repositories and observed an apparently FDR-significant correlation between development burstiness and stale-issue ratio (ρ = 0.685, p = 0.002 on n = 17 pairs). When we expanded the panel to 37 repositories in spring 2026, we discovered that the pilot estimate was built on the subset of repositories for which GitHub's `/stats/commit_activity` endpoint had returned populated data — a subset that turned out to be positively biased toward more active projects. Recomputing burstiness from an independently-collected GraphQL bulk-fetch source raised coverage to 37/37 and attenuated the correlation to ρ = 0.444, no longer surviving Benjamini–Hochberg FDR correction.

### Contributions

1. **A case study of measurement-coverage bias** in a publication-ready OSS health metric. §4.2 reports the discovery, decomposes the change between sample composition and coverage components, and shows that even the corrected estimate is itself partly coverage-biased — coverage cannot in general be solved by triangulation alone.
2. **Triangulation as engineering response.** An open-source Python toolchain (§3.3) that detects `/stats/*` time-outs, falls back to GraphQL bulk-fetch sources, and reports per-metric coverage as a first-class output. Burstiness coverage in the canonical panel is now 37/37 where the pilot was 17/29.
3. **Two well-powered paired-design findings** on the same panel that are robust to the coverage problem because they use within-repository paired comparisons: bot contributors significantly inflate HHI but not bus factor (Wilcoxon p = 7 × 10⁻⁶); effort-weighted Gini systematically exceeds commit-count Gini (Wilcoxon p = 4.8 × 10⁻⁵).
4. **An open dataset and operational definition of civic technology.** A 37-repository panel with explicit binary inclusion criteria (§3.2), an open-source crawler, and a versioned artefact (see Data Availability) supporting deterministic reproduction of every numerical claim.

### Research questions

- **RQ1 (methodological).** How does measurement-coverage bias on `/stats/*`-derived metrics distort downstream FDR-corrected correlation analyses, and can triangulation from an independent source correct it?
- **RQ2 (substantive).** What are the contributor- and organisational-concentration characteristics of the civic-tech panel, and how do they change under bot filtering?
- **RQ3 (substantive).** When effort is measured by lines changed rather than commits, how does the concentration picture shift?
- **RQ4 (substantive).** What development-pattern, responsiveness, and maturity associations are visible on the panel, with what caveats given n = 37?

The work is in progress; §7 outlines longer-term objectives.

---

## 2. Related Work

**Repository health metrics and concentration.** The CHAOSS framework [8] provides a standardised vocabulary for OSS community health metrics. The bus factor [1] and the Herfindahl–Hirschman Index measure contribution concentration; both are widely flagged as sustainability risks. Coelho and Valente [3] identified contributor departure as the primary cause of unmaintained projects. Pinto et al. [10] characterised casual contributors. DORA-style delivery metrics [5, 6] index development-practice maturity.

**Civic technology.** Civic-tech adoption surveys [9, 11] document significant variation in technical maturity and sustainability practices; most prior work is qualitative.

**Bot detection.** Dey et al. [2] and Golzadeh et al. [7] proposed heuristic and supervised methods for bot identification.

**Measurement-coverage bias.** We are not aware of prior civic-tech-specific work that has flagged the `/stats/*` coverage issue. More broadly, missing-not-at-random concerns are a recurring topic in mining-software-repositories methodology, but we have not seen the specific failure pattern we document — where a downstream FDR-corrected correlation is built on the cached subset of an asynchronous aggregate endpoint — discussed as a generalisable risk class.

*[TODO: 1–2 recent (2023–2025) OSS-health or sustainability references for currency.]*

---

## 3. Methodology

### 3.1 Framework

The framework implements 25 metrics informed by the CHAOSS project [8], organised into six categories: contributor concentration (bus factor, elephant factor, HHI in three variants, core/periphery counts); development activity (total commits, burstiness CV, new-contributor rate, weekly lines added/removed per contributor); community responsiveness (median time to first response on issues and PRs, PR review turnaround, stale-issue ratio); code review; organisational diversity; and software-delivery indicators. All concentration metrics are computed with and without bot contributors.

### 3.2 Dataset

**Operational definition of civic technology.** A repository is included if it satisfies *all* of the following binary criteria, applied against repository metadata:

- **(C1) Public-interest design intent** — the project's stated purpose is to enable civic engagement, improve a government service, deliver public-interest information (electoral, environmental, transparency, FOI), facilitate deliberation, or support a democratic or public-service function. Software whose civic use is incidental to a commercial or general-purpose mission is excluded.
- **(C2) Public-interest steward** — maintained by a non-profit, government, academic, or civic-mission organisation, or by an independent collective whose public mission is civic technology. Commercial vendors of civic-tech-as-a-product are excluded.
- **(C3) Open development** — hosted on a public Git forge with public commit history.

Borderline cases are resolved by C1: design intent at project inception, not contemporary use, determines inclusion.

**Inter-rater reliability.** C1–C3 were applied independently by two researchers to the full candidate pool. Cohen's κ = *[TBD: see Data Availability]*; disagreements were resolved by discussion. The supplementary artefact contains the dual-coder agreement table.

**Sampling frame.** The candidate pool was seeded from three sources: (i) the GitHub organisations of well-known civic-tech umbrella networks (Code for America, Code for Africa, MySociety, Democracy Club, Open Knowledge Foundation, Code for Japan); (ii) the membership rosters of those networks expanded to all repositories with ≥ 1 commit in the preceding 12 months; and (iii) targeted additions to widen scale and topical breadth, selected as: *within each of five topic categories (federated social infrastructure, mesh networking, deliberation platforms, FOI platforms, civic mapping), the most-starred public repository whose maintaining organisation satisfied C2*. 64 candidate repositories were screened against C1–C3; 37 satisfied all three criteria, 21 failed C1, and 6 failed C3.

**Panel characteristics.** 37 repositories spanning 16 primary programming languages, ages 0.2–15.0 years (median 6.3), 1–414 contributors per repository, and 9–52,222 commits (median 1,272).

### 3.3 Data collection and resilience

Data were collected via an open-source Python CLI tool interacting with the GitHub REST and GraphQL APIs, capturing repository metadata, weekly contributor stats, per-commit effort data via the GraphQL `Repository.defaultBranchRef.target.history` connection, issue and PR data (capped at 5,000 issues per repository), and bot-detection inputs.

**Resilience improvements.** GitHub's `/stats/commit_activity` and `/stats/contributors` endpoints are computed asynchronously; first requests return HTTP 202 and the build can take 30–180 s for active repositories. A prior linear-backoff budget of 45 s was insufficient — only 5 of 37 repositories returned populated stats data within budget. We replaced it with exponential backoff capped at 30 s/retry over 10 attempts (≈ 225 s total), plus a warm-up pre-pass. When `/stats/commit_activity` still does not return, the crawler derives weekly commit counts from a GraphQL bulk-fetch result. Burstiness coverage in the canonical panel is now 37/37.

**Bot detection.** Heuristic match on `[bot]` suffix, known bot logins, and `*-bot` / `*Bot` patterns, following [2, 7]. Manual inspection confirmed > 95% accuracy.

### 3.4 Metric definitions and analysis

**Burstiness** = coefficient of variation of weekly commit counts over a trailing 52-week window (the same window used by the pilot phase, retained for comparability). For 4 repositories younger than 52 weeks, the CV is computed over the full available history (16, 38, 50, 50 weeks). All values are derived from `weekly_snapshots.csv` (GraphQL), not from `/stats/commit_activity`.

**Stale-issue ratio** = fraction of currently-open issues with no activity (comment, label change, edit) for at least 90 days (matching the widely-used `stale[bot]` default). Undefined when a repository has zero open issues.

**Statistical analysis.** Shapiro–Wilk tests confirmed non-normality for 11 of 12 key metrics. Pairwise Spearman correlations across 17 metrics (136 unique pairs), Benjamini–Hochberg FDR correction at α = 0.05, partial Spearman correlations on 10 key pairs controlling for `num_developers`, Mann–Whitney U with Cliff's δ [12], Wilcoxon signed-rank for paired metric variants. Given n = 37 and per-metric coverage gaps, we treat the inferential layer as exploratory and the paired-design Wilcoxon results as the most robust findings.

---

## 4. Results

### 4.1 Panel summary

The 37 repositories include 703 total contributors (654 human, 49 bot) and 178,099 commits. The GraphQL-derived contributor-week table covers 22,486 rows, 2,344 unique attributable contributors, 44.4 M cumulative lines added, and 34.8 M cumulative lines removed. Table 1 gives descriptive medians; we report these for context and turn to the methodological case study below.

**Table 1: Descriptive statistics on the 37-repository panel.**

| Metric | n | Median | IQR | Range |
|---|---|---|---|---|
| Total commits | 37 | 1,272 | 6,978 | 9 – 52k+ |
| Num. developers | 37 | 11 | 26 | 1 – 414 |
| Bus factor | 37 | 2 | 1 | 1 – 5 |
| HHI (no bots) | 37 | 4,357 | 4,585 | 1,059 – 10,000 |
| Burstiness CV (52w) | 37 | 0.91 | 0.54 | 0.31 – 1.89 |
| Stale-issue ratio | 26 | 0.98 | 0.26 | 0.00 – 1.00 |
| Issue first response (h) | 24 | 34.4 | 71.6 | 0.0 – 7,300 |
| PR review turnaround (h) | 29 | 3.20 | 20.4 | 0.0 – 902 |
| Network density | 29 | 0.40 | 0.27 | 0.13 – 1.00 |

### 4.2 The measurement-coverage discovery (RQ1)

**Pilot finding.** During an autumn 2025 pilot phase we computed pairwise Spearman correlations across 17 metrics on 29 civic-tech repositories. The burstiness ↔ stale-issue ratio correlation appeared as a robust headline result: ρ = 0.685, p = 0.002, FDR-significant; partial ρ = 0.553 controlling for `num_developers`. Both metrics behaved as expected directionally (bursty development → more accumulated stale issues), and the partial-correlation control on team size strengthened the interpretation that the relationship was structural rather than size-mediated.

**Coverage problem.** The estimate was computed on n = 17 of 29 repositories — the only ones for which both burstiness and stale-issue ratio were populated at crawl time. Burstiness was the limiting factor: GitHub's `/stats/commit_activity` endpoint had timed out for 12 of 29 repositories, returning HTTP 202 indefinitely under our 45-second retry budget. The 17 repositories that did return populated data were those for which GitHub's asynchronous stats build had been recently triggered server-side, which itself correlates with external API traffic and project activity.

**Correction.** Expanding the panel to 37 repositories surfaced the issue. Recomputing burstiness from a separately-collected GraphQL bulk-fetch source (§3.3) raised coverage to 37 of 37. The burstiness ↔ stale-issue ratio correlation on the corrected data is **ρ = 0.444, p = 0.023, n = 26 pairs**. The pair's rank among the 136 BH-ordered tests is 35, with corresponding BH critical value 35 × 0.05 / 136 = 0.0129; the observed p = 0.023 > 0.0129, so the pair does *not* survive BH correction. (For context, 31 pairs do survive; the largest surviving p at rank 31 is 0.0092, critical value 0.0114.) The partial correlation controlling for `num_developers` is ρ = 0.393, p = 0.047, n = 25.

**Decomposition.** The change is not driven by sample composition. Table 2 decomposes the attenuation: restricting the recomputed burstiness to only the original 29 pilot repositories yields ρ = 0.461 — close to the wider-sample ρ = 0.444 and far from the pilot's ρ = 0.685. The 17 repositories with `/stats` data in the pilot were a positively-biased subset; the same repositories contribute weaker burstiness ↔ stale signal when burstiness is measured from an independent source. Figure 1 shows the corrected relationship.

**Table 2: Decomposition of the burstiness ↔ stale-issue correlation under three sampling scenarios.**

| Sample | Pairs | ρ | p | Notes |
|---|---:|---:|---:|---|
| Pilot (n=29), `/stats` only | 17 | 0.685 | 0.002 | Coverage-biased |
| Full panel (n=37), recomputed | 26 | **0.444** | 0.023 | Wider repos AND coverage |
| Pilot 29 only, recomputed | 19 | 0.461 | 0.039 | Same repos, fuller coverage |

![Figure 1](figures/fig3_burstiness_vs_stale.png)

**Figure 1.** Burstiness vs. stale-issue ratio after the coverage fix on the full 37-repository panel (26 pairs). The direction is preserved; the magnitude is moderate (ρ = 0.444) rather than strong (ρ = 0.685).

**Coverage of the corrected estimate.** The corrected ρ = 0.444 is itself computed on only 26 of 37 repositories: stale-issue ratio remains undefined for 11 repositories that all have zero open issues at crawl time (deterministic missingness, not censoring). The populated subset, however, is positively biased toward larger projects: Spearman(populated, `total_commits`) = +0.454 (p = 0.005); median `total_commits` is 254 in the missing group versus 2,034 in the populated group — an ≈ 8× gap. The corrected estimate is therefore best read as the burstiness/stale-issue relationship *conditional on the project having open issues*, which is itself a function of project scale. The discovery teaches a stronger lesson than "triangulate to fix coverage": triangulation reduces one bias mechanism but the corrected metric can remain coverage-biased through a second mechanism on a different metric in the same pair. Reporting per-metric coverage and decomposing missingness mechanisms is the more defensible practice.

### 4.3 Effort-resolved concentration: a paired-design result (RQ3)

We computed, for each of the 37 repositories, both the Gini coefficient of `lines_added + lines_removed` per contributor over full history (**line-Gini**) and the Gini coefficient of `commits` per contributor (**commit-Gini**). The paired comparison is robust to coverage problems because both Ginis are computed from the same GraphQL bulk-fetch contributor-week data for the same 37 repositories.

**Line-Gini is systematically higher than commit-Gini.** Full-history line-Gini has median 0.70 (IQR 0.21). Across the 37 repositories, line-Gini exceeds commit-Gini in 27 cases, is smaller in 6, and is equal in 4: mean Δ = +0.052. A Wilcoxon signed-rank test on the 33 non-zero pairs rejects the null of zero difference: **W = 53.0, p = 4.8 × 10⁻⁵**. A one-sided sign test on 27/33 positive differences gives p = 1.6 × 10⁻⁴.

**Implication.** Research that uses commit counts as a proxy for contribution weight systematically under-estimates effort concentration. At the largest scales (> 5,000 commits), the line-Gini saturates near 1 while the commit-Gini stays moderate (0.76–0.95), indicating that effort concentration is dominated by a small number of large-line-count commits that the count-based metric treats as equivalent to small commits. We refer to this as the high-Gini regime visible only at flagship scale, but do not in this paper validate the specific commit-level mechanism (refactors, batch-merges) by inspection of the dominant commits; that would be useful follow-up. Figure 2 displays the paired comparison.

![Figure 2](figures/fig2_effort_gini.png)

**Figure 2.** Effort Gini (lines) vs. effort Gini (commits) per repository. Points above the y = x diagonal are repositories where effort concentration is more extreme than commit-count concentration suggests. The pattern is consistent across 27 of 37 repositories (Wilcoxon p = 4.8 × 10⁻⁵).

### 4.4 Contributor concentration and bot impact (RQ2)

**Concentration.** Median bus factor 2 (range 1–5 with bots; 1–4 without). Seventeen repositories (46%) have a bus factor of 1 — a single developer accounts for ≥ 50% of project commits. Median HHI 6,344 with bots and 4,357 without — a 31% reduction. Median per-repository **elephant-week share** (weeks in which a single contributor accounts for ≥ 50% of `lines_added` + `lines_removed`) is 96.6% (IQR 94.9–100.0%, range 43.6–100.0%); weighted by active weeks, 83.3% of all active panel-weeks are elephant weeks.

**Bot impact is metric-specific (paired design).** A Wilcoxon signed-rank test comparing HHI with and without bots across all 37 repositories yields W = 2.0, **p = 7 × 10⁻⁶** (27 of 37 repositories change): bot contributors systematically inflate organisational concentration as measured by HHI. The same test on bus factor finds no difference (W = 5.0, p = 1.00, 4 of 37 change); the elephant factor is unchanged in all 37 repositories. The recommendation for downstream studies is metric-specific: filter bots when computing HHI; safely include them in bus-factor analyses.

**Sanity check: bus factor and HHI.** The strongest pairwise zero-order Spearman correlation in the panel is ρ(bus_factor, HHI) = −0.920, with partial ρ = −0.872 after controlling for `num_developers` (Figure 3). We flag this as a sanity check rather than as a substantive finding: bus factor and HHI are non-independent summary statistics of the same per-contributor commit-count distribution, so a negative correlation between them is partly an arithmetic identity. The partial-correlation control on team size demonstrates the relationship is not explained by panel scale, but does not separate the arithmetic component from a substantive claim about distribution shape. A random-null simulation calibrating the expected ρ under shuffled contribution shares would be a useful follow-up.

![Figure 3](figures/fig1_busfactor_vs_hhi.png)

**Figure 3.** Bus factor vs. HHI on the n=37 panel (ρ = −0.920; partial ρ = −0.872 after controlling for team size). The two metrics are non-independent summary statistics of the same contribution distribution; we treat the correlation as a sanity check on metric behaviour rather than an independent finding. Marker size encodes `num_developers`.

### 4.5 Development patterns, responsiveness, and maturity (RQ4)

**Development patterns.** Burstiness CV has median 0.91 (IQR 0.54). Community-health percentage [8] has median 50% with three repositories at 100% and one at 0% — many civic-tech projects lack standard community documentation. Stale-issue ratio has median 0.98 (n = 26): the median civic-tech project has ≈ 98% of its open issues without recent activity.

**Responsiveness and review collaboration.** Median issue first-response time 34.4 h (n = 24); median PR review turnaround 3.20 h (n = 29); the negative correlation between PR acceptance ratio and PR review turnaround (ρ = −0.552, partial −0.542, n = 29) survives size control. Review-collaboration network density has median 0.40 (n = 29), with 7 dense networks (> 0.5); core-reviewer count negatively correlates with density (partial ρ = −0.655).

**Maturity.** Splitting the panel at median age (6.3 y) into mature (n = 19) and young (n = 18) cohorts, mature projects have significantly more developers (medians 27 vs. 5, p = 0.004, δ = 0.55), more total commits (3,521 vs. 638, p = 0.009, δ = 0.51), and higher bus factor (p = 0.036, δ = 0.38). Burstiness and community-health percentage do not differ significantly by maturity (Figure 4). We tested cross-organisation differences via Kruskal–Wallis for the three organisations with n ≥ 3 but report them only descriptively in the artefact: n = 3 in two of the three groups is too few for inferential claims.

![Figure 4](figures/fig4_maturity_split.png)

**Figure 4.** Mature (≥ 6.3 years, n = 19) vs. young (n = 18) repositories. Mature projects gain developers, commits, and bus factor; HHI and burstiness do not differ significantly by maturity.

---

## 5. Discussion

**Measurement-coverage bias is a generalisable risk class.** The pattern documented in §4.2 is not specific to burstiness or to civic-tech repositories. Any OSS health study that joins an aggregate endpoint with cache-driven coverage to a target metric, then computes a correlation across the joined subset, can exhibit the same failure: the joined subset will be biased toward repositories the aggregate endpoint has been recently invoked for, which itself correlates with project activity. We recommend three practices for downstream studies: *(i) report per-metric coverage in the methodology section, with denominators*; *(ii) document the missingness mechanism for each metric*; *(iii) where feasible, triangulate from an independent source*. Practice (iii) is not always available, but for many CHAOSS-aligned metrics a GraphQL bulk-fetch alternative exists; we offer our crawler's in-collector fallback as a reference implementation.

**Triangulation is not a complete fix.** The corrected ρ = 0.444 is itself computed on the subset of repositories with non-zero open issues. This second-mechanism coverage bias is structurally different (deterministic missingness on a domain criterion, not asynchronous cache behaviour) but it still skews the estimate toward larger, more active projects. The deeper lesson is that triangulation reduces individual bias mechanisms without guaranteeing population coverage; decomposing missingness mechanisms is the more defensible practice. A natural follow-up is to develop coverage-tolerant variants of the affected metrics — for stale-issue ratio specifically, a binary "has any stale issue" indicator defined for all 37 repositories would be a starting point.

**Paired-design results are robust by construction.** The bot-impact result on HHI (W = 2.0, p = 7 × 10⁻⁶) and the line-Gini vs. commit-Gini result (W = 53.0, p = 4.8 × 10⁻⁵) are paired within-repository comparisons: the coverage of each metric across the panel does not enter the test because each pair is its own control. These designs are the most robust to the coverage-bias risk we document and should be preferred in small-sample OSS health studies.

---

## 6. Threats to Validity

**Construct validity.** Bus factor and HHI are commit-based and undervalue contributors who primarily review code, manage issues, or write documentation; the effort-Gini analysis (§4.3) mitigates this for the lines-changed dimension. The civic-tech inclusion criteria (C1–C3) are applied by two coders with disagreements resolved by discussion; until κ is reported in the camera-ready, single-rule operationalisation of "design intent at project inception" remains a residual construct-validity threat.

**External validity.** The 37-repository panel is purposive, not a probability sample of any defined civic-tech population. Results may not generalise to all civic-tech projects, particularly self-hosted or non-GitHub projects. The artefact deposit lists repositories by name and several entries are uniquely identifiable; ESEM allows GitHub references in anonymised submissions but reviewers should note that the dataset is identifiable on artefact inspection. The methodological case study (§4.2) is a single-instance discovery and we do not claim that other downstream OSS-health correlations in the literature are similarly biased — only that the failure mode is reproducible and worth auditing.

**Statistical validity.** n = 37 limits power for detecting small effects. We treat the inferential layer as exploratory and emphasise the paired-design Wilcoxon results, which have large effect sizes and within-repository controls. Coverage per metric in this paper: `burstiness_cv` 37/37 (after triangulation; previously 5/37); `stale_issue_ratio` 26/37 (all 11 missing have zero open issues); time-to-first-response (issues) 24/37; PR review turnaround 29/37; network density 29/37.

**Measurement-coverage validity.** §4.2 is itself the threats-to-validity discussion of the predecessor estimate. We have addressed coverage for burstiness but cannot rule out similar issues for other metrics in the panel until each is systematically audited.

---

## 7. Conclusions and Longer-Term Plan

We reported emerging results that surfaced a measurement-coverage failure mode in OSS repository health metrics: a pilot-phase correlation between development burstiness and stale-issue ratio of ρ = 0.685 attenuates to ρ = 0.444 after triangulating from an independent data source, with the change driven by coverage bias rather than sample composition. Even the corrected estimate is partly coverage-biased through a second mechanism. We also reported two paired-design within-repository findings on the same 37-repository civic-tech panel that are robust by construction: bot contributors significantly inflate HHI but not bus factor (Wilcoxon p = 7 × 10⁻⁶), and effort-weighted Gini systematically exceeds commit-count Gini (Wilcoxon p = 4.8 × 10⁻⁵). The strongest pairwise Spearman correlation in the panel (ρ = −0.920 between bus factor and HHI) is reported as a sanity check, not as a substantive finding, because the two metrics are partially algebraically dependent.

The work is in progress along three axes. **(L1) Longitudinal tracking**: quarterly recrawls of the 37-repository panel over a 24-month horizon, with change-over-time analyses and event-study designs around governance changes. **(L2) Replication and extension**: extension to non-GitHub hosts (GitLab, Codeberg, self-hosted Gitea) and to a larger civic-tech population (target n ≥ 100). **(L3) Coverage-bias audit**: a systematic audit of which CHAOSS-aligned metrics are exposed to the same failure mode, with triangulation alternatives where they exist. Future OSS health studies that depend on aggregate `/stats/*` endpoints should report per-metric coverage, document missingness mechanisms, and triangulate where feasible.

---

## Data Availability

In accordance with ESEM 2026's open-science policy, all artefacts supporting the claims in this paper will be deposited in **Zenodo** under CC-BY 4.0 (data) / MIT (code) licences and assigned a DOI. For the duration of double-anonymous review the deposit is mirrored at an anonymous URL at `[anonymous-url-redacted-for-double-blind-review]`; the persistent Zenodo DOI replaces this in the camera-ready version.

The deposit contains: the Python CLI toolchain (with the resilience features in §3.3); the canonical May 2026 results snapshot (`repo_metrics.csv`, `chaoss_summary.csv`, `contributor_weekly_activity.csv`, `weekly_snapshots.csv`, `issue_summary.csv`, and per-repository raw API caches); the dual-coder C1–C3 agreement table and κ computation; all analysis scripts including `scripts/paper_figures.py` (regenerates Figures 1–4 deterministically) and `scripts/recompute_burstiness.py` (the GraphQL-derived recompute used in §4.2); and an `analysis_n37.md` documenting the statistical pipeline.

---

## References

[1] Avelino, G., Passos, L., Hora, A., & Valente, M. T. (2016). A novel approach for estimating truck factors. In *Proc. ICPC*, pp. 1–10.

[2] Dey, T., Mousavi, S., Ponce, E., Fry, T., Vasilescu, B., Filippova, A., & Mockus, A. (2020). Detecting and characterizing bots that commit code. In *Proc. MSR*, pp. 209–219.

[3] Coelho, J., & Valente, M. T. (2017). Why modern open source projects fail. In *Proc. ESEC/FSE*, pp. 186–196.

[4] Eghbal, N. (2020). *Working in Public: The Making and Maintenance of Open Source Software*. Stripe Press.

[5] Forsgren, N., Humble, J., & Kim, G. (2018). *Accelerate: The Science of Lean Software and DevOps*. IT Revolution Press.

[6] Forsgren, N., Storey, M.-A., Maddila, C., Zimmermann, T., Houck, B., & Butler, J. (2021). The SPACE of developer productivity. *Communications of the ACM*, 64(6), 46–53.

[7] Golzadeh, M., Decan, A., Legay, D., & Mens, T. (2021). A ground-truth dataset and classification model for detecting bots in GitHub issue and PR comments. *Journal of Systems and Software*, 175, 110911.

[8] Goggins, S. P., Lumbard, K., & Germonprez, M. (2021). Open source community health: Analytical metrics and their corresponding narratives. In *Proc. SoHeal*, pp. 25–32.

[9] McNutt, J. G., et al. (2016). The diffusion of civic technology and open government in the United States. *Information Polity*, 21(2), 153–170.

[10] Pinto, G., Steinmacher, I., & Gerosa, M. A. (2016). More common than you think: An in-depth study of casual contributors. In *Proc. SANER*, pp. 112–123.

[11] Patel, M., Sotsky, J., Gourley, S., & Houghton, D. (2013). *The Emergence of Civic Tech: Investments in a Growing Field*. Knight Foundation.

[12] Romano, J., et al. (2006). Appropriate statistics for ordinal level data. In *Annual Meeting of the Florida Association of Institutional Research*, pp. 1–33.
