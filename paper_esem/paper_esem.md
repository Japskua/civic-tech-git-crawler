---
title: "Measuring Civic-Tech Repository Health: Emerging Results from a Multi-Dimensional Study of 37 Open-Source Projects"
track: ESEM 2026 — Emerging Results
format: LIPIcs (10p main + 2p references/Data Availability)
anonymous: true
---

# Measuring Civic-Tech Repository Health: Emerging Results from a Multi-Dimensional Study of 37 Open-Source Projects

**Anonymous submission for double-anonymous review (ESEM 2026 ER track).**

## Abstract

Civic technology — software developed to support civic engagement, government transparency, and public participation — increasingly depends on small, often volunteer-led, open-source communities, yet its sustainability is poorly characterised at scale. We present emerging results from an in-progress multi-dimensional study of 37 civic-tech repositories drawn from 16 organisations (electoral systems, government services, environmental monitoring, mesh networking, federated social infrastructure, deliberation platforms, and digital rights) spanning 15 years of project history. We operationalise 25 CHAOSS-aligned metrics in an open-source Python toolchain, augment them with PR review network analysis and an effort-resolved view of weekly lines added/removed per contributor, and apply non-parametric statistical testing with FDR correction and partial-correlation controls. The dataset reveals critically low contributor concentration (median bus factor 2; 46% of repositories at bus factor 1), high organisational concentration (median HHI 4,357 after bot filtering), and 83% of all active weeks dominated by a single contributor. Effort-weighted Gini systematically exceeds commit-count Gini (mean Δ = +0.057, positive in 33/37 repositories). During the study we also discovered, and report here, a methodological pitfall: an earlier 29-repository pilot phase of the analysis produced a correlation between development burstiness and stale-issue ratio of ρ = 0.685 (FDR-significant on n=17 pairs), but expanding the panel to 37 repositories and triangulating burstiness with GraphQL bulk-fetch data exposed measurement-coverage bias in GitHub's `/stats/commit_activity` endpoint and attenuated the relationship to ρ = 0.444 (uncorrected significant, not FDR-significant). We position these findings as emerging results en route to a longitudinal civic-tech health programme and surface measurement-coverage bias as a systemic risk for small-sample OSS health research.

**Keywords:** civic technology; open-source sustainability; CHAOSS; bus factor; measurement bias; repository mining.

---

## 1. Introduction

Civic technology encompasses software designed to facilitate civic engagement, improve government services, enhance transparency, and enable democratic participation [11]. Unlike commercially backed open-source projects, many civic-tech projects depend on volunteer contributors, intermittent grant funding, and small non-profit teams. When such a project becomes unmaintained — a voter information service goes stale before an election, a freedom-of-information platform stops receiving security updates — the consequences extend beyond the developer community to democratic participation and public-service delivery.

Despite growing interest in OSS sustainability [4, 6, 8] and civic-tech adoption [9, 11], systematic empirical analysis of civic-tech project health remains limited. Existing work focuses either on large-scale mining of general-purpose repositories [3] or on qualitative case studies of individual initiatives [9]. There is a methodological gap for rigorous, multi-dimensional, quantitative analysis of civic-tech repository health using standardised metrics. We contribute four pieces toward filling that gap:

1. **A measurement framework** implementing 25 indicators from the CHAOSS project [8], augmented with PR review collaboration networks, contributor retention cohorts, organisational concentration indices, DORA delivery metrics [6], and an **effort-resolved view** that records weekly lines added/removed per contributor — a level of granularity not present in commit-count-based CHAOSS instantiations.

2. **An open-source toolchain** (Python CLI) that collects these metrics from the GitHub REST and GraphQL APIs, applies heuristic bot detection [2, 7], and exports structured datasets. The tool incorporates resilience features (exponential-backoff retry on async `/stats/*` endpoints with warm-up pre-pass, in-collector fallback to GraphQL-derived weekly snapshots, auto-respawn under external SIGKILL) developed in response to the measurement-coverage failures reported in §4.4.

3. **An empirical study of 37 civic-tech repositories** from 16 organisations across 16 programming languages and 15 years of project history. We apply Spearman correlations with Benjamini–Hochberg FDR correction, Mann–Whitney U and Wilcoxon signed-rank tests, Kruskal–Wallis tests, and partial correlations to characterise the health landscape and identify factors associated with sustainability.

4. **A methodological pitfall discovered mid-study**, reported under the ESEM ER track's explicit welcome of negative findings. During an earlier 29-repository pilot phase of the analysis we observed an apparently robust correlation between development burstiness and stale-issue ratio (ρ = 0.685, FDR-significant). Expanding the panel to 37 repositories made the issue visible: the pilot estimate was inflated by **measurement-coverage bias** — GitHub's `/stats/commit_activity` endpoint had timed out for the majority of repositories, leaving burstiness available only for an opportunistically-cached subset. Triangulating with GraphQL bulk-fetch data and re-running the analysis on the wider panel raises coverage to 37/37 and attenuates the correlation to ρ = 0.444 (uncorrected significant, not FDR-significant). The relationship is real but smaller than the pilot suggested.

### Research questions

- **RQ1.** How concentrated are contributions in civic-tech projects, and does bot filtering change the picture?
- **RQ2.** What temporal patterns characterise civic-tech development, and how do they relate to issue management?
- **RQ3.** Which project-health metrics are correlated, and which correlations survive correction for multiple testing and control for project size?
- **RQ4.** How responsive are civic-tech communities to issues and pull requests?
- **RQ5.** How do maturity, technology stack, and organisational context relate to health outcomes?

The work is in progress; §7 outlines longer-term objectives, including longitudinal tracking, extension to non-GitHub hosts, and intervention-design studies driven by the partial-correlation findings.

---

## 2. Related Work

**Project health and contributor concentration.** The CHAOSS framework provides a standardised vocabulary for OSS community health metrics organised around activity, engagement, and responsiveness [8]. The bus factor [1] measures the minimum number of contributors whose departure would jeopardise a project; Avelino et al. analysed 133 popular GitHub projects and found that most have dangerously low values. Coelho and Valente [3] studied unmaintained GitHub projects and identified contributor departure as the primary cause of project death. Organisational diversity — captured by metrics such as the Herfindahl–Hirschman Index (HHI) and the elephant factor [8] — is a key sustainability indicator.

**Contributor dynamics.** Pinto et al. [10] studied casual contributors and showed that their individually small contributions collectively represent a significant portion of project activity. Eghbal [4] characterised the maintainer-volunteer model that dominates much of the OSS ecosystem.

**Civic technology.** Civic-tech adoption surveys [9, 11] identify significant variation in technical maturity, community engagement, and sustainability practices. Most existing civic-tech work is qualitative; we are not aware of prior quantitative multi-metric studies of civic-tech repository health at the scale presented here.

**Software delivery.** DORA metrics [6] — deployment frequency, lead time for changes, change failure rate, time to restore — were designed for commercial teams but indicate the maturity of development practices in civic-tech projects.

**Bot detection.** Automated bots (Dependabot, Renovate, GitHub Actions) distort contributor metrics. Dey et al. [2] and Golzadeh et al. [7] proposed heuristic and supervised methods for bot identification; failing to filter bots inflates activity metrics and skews concentration analyses.

**Measurement-coverage bias.** Repository-mining studies routinely depend on aggregate endpoints whose coverage is incomplete in ways that correlate with the variables of interest. GitHub's `/stats/*` endpoints, for instance, are computed asynchronously and may time out for active repositories whose computation budget is exhausted; the repositories that *do* return are disproportionately those for which GitHub has cached recent results, which itself correlates with project popularity and activity. We are not aware of prior civic-tech-specific work that has flagged this risk; §4.4 of this paper revisits a previously-published correlation in light of it.

---

## 3. Methodology

### 3.1 Framework design

The framework implements 25 metrics organised into six categories (Table 1). All concentration metrics (bus factor, elephant factor, HHI) are computed both with and without bot contributors, and HHI is additionally computed in a "known organisations only" variant that excludes contributors with unknown organisational affiliation.

**Table 1: Metric categories**

| Category | Metrics |
|---|---|
| Contributor concentration | Bus factor, elephant factor, HHI (3 variants), core/periphery counts |
| Development activity | Total commits, burstiness CV, new-contributor rate, weekly lines added/removed |
| Community responsiveness | Median time to first response (issues, PRs), PR review turnaround, stale-issue ratio |
| Code review | Change request acceptance ratio, average review comments per PR |
| Organisational diversity | HHI by organisation, contributor org types, unknown-org count |
| Software delivery (DORA) | Deployment frequency, median lead time, change failure rate |

### 3.2 Dataset

We selected 37 repositories from 16 organisations representing diverse civic-tech domains. Selection criteria: (a) explicit civic-technology mission — software designed to enhance civic engagement, government services, transparency, public participation, deliberation, or democratic processes; (b) public GitHub commit history; and (c) at least one commit in the preceding 12 months. We intentionally varied repository size, maturity, and organisational context to capture the breadth of the civic-tech ecosystem. The dataset spans 16 primary programming languages, ages 0.2–15.0 years (median 6.3), 1–414 contributors per repository, and 9–52,222 commits (median 1,272). Notable extremes include a federated social-infrastructure project at 49,930 stars and a deliberation platform at 52,222 commits — the largest commit count in the sample. The full repository list is in the supplementary `repo_metrics.csv` (see Data Availability).

### 3.3 Data collection

Data were collected via an open-source Python CLI tool interacting with the GitHub REST and GraphQL APIs:

- Repository metadata, languages, license, topics, community profile;
- Weekly contributor stats via `GET /repos/{owner}/{repo}/stats/contributors`, with iterative-retry around HTTP 202 (computation in progress) and a fallback to commit-history-derived attribution;
- **Per-commit effort data** (oid, additions, deletions, committedDate, author) fetched in 100-commit batches via the GraphQL `Repository.defaultBranchRef.target.history` connection. This yields a (repository × contributor × ISO-week) table covering 22,486 rows;
- Weekly per-repo commit counts via the same GraphQL pipeline, used as the canonical burstiness source (see §3.5);
- Issue and pull-request data via paginated endpoints (capped at 5,000 issues per repository);
- Contributor profiles via `GET /users/{login}`;
- Technology detection (CI/CD, cloud, AI/ML) via file and dependency scanning.

**Bot detection.** A contributor is classified as a bot if the GitHub login matches: (a) the `[bot]` suffix, (b) a curated list of known bot logins (`github-actions[bot]`, `snyk-bot`, `codecov[bot]`, `imgbot[bot]`, `stale[bot]`, `allcontributors[bot]`, `transifex-integration[bot]`), or (c) the patterns `*-bot` / `*Bot`. This follows established practice [2, 7]; manual inspection of flagged accounts confirmed > 95% accuracy on this dataset.

### 3.4 Resilience improvements (motivating the self-correction)

GitHub's `/stats/commit_activity` and `/stats/contributors` endpoints are computed asynchronously; first requests return HTTP 202, and the build can take 30–180 s for active repositories. A prior linear-backoff budget of 45 s was insufficient — only 5 of 37 repositories returned populated stats data within budget. We replaced it with exponential backoff capped at 30 s/retry over 10 attempts (≈225 s total), plus a warm-up pre-pass that fires one request per repository at crawl start so async builds proceed in parallel server-side. When `/stats/commit_activity` still does not return, the crawler now derives weekly commit counts from a GraphQL bulk-fetch result (independently collected and reliable). Burstiness coverage in the canonical dataset is 37 of 37.

### 3.5 Burstiness measurement

Burstiness is the coefficient of variation (CV) of weekly commit counts over a fixed window. We use a trailing 52-week window for the headline metric (the same window used by the pilot phase analysis in §4.4.1, retained for comparability). All values reported in this paper are derived from the GraphQL-derived `weekly_snapshots.csv`, not from `/stats/commit_activity`. Validation on the 5 repositories where both sources are available shows trailing-52w agreement within ±0.07 in 4 of 5 cases.

### 3.6 Analysis approach

Shapiro–Wilk tests confirmed non-normality for 11 of 12 key metrics, justifying non-parametric methods throughout. We computed pairwise Spearman rank correlations across 17 metrics (136 unique pairs) and applied Benjamini–Hochberg FDR correction at α = 0.05. For 10 key pairs we additionally computed partial Spearman correlations controlling for `num_developers` (rank-transform → OLS residualise on the control → Pearson on residuals). Group comparisons used Mann–Whitney U (two-group) and Kruskal–Wallis (three+ groups), with Cliff's δ and ε² as effect sizes (Romano et al. thresholds [12]). Paired metric variants (with/without bots) were compared with the Wilcoxon signed-rank test.

---

## 4. Results

### 4.1 Dataset overview

The 37 repositories include 703 total contributors (654 human, 49 bot) and 178,099 commits. The GraphQL-derived contributor-week table covers 22,486 rows, 2,344 unique attributable contributors, 44.4 M cumulative lines added, and 34.8 M cumulative lines removed. Median values for the key metrics are summarised in Table 2; the dataset exhibits high variability, reflecting the heterogeneity of the civic-tech ecosystem from single-developer infrastructure modules to platforms with hundreds of contributors.

**Table 2: Descriptive statistics (n = 37 unless noted)**

| Metric | n | Median | IQR | Min | Max |
|---|---|---|---|---|---|
| Total commits | 37 | 1,272 | 6,978 | 9 | 52,222 |
| Num. developers | 37 | 11 | 26 | 1 | 414 |
| Bus factor | 37 | 2 | 1 | 1 | 5 |
| Bus factor (no bots) | 37 | 2 | 1 | 1 | 4 |
| Burstiness CV (52w) | 37 | 0.91 | 0.54 | 0.31 | 1.89 |
| HHI | 37 | 6,344 | 4,083 | 2,092 | 10,000 |
| HHI (no bots) | 37 | 4,357 | 4,585 | 1,059 | 10,000 |
| Stale-issue ratio | 26 | 0.98 | 0.26 | 0.00 | 1.00 |
| CR acceptance ratio | 36 | 0.82 | 0.13 | 0.22 | 1.00 |
| Issue first response (h) | 24 | 34.4 | 71.6 | 0.0 | 7,300 |
| PR review turnaround (h) | 29 | 3.20 | 20.4 | 0.0 | 902 |
| Core contributors | 37 | 1 | 4 | 0 | 9 |
| Network density | 29 | 0.40 | 0.27 | 0.13 | 1.00 |
| Health percentage | 37 | 50 | 25 | 0 | 100 |

### 4.2 Contributor concentration (RQ1)

The median bus factor across all 37 repositories is **2** (IQR 1, range 1–5 with bots; 1–4 without). **Seventeen repositories (46%) have a bus factor of 1** — a single developer accounts for ≥ 50% of project commits, and their departure would critically endanger the project. The median HHI is 6,344 (IQR 4,083) with bots and drops to 4,357 (IQR 4,585) without — a 31% reduction. The "known organisations only" HHI is 8,025.

**Bot impact is metric-specific.** A Wilcoxon signed-rank test comparing HHI with and without bots across 37 repositories yields **W = 2.0, p = 7 × 10⁻⁶** (n changed = 27): bot contributors systematically inflate organisational concentration. In contrast, the bus factor shows no significant difference (W = 5.0, p = 1.00, n changed = 4), and the elephant factor is unchanged in all 37 repositories. Bots distort fine-grained concentration metrics but not coarser thresholds.

### 4.3 Development patterns (RQ2)

The trailing-52w burstiness CV has a median of 0.91 (IQR 0.54, range 0.31–1.89). Three repositories exhibit CV > 1.5 — highly bursty, irregular development characteristic of intermittently-funded or volunteer-sprint-driven projects. The lowest burstiness (0.31) is a 50k-star federated infrastructure project with sustained weekly commits from a core team.

The GitHub community health percentage has a median of 50% (IQR 25%, range 0–100%); only three repositories achieve 100%, and one scores 0%. The wide range indicates that many civic-tech projects lack standard community documentation (CONTRIBUTING, CODE_OF_CONDUCT, issue/PR templates) that supports contributor onboarding.

The stale-issue ratio has a median of **0.98** (IQR 0.26, n = 26) — the median civic-tech project has ≈ 98% of its open issues without recent activity. The change-request acceptance ratio has a median of 0.82 (IQR 0.13, range 0.22–1.00).

### 4.4 Correlation analysis and a methodological self-correction (RQ3)

Of 136 Spearman pairs, 47 were significant at uncorrected α = 0.05; **31 survived Benjamini–Hochberg FDR correction**. The strongest non-trivial relationship is between bus factor and HHI:

**ρ(bus_factor_no_bots, HHI_no_bots) = −0.920** (zero-order); **partial ρ = −0.872** controlling for `num_developers`.

Figure 1 visualises this relationship. The negative association is mechanically expected — as the number of key contributors increases, organisational concentration decreases — and it persists after controlling for project size, indicating a genuine structural relationship rather than a size artefact.

![Figure 1](figures/fig1_busfactor_vs_hhi.png)

**Figure 1.** Bus factor vs. HHI on the n=37 sample (Spearman ρ = −0.920; partial ρ = −0.872 after controlling for team size). Marker size encodes `num_developers`. The negative relationship is the central concentration-of-effort mechanism in the dataset.

**Partial correlations.** Of 10 key pairs subjected to size-controlled partial-correlation analysis, **five relationships are robust** (Δρ < 0.10 after residualisation): bus_factor ↔ HHI; burstiness ↔ stale-issue ratio; core_contributor_count ↔ network_density (ρ_partial = −0.655); CR_acceptance ↔ PR_turnaround (ρ_partial = −0.542); and burstiness ↔ health_percentage (ρ_partial = −0.304, borderline). **Five relationships are confounded by project size**, including the apparent positive relationship between bus factor and health-percentage that reverses sign after residualisation.

#### 4.4.1 Burstiness ↔ stale-issue ratio: a measurement-coverage discovery

During an earlier pilot phase of this study we crawled a 29-repository subset of the panel and computed an apparently robust correlation between development burstiness and stale-issue ratio (ρ = 0.685, p = 0.002, FDR-significant; partial ρ = 0.553 after size control). That estimate was computed on **n = 17 of 29 repositories** — the only ones for which both burstiness and stale-issue ratio were populated at the time. **Burstiness was the limiting factor**: GitHub's `/stats/commit_activity` endpoint had timed out for the other 12 repositories.

Expanding the panel to 37 repositories surfaced the issue. Recomputing burstiness from a separately collected GraphQL bulk-fetch source (see §3.5) raises coverage to 37 of 37 and gives:

- **Zero-order**: ρ = 0.444, p = 0.023, n = 26 pairs (uncorrected significant; **not FDR-significant** at the dataset's adjusted α threshold of ≈ 0.012)
- **Partial controlling `num_developers`**: ρ = 0.393, p = 0.047, n = 25

Decomposing the change (Table 3) shows that **sample composition is not the driver**: restricting the recomputed burstiness to only the original 29 pilot repositories yields ρ = 0.461, close to the wider-sample ρ = 0.444 and far from the pilot's ρ = 0.685.

**Table 3: Decomposition of the burstiness ↔ stale-issue correlation**

| Sample | Pairs | ρ | p | Notes |
|---|---:|---:|---:|---|
| Pilot phase (n=29), `/stats` data only | 17 | 0.685 | 0.002 | Coverage-biased estimate |
| Full panel (n=37), recomputed | 26 | **0.444** | 0.023 | Wider repos AND fuller coverage |
| Pilot 29 only, recomputed | 19 | 0.461 | 0.039 | Wider coverage, same repos |

The 17 repositories with `/stats` data in the pilot were a positively-biased subset for which GitHub had cached stats results, and that caching itself correlates with project activity. The substantive relationship is real and moderately positive (ρ ≈ 0.4), but its magnitude is meaningfully smaller than the pilot suggested, and at the corrected coverage it does not survive FDR correction. We report the discovery here as a cautionary case study; §5 discusses the systemic risk. Figure 3 shows the corrected relationship.

![Figure 3](figures/fig3_burstiness_vs_stale.png)

**Figure 3.** Burstiness vs. stale-issue ratio after the coverage fix. The direction is preserved; the magnitude is moderate rather than strong.

### 4.5 Community responsiveness (RQ4)

The median time to first response for issues is **34.4 hours** (IQR 71.6, range 0.0–7,300, n = 24); the extreme upper bound is approximately ten months. The median PR review turnaround is **3.20 hours** (IQR 20.4, range 0.0–902, n = 29) — substantially better than issue responsiveness, likely reflecting that PRs represent immediate contribution opportunities that maintainers prioritise. The negative correlation between PR acceptance and PR turnaround (ρ = −0.552, partial −0.542) is robust to size control: projects that review PRs faster also accept a higher proportion of them.

### 4.6 Maturity and contextual factors (RQ5)

Splitting the dataset at the median age (6.3 years) into mature (n = 19) and young (n = 18) cohorts, Mann–Whitney tests reveal that mature projects have significantly more developers (medians 27 vs 5, p = 0.004, δ = 0.55 large), more total commits (3,521 vs 638, p = 0.009, δ = 0.51 large), and higher bus factor (p = 0.036, δ = 0.38 medium). Burstiness and health-percentage do not differ significantly by maturity — irregular development patterns and documentation gaps are not simply features of young projects. Figure 5 visualises the maturity split.

![Figure 5](figures/fig5_maturity_split.png)

**Figure 5.** Mature (≥ 6.3 years, n=19) vs. young (n=18) repositories. Mature projects gain developers, commits, and bus factor; HHI shows no significant difference.

CI/CD adoption (31 of 37 repositories) is associated with larger, more active teams (medians 11 vs 4.5 developers, U = 140, p ≈ 0.055, δ = 0.51), at the edge of significance. Cross-organisation Kruskal–Wallis tests for the three organisations with n ≥ 3 reveal significant differences in `num_developers` (H = 7.47, p = 0.024, ε² = 0.29) and stale-issue ratio (H = 8.77, p = 0.013, ε² = 0.68).

### 4.7 Effort concentration (lines vs commits)

The contributor-week effort data enables three analyses not possible with commit-count metrics alone.

**(A) Weekly elephant factor.** For each repository we compute, per week, the share of total weekly `lines_added + lines_removed` contributed by the busiest single author. **Weighted by active weeks across the dataset, 83% of all active weeks are "elephant weeks"** — a single contributor accounts for ≥ 50% of the week's code change. Five repositories fall below the 65% mean-top-share threshold; all five have ≥ 5 contributors and substantial team scale. Below that scale, single-author weeks are the norm.

**(B) Effort Gini coefficient.** Across the 37 repositories, the full-history line-Gini has median 0.70 (IQR 0.21). Line-Gini is systematically higher than commit-Gini: **mean Δ = +0.057, positive in 33 of 37 repositories**. At the largest scales (>5,000 commits) the line-Gini saturates near 1 while the commit-Gini stays moderate (0.76–0.95) — a "mega-commit regime" in which a small number of large refactor or batch-merge commits dominate effort concentration. Figure 2 displays the line-Gini vs commit-Gini relationship.

![Figure 2](figures/fig2_effort_gini.png)

**Figure 2.** Effort Gini (lines) vs. effort Gini (commits) per repository. Points above the y=x diagonal indicate effort concentration is more extreme than commit-count concentration suggests. The upper-right cluster (line-Gini ≥ 0.94) is the mega-commit regime visible only at flagship scale.

**(C) Churn ratio.** Weekly churn `= deletions / (additions + deletions)` summarises growth vs. cleanup posture. The dataset median is 0.34 (IQR 0.16) — below the 0.50 balanced-maintenance threshold — indicating most repositories are still in growth mode. Three repositories show net-negative full-history LOC, all attributable to one-off purges of committed generated data.

Together, the three analyses paint a consistent picture: civic-tech effort is concentrated *across contributors* (Gini ≈ 0.70 median) and *across time* (83% single-contributor weeks), and effort-based measurement reveals concentration that commit-count metrics systematically under-estimate.

---

## 5. Discussion

**Civic-tech sustainability is fragile and the fragility is structural.** The median bus factor of 2 means most civic-tech projects are one or two developer departures from critical risk; 46% sit at bus factor 1. The negative correlation between bus factor and HHI (ρ = −0.920, partial −0.872) is the strongest non-trivial signal in the dataset and survives all controls. The fragility is not a small-project artefact: it persists at flagship scale, and the partial-correlation analysis identifies it as a structural relationship between number of key contributors and organisational concentration rather than a downstream consequence of team size.

**Effort-based measurement reveals concentration that commit counts hide.** The systematic positive gap between line-Gini and commit-Gini (Δ = +0.057, positive in 33/37 repositories) means that research using commit counts as a proxy for contribution weight systematically under-estimates concentration. The mega-commit regime at flagship scale (line-Gini ≥ 0.94 while commit-Gini stays at 0.76) further indicates that, at scale, large refactor or batch-merge commits dominate effort even when commit counts look balanced. We argue that CHAOSS-aligned health frameworks should incorporate effort-resolved metrics alongside count-based ones.

**Bot filtering matters — selectively.** Bots significantly inflate HHI (Wilcoxon p = 7 × 10⁻⁶) but do not materially affect bus factor (p = 1.00) or elephant factor (no change). We recommend bot filtering as standard practice when computing HHI; bus-factor analyses can safely include them.

**Project size confounds many apparent relationships.** Five of ten key correlations are entirely explained by team size. Bivariate correlations between health metrics, reported without size controls, risk overstating the strength of structural relationships. Partial correlations should be reported alongside zero-order correlations in multi-metric OSS health studies.

**Measurement-coverage bias is a systemic risk in small-sample OSS health research.** The attenuation of the burstiness ↔ stale-issue correlation from ρ = 0.685 (pilot phase) to ρ = 0.444 (corrected panel) reflects non-random missingness on the original burstiness measurement: GitHub's `/stats/*` endpoints time out preferentially on repositories whose async builds are not pre-cached, and pre-caching correlates with project activity. The same pattern can affect any study that depends on aggregate endpoints whose computation budgets are exhausted by uncached repositories. We recommend three practices: report coverage per metric, document the missingness mechanism, and triangulate from independent sources where possible (in our case, GraphQL bulk fetches yield the same per-week commit data without the async-build timeout).

---

## 6. Threats to Validity

**Construct validity.** The bus factor captures commit-based contributions and may undervalue contributors who primarily review code, manage issues, or write documentation. The HHI depends on organisational affiliation data, which is often incomplete on GitHub. We mitigate via three-tier HHI reporting and via the effort-Gini analysis (§4.7), which captures contribution weight via lines-changed.

**Internal validity.** Bot detection uses heuristic pattern matching, which may miss bots that do not follow standard naming conventions or misclassify human accounts with "bot" in their names; manual inspection confirmed > 95% accuracy on this dataset.

**External validity.** The 37-repository sample is purposive, not random, and may not generalise to all civic-tech projects, particularly self-hosted or non-GitHub projects. The civic-tech definition we apply emphasises explicit public-interest design intent rather than incidental public-interest use; broader definitions would change sample composition.

**Statistical validity.** With n = 37, statistical power is limited for detecting small effects. We mitigate via effect-size reporting alongside p-values, FDR correction for multiple testing, non-parametric methods, and partial correlations. Borderline findings are flagged as such.

**Measurement-coverage validity.** §4.4.1 documents how the pilot phase of this study was affected by non-random missingness on burstiness. We have addressed this for burstiness (coverage now 37/37) but cannot rule out similar issues for other metrics. Coverage per metric in this paper: `burstiness_cv` 37/37; `stale_issue_ratio` 26/37; `median_time_to_first_response_issues_hours` 24/37; `median_pr_review_turnaround_hours` 29/37; `network_density` 29/37. The 178,099 vs 162,033 commit-count discrepancy between `repo_metrics.total_commits` and the sum of `contributor_weekly_activity.commits` (9% overall, concentrated in one repository) reflects different attribution mechanisms; we use GraphQL-derived counts where contributor attribution matters. One repository hit the 5,000-issue cap; its aggregated time-to-close metrics are right-censored.

---

## 7. Conclusions and Longer-Term Plan

This paper presented emerging results from a multi-dimensional study of 37 civic-tech repositories. The framework, toolchain, and dataset are open-source; the n=37 sample reveals a civic-tech landscape characterised by structural fragility (median bus factor 2; 46% at bus factor 1; effort concentration of 83% single-contributor weeks; median full-history line-Gini 0.70), with structural concentration mechanisms (bus factor ↔ HHI, partial ρ = −0.872) that persist after controlling for project size. A methodological discovery made mid-study documents how measurement-coverage bias in GitHub's `/stats/*` endpoints inflated a pilot-phase correlation from a corrected ρ = 0.444 to an apparent ρ = 0.685 — real but moderate rather than headline-strong, and a cautionary case study for small-sample OSS health research.

The work is in progress along three axes.

**(L1) Longitudinal tracking.** All metrics reported here are snapshots at a single collection date. A longitudinal extension is underway: we plan quarterly recrawls of the 37-repository panel over a 24-month horizon and will report change-over-time analyses, contributor-lifecycle cohort effects, and event-study designs around governance changes (sponsor changes, license relicensing, foundation transitions).

**(L2) Replication and extension.** We plan to extend the sample to non-GitHub hosts (GitLab, Codeberg, self-hosted Gitea) and to a larger civic-tech population (target n ≥ 100), enabling more powerful tests of contextual hypotheses (cross-organisation effects, language/stack effects) that the current n=37 sample can only detect when effect sizes are large.

**(L3) Intervention design.** The partial-correlation findings — particularly the robust bus-factor ↔ HHI relationship and the robust CR-acceptance ↔ PR-turnaround relationship — identify candidate intervention points. We are scoping a co-design study with two civic-tech maintainer organisations to evaluate whether onboarding programmes that reduce HHI also raise bus factor, and whether review-turnaround improvements raise acceptance ratios independently of size.

Finally, we offer the measurement-coverage self-correction as a cautionary case study. Future open-source health studies that depend on aggregate `/stats/*` endpoints should report coverage per metric, document missingness mechanisms, and triangulate from independent sources where possible. The corresponding crawler resilience improvements (§3.4) make this practical at no significant cost.

---

## Data Availability

In accordance with ESEM 2026's open-science policy, all artefacts supporting the claims in this paper will be deposited in **Zenodo** under a CC-BY 4.0 (data) / MIT (code) licence and assigned a DOI. For the duration of double-anonymous review the deposit is mirrored at an anonymous URL at [anonymous-url-redacted-for-double-blind-review]; the persistent Zenodo DOI will be substituted in the camera-ready version.

The deposit contains:

- The Python CLI toolchain (`src/civic_tech_crawler/`), including the resilience features documented in §3.4 (exponential-backoff retry on async `/stats/*` endpoints, warm-up pre-pass, GraphQL in-collector fallback, auto-respawn under external SIGKILL).
- The canonical May 2026 results snapshot (`example_results/may_2026/`): `repo_metrics.csv`, `person_metrics.csv`, `chaoss_summary.csv`, `contributor_weekly_activity.csv` (22,486 rows), `weekly_snapshots.csv`, `issue_summary.csv`, `pull_requests.csv`, `tags.csv`, `cross_project_overlap.csv`, `temporal_summary.csv`, `core_periphery.csv`, plus per-repository directories with raw API responses.
- All analysis scripts under `scripts/`, including `scripts/paper_figures.py` (regenerates Figures 1–3 and Figure 5 deterministically from the snapshot) and `scripts/recompute_burstiness.py` (the GraphQL-derived burstiness recompute used in §4.4.1).
- A `per_repo_findings.md` with per-repository commentary and an `analysis_n37.md` documenting the statistical pipeline that produced every numerical claim in this paper.

The deposit is pinned to a versioned snapshot corresponding to this submission so that every reported figure can be reproduced from the same inputs.

---

## References

[1] Avelino, G., Passos, L., Hora, A., & Valente, M. T. (2016). A novel approach for estimating truck factors. In *Proc. 24th IEEE Int. Conf. on Program Comprehension (ICPC)*, pp. 1–10.

[2] Dey, T., Mousavi, S., Ponce, E., Fry, T., Vasilescu, B., Filippova, A., & Mockus, A. (2020). Detecting and characterizing bots that commit code. In *Proc. 17th Int. Conf. on Mining Software Repositories (MSR)*, pp. 209–219.

[3] Coelho, J., & Valente, M. T. (2017). Why modern open source projects fail. In *Proc. ESEC/FSE*, pp. 186–196.

[4] Eghbal, N. (2020). *Working in Public: The Making and Maintenance of Open Source Software*. Stripe Press.

[5] Forsgren, N., Humble, J., & Kim, G. (2018). *Accelerate: The Science of Lean Software and DevOps*. IT Revolution Press.

[6] Forsgren, N., Storey, M.-A., Maddila, C., Zimmermann, T., Houck, B., & Butler, J. (2021). The SPACE of developer productivity. *Communications of the ACM*, 64(6), 46–53.

[7] Golzadeh, M., Decan, A., Legay, D., & Mens, T. (2021). A ground-truth dataset and classification model for detecting bots in GitHub issue and PR comments. *Journal of Systems and Software*, 175, 110911.

[8] Goggins, S. P., Lumbard, K., & Germonprez, M. (2021). Open source community health: Analytical metrics and their corresponding narratives. In *Proc. IEEE/ACM 4th SoHeal Workshop*, pp. 25–32.

[9] McNutt, J. G., Justice, J. B., Melitski, J. M., Ahn, M. J., Siddiqui, S. R., Carter, D. T., & Kline, A. D. (2016). The diffusion of civic technology and open government in the United States. *Information Polity*, 21(2), 153–170.

[10] Pinto, G., Steinmacher, I., & Gerosa, M. A. (2016). More common than you think: An in-depth study of casual contributors. In *Proc. IEEE 23rd Int. Conf. on Software Analysis, Evolution, and Reengineering (SANER)*, pp. 112–123.

[11] Patel, M., Sotsky, J., Gourley, S., & Houghton, D. (2013). *The Emergence of Civic Tech: Investments in a Growing Field*. Knight Foundation.

[12] Romano, J., Kromrey, J. D., Coraggio, J., & Skowronek, J. (2006). Appropriate statistics for ordinal level data. In *Annual Meeting of the Florida Association of Institutional Research*, pp. 1–33.
