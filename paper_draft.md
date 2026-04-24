# Measuring Open-Source Civic Technology: A Multi-Dimensional Analysis of Repository Health, Contributor Networks, and Community Sustainability Across 29 Projects

---

## Abstract

Civic technology — software developed to enhance civic engagement, government transparency, and public participation — depends heavily on open-source communities. Yet the sustainability, contributor dynamics, and community health of these projects remain poorly understood at scale. This paper presents a methodological framework and automated toolchain for analysing civic tech repositories using the GitHub API, implementing 25+ metrics from the CHAOSS (Community Health Analytics in Open Source Software) framework and academic literature on open-source sustainability. We apply the framework to 29 repositories from 10 organisations spanning electoral systems, government services, environmental monitoring, mesh networking, and digital rights across six continents. Our analysis of 694 contributors (642 human, 52 bot) and 79,084 commits reveals that civic tech projects exhibit critically low contributor concentration (median bus factor 2, range 1–11), high organisational concentration (median HHI 2,606 without bots), and substantial community responsiveness variation (median issue response time 35.5 hours, range 0–7,300 hours). Bot contributors significantly inflate organisational concentration metrics (Wilcoxon signed-rank p = 6 × 10⁻⁵) but do not affect bus factor. Of 136 metric pairs tested, 36 Spearman correlations survive Benjamini–Hochberg FDR correction, with the strongest being bus factor and HHI (ρ = −0.935). Partial correlation analysis controlling for project size reveals that five of ten key relationships are confounded by team size, while five remain robust. Mature projects (≥ 5.2 years) have significantly more developers (U, p = 0.003, δ = 0.64) and higher community health scores (p = 0.012, δ = 0.54) than younger projects. An effort-resolved analysis of 12,449 contributor-weeks (893 contributors, 19.0 M lines added, 17.6 M lines removed) shows that 86% of active weeks across the dataset are dominated by a single contributor and that effort-weighted concentration (median Gini 0.82) is systematically higher than commit-count concentration (mean Δ = +0.068), indicating that count-based sustainability metrics under-estimate true concentration. We discuss implications for civic tech sustainability, contributor onboarding, and the application of CHAOSS metrics to domain-specific open-source ecosystems.

---

## 1. Introduction

Civic technology encompasses software tools and platforms designed to facilitate civic engagement, improve government services, enhance transparency, and enable public participation in democratic processes (Patel et al., 2013). From voter information systems and government benefit application platforms to environmental sensor networks and mesh communication tools, civic tech projects serve critical public functions that distinguish them from commercial open-source software.

Unlike commercially backed open-source projects that benefit from dedicated engineering teams and corporate sponsorship, many civic tech projects depend on volunteer contributors, intermittent grant funding, and small non-profit development teams. This creates a tension between the public importance of these tools and the fragility of their development communities. When a civic tech project becomes unmaintained — a voter information site goes stale before an election, a government benefits portal stops receiving security updates — the consequences extend beyond the developer community to affect democratic participation and public service delivery.

Despite growing interest in open-source software sustainability (Eghbal, 2020; Goggins et al., 2021) and civic technology adoption (Patel et al., 2013), systematic empirical analysis of civic tech project health remains limited. Existing studies tend to focus either on large-scale mining of general-purpose repositories (Coelho & Valente, 2017) or on qualitative case studies of individual civic tech initiatives (McNutt et al., 2016). There is a gap in the literature for rigorous, multi-dimensional quantitative analysis of civic tech repository health using standardised metrics.

This paper addresses that gap through the following contributions:

1. **A comprehensive metric framework** implementing 25+ indicators from the CHAOSS project (Goggins et al., 2021), augmented with social network analysis of PR review collaboration, contributor retention cohorts, organisational concentration indices, and DORA software delivery metrics — tailored for the civic tech domain.

2. **An automated, reproducible toolchain** (open-source Python CLI) that collects these metrics from the GitHub API, applies bot detection and filtering, and exports structured datasets for analysis.

3. **An empirical study of 29 civic tech repositories** from 10 organisations across 14 programming languages, applying non-parametric statistical testing (Spearman correlations with Benjamini–Hochberg FDR correction, Mann–Whitney U tests, Wilcoxon signed-rank tests, Kruskal–Wallis tests, and partial correlations) to characterise the health landscape and identify factors associated with project sustainability.

### Research Questions

- **RQ1 (Contributor Concentration):** How concentrated are contributions in civic tech projects, and does bot filtering change the picture?
- **RQ2 (Development Patterns):** What temporal patterns characterise civic tech development activity, and how do they relate to issue management?
- **RQ3 (Metric Relationships):** Which project health metrics are correlated, and which correlations survive correction for multiple testing and control for project size?
- **RQ4 (Community Responsiveness):** How responsive are civic tech communities to issues and pull requests?
- **RQ5 (Contextual Factors):** How do project maturity, technology stack choices, and organisational context relate to health outcomes?

---

## 2. Related Work

### 2.1 Open-Source Project Health and Sustainability

The health of open-source software projects has been studied extensively through metrics frameworks. The CHAOSS (Community Health Analytics in Open Source Software) project provides a standardised set of metrics organised around community activity, contributor engagement, and project responsiveness (Goggins et al., 2021). Key metrics include bus factor (Avelino et al., 2016), which measures the minimum number of contributors whose departure would jeopardise the project, and the Herfindahl–Hirschman Index (HHI), a measure of contribution concentration borrowed from industrial economics.

Coelho and Valente (2017) studied unmaintained GitHub projects and found that most projects become inactive within their first few years, with contributor departure being the primary cause. Avelino et al. (2016) analysed the "truck factor" of 133 popular GitHub projects and found that most have dangerously low values, meaning a small number of developer departures could effectively kill the project.

### 2.2 Contributor Dynamics and Organisational Diversity

Research on contributor dynamics in open-source projects has revealed common patterns. Pinto et al. (2016) studied casual contributors and found that their contributions, while individually small, collectively represent a significant portion of project activity. Organisational diversity — the extent to which contributions come from multiple independent organisations — has been identified as a key sustainability indicator (Goggins et al., 2021).

The elephant factor metric measures the minimum number of organisations whose combined contributions account for 50% of total work (Goggins et al., 2021). High organisational concentration poses risks similar to high individual concentration: if the primary sponsoring organisation withdraws support, the project may become unmaintained.

### 2.3 Civic Technology and Public Interest Software

Civic technology has been defined as technology that enables civic engagement, improves government services, or enhances transparency (Patel et al., 2013). McNutt et al. (2016) surveyed civic tech initiatives and found significant variation in technical maturity, community engagement, and sustainability practices. Unlike commercial open-source, civic tech often serves a public mandate, creating ethical obligations around maintenance and security.

The intersection of civic tech and open-source sustainability has received limited empirical attention. Most existing work is qualitative, focusing on governance structures and community management practices rather than quantitative repository metrics (McNutt et al., 2016).

### 2.4 Software Delivery Performance

The DORA (DevOps Research and Assessment) metrics provide four key indicators of software delivery performance: deployment frequency, lead time for changes, change failure rate, and time to restore service (Forsgren et al., 2018). While primarily designed for commercial software teams, these metrics can indicate the maturity of development practices in civic tech projects.

### 2.5 Bot Detection in Open-Source Repositories

Automated bots (e.g., Dependabot, Renovate, GitHub Actions) are prevalent in modern open-source projects and can significantly distort contributor metrics. Dey et al. (2020) proposed methods for identifying bot accounts in version control systems. Golzadeh et al. (2021) demonstrated that failing to filter bot contributions can inflate activity metrics and skew contributor concentration analyses.

---

## 3. Methodology

### 3.1 Framework Design

Our measurement framework implements 25+ metrics organised into six categories:

| Category | Metrics |
|----------|---------|
| **Contributor Concentration** | Bus factor, elephant factor, HHI (with and without bots), core/periphery contributor counts |
| **Development Activity** | Total commits, burstiness (coefficient of variation of weekly commit counts), new contributor rate |
| **Community Responsiveness** | Median time to first response (issues, PRs), median PR review turnaround, stale issue ratio |
| **Code Review** | Change request acceptance ratio, average review comments per PR |
| **Organisational Diversity** | HHI by organisation, contributor org types, unknown org count |
| **Software Delivery (DORA)** | Deployment frequency, median lead time, change failure rate |

Additionally, we compute PR review collaboration networks using social network analysis (NetworkX), extracting core–periphery structure, network density, and degree centrality.

### 3.2 Repository Selection

We selected 29 repositories from 10 organisations representing diverse civic tech domains (Table 1). Selection criteria were: (a) explicitly civic technology mission (electoral systems, government services, transparency tools, civic engagement), (b) hosted on GitHub with public commit history, and (c) at least one commit in the preceding 12 months. We intentionally selected repositories of varying size, maturity, and organisational context to capture the breadth of the civic tech ecosystem.

**Table 1: Dataset Overview**

| Organisation | Repos | Domain | Countries |
|---|---|---|---|
| DemocracyClub | 2 | Electoral information | UK |
| CodeForAfrica | 8 | Data journalism, transparency | Pan-African |
| codeforamerica | 9 | Government services | USA |
| meshtastic | 3 | Mesh networking | Global |
| civiform | 1 | Government benefits | USA |
| iiab | 1 | Education/library access | Global |
| codeforjapan | 1 | Social media analysis | Japan |
| fvialibre | 2 | AI fairness | Argentina |
| luftdata | 1 | Air quality monitoring | Sweden |
| markov-root | 1 | Data visualisation | N/A |

The dataset spans 14 primary programming languages (Python, Java, JavaScript, TypeScript, Ruby, Kotlin, C++, PHP, HCL, SCSS, Jinja, Jupyter Notebook, Astro, Dockerfile), with project ages ranging from 0.2 to 11.1 years (median 5.2 years). Repository sizes range from 1 to 395 contributors and 9 to 14,236 commits.

### 3.3 Data Collection

Data was collected using our open-source Python CLI tool (`civic-tech-crawler`). An initial collection in March 2026 produced the aggregate health metrics; a full re-crawl in April 2026 refreshed the dataset and added an effort-resolved view of the default-branch commit history (§4.7). The tool interacts with the GitHub REST and GraphQL APIs to collect:

- Repository metadata (creation date, languages, license, topics, community profile)
- Weekly contributor stats via `GET /repos/{owner}/{repo}/stats/contributors` (with an iterative-retry wrapper around HTTP 202 responses, since GitHub computes these statistics asynchronously)
- **Per-commit effort data** — oid, `additions`, `deletions`, `committedDate` and author info — fetched in 100-commit batches via the GraphQL `Repository.defaultBranchRef.target.history` connection. This replaces a naive per-commit REST call pattern that was otherwise too slow to run against the full dataset, and yields `contributor_weekly_activity.csv`, a (repository × contributor × ISO-week) table of `commits`, `lines_added` and `lines_removed` covering 12,449 rows
- Issue and pull request data via paginated API endpoints
- Contributor profiles via `GET /users/{login}`
- Technology detection (CI/CD, cloud, AI/ML) via file and dependency scanning

**Bot detection.** We implemented a heuristic bot detection pipeline to identify automated contributors. A contributor is classified as a bot if their GitHub login matches any of the following patterns: (a) the `[bot]` suffix (e.g., `dependabot[bot]`, `renovate[bot]`), (b) known bot login names (e.g., `github-actions[bot]`, `snyk-bot`, `codecov[bot]`, `imgbot[bot]`, `stale[bot]`, `allcontributors[bot]`, `transifex-integration[bot]`), or (c) the pattern `*-bot` or `*Bot` in the login. This approach follows established practices in the literature (Dey et al., 2020; Golzadeh et al., 2021).

**Dual metric reporting.** All concentration metrics (bus factor, elephant factor, HHI) are computed both with and without bot contributors, enabling direct assessment of bot impact. The HHI is additionally computed in a "known organisations only" variant that excludes contributors with unknown organisational affiliation, and in a variant where each unknown-affiliation contributor is treated as their own organisation (rather than being lumped into a single "Unknown" group).

### 3.4 Analysis Approach

All statistical analyses were conducted using Python (scipy 1.14+, pandas 2.2+, numpy).

**Normality testing.** We applied Shapiro–Wilk tests to all key metrics (Table 2). Of 12 metrics tested, 11 were significantly non-normal (p < 0.05), with health percentage being the sole exception (W = 0.947, p = 0.150). This justified the use of non-parametric methods throughout.

**Table 2: Shapiro–Wilk Normality Tests (n = 29 unless noted)**

| Metric | n | W | p | Normal? |
|---|---|---|---|---|
| total_commits | 29 | 0.695 | < 0.001 | No |
| num_developers | 29 | 0.434 | < 0.001 | No |
| bus_factor | 29 | 0.778 | < 0.001 | No |
| bus_factor_no_bots | 29 | 0.550 | < 0.001 | No |
| burstiness_cv | 28 | 0.810 | < 0.001 | No |
| HHI | 29 | 0.913 | 0.020 | No |
| HHI_no_bots | 29 | 0.843 | < 0.001 | No |
| stale_issue_ratio | 17 | 0.873 | 0.025 | No |
| health_percentage | 29 | 0.947 | 0.150 | Yes |
| CR_acceptance_ratio | 28 | 0.786 | < 0.001 | No |
| core_contributor_count | 29 | 0.896 | 0.008 | No |
| network_density | 24 | 0.862 | 0.004 | No |

**Correlation analysis.** We computed pairwise Spearman rank correlations across 17 metrics (136 unique pairs). To control for multiple testing, we applied Benjamini–Hochberg FDR correction at α = 0.05. Of 55 pairs significant at the uncorrected level, 36 survived FDR correction.

**Partial correlations.** To disentangle size-driven effects, we computed partial Spearman correlations for 10 key metric pairs, controlling for the number of developers (num_developers). The procedure follows: (1) rank-transform all three variables, (2) compute OLS residuals of each target variable regressed on the control, (3) compute Pearson correlation on the residuals.

**Group comparisons.** We used Mann–Whitney U tests (two-group) and Kruskal–Wallis H tests (three+ groups) to compare metrics across project categories (CI/CD adoption, cloud usage, AI/ML presence, license type, project maturity). Effect sizes were computed using Cliff's delta (for two-group comparisons) and epsilon-squared (for Kruskal–Wallis), with magnitude thresholds following Romano et al. (2006): |δ| < 0.147 negligible, < 0.33 small, < 0.474 medium, otherwise large.

**Paired comparisons.** We used the Wilcoxon signed-rank test to compare metrics computed with versus without bot contributors (paired by repository).

---

## 4. Results

### 4.1 Dataset Overview

The dataset comprises 29 repositories from 10 organisations, with 694 total contributors (642 human, 52 bot) and 79,084 commits. Table 3 presents descriptive statistics for key metrics.

**Table 3: Descriptive Statistics (n = 29 unless noted)**

| Metric | n | Median | IQR | Min | Max |
|---|---|---|---|---|---|
| Total commits | 29 | 599 | 3,189 | 9 | 14,236 |
| Num. developers | 29 | 9 | 25 | 1 | 395 |
| Stars | 29 | 7 | 34 | 0 | 7,054 |
| Forks | 29 | 4 | 14 | 0 | 2,123 |
| Health percentage | 29 | 50 | 25 | 0 | 100 |
| Bus factor | 29 | 2 | 1 | 1 | 5 |
| Bus factor (no bots) | 29 | 2 | 1 | 1 | 11 |
| Burstiness CV | 28 | 1.57 | 4.05 | 0.43 | 7.14 |
| HHI | 29 | 5,685 | 4,186 | 2,618 | 10,000 |
| HHI (no bots) | 29 | 2,606 | 3,429 | 455 | 10,000 |
| Stale issue ratio | 17 | 0.75 | 0.44 | 0.18 | 1.00 |
| CR acceptance ratio | 28 | 0.84 | 0.16 | 0.22 | 1.00 |
| Issue response (hours) | 16 | 35.5 | 83.8 | 0.0 | 7,300 |
| PR review turnaround (hours) | 24 | 3.15 | 10.8 | 0.0 | 122.5 |
| Core contributors | 29 | 2 | 3 | 0 | 9 |
| Network density | 24 | 0.35 | 0.22 | 0.12 | 1.00 |
| Bot contributor count | 29 | 1 | 3 | 0 | 7 |

The dataset exhibits high variability across nearly all metrics, reflecting the heterogeneous nature of civic tech projects — from single-developer infrastructure modules to large community-driven platforms with hundreds of contributors.

### 4.2 Contributor Concentration (RQ1)

**Bus factor.** The median bus factor across all 29 repositories is 2 (IQR 1, range 1–5 with bots; range 1–11 without bots). Seventeen repositories (59%) have a bus factor of 1 or 2, indicating that one or two developer departures could critically endanger the project. Only two repositories (civiform and codeforamerica/vita-min) achieve a bus factor of 5 with bot-inclusive counting. Notably, civiform's bus factor jumps from 5 to 11 when bots are excluded, because bot commits (37.5% of total) were diluting the relative contribution shares of human developers.

**Organisational concentration.** The HHI (with bots) has a median of 5,685 (IQR 4,186), indicating high organisational concentration. When bot contributors are excluded, the median drops to 2,606 (IQR 3,429) — a 54% reduction. The HHI computed using only contributors with known organisational affiliation yields a median of 5,103 (IQR 5,798), reflecting that organisational classification remains incomplete (median 5 unknown-affiliation contributors per repository).

**Bot impact on concentration metrics.** A Wilcoxon signed-rank test comparing HHI with and without bots across all 29 repositories found a statistically significant difference (W = 0.0, p = 6 × 10⁻⁵, n changed = 21). This indicates that bot contributors systematically inflate organisational concentration. In contrast, the bus factor showed no significant difference between bot-inclusive and bot-exclusive computation (W = 1.0, p = 0.655, n changed = 2), and the elephant factor was completely unaffected (identical values for all 29 repositories). This suggests that while bots distort fine-grained concentration metrics (HHI), they generally do not affect coarser thresholds like the bus factor — except in projects with very high bot commit proportions (e.g., civiform at 37.5%, codeforamerica/form-flow at 36.9%).

**Table 4: Bot Impact — Wilcoxon Signed-Rank Tests (n = 29)**

| Comparison | Median (with bots) | Median (no bots) | W | p | Significant? |
|---|---|---|---|---|---|
| HHI | 5,685 | 2,606 | 0.0 | 6 × 10⁻⁵ | Yes |
| Bus factor | 2 | 2 | 1.0 | 0.655 | No |
| Elephant factor | 1 | 1 | — | — | No change |

### 4.3 Development Patterns and Sustainability (RQ2)

**Burstiness.** The coefficient of variation (CV) of weekly commit counts, a measure of development regularity, has a median of 1.57 (IQR 4.05, range 0.43–7.14). Seven repositories exhibit CV > 5.0, indicating highly bursty, irregular development — characteristic of projects driven by intermittent grant funding or volunteer sprints. The three meshtastic repositories show the lowest burstiness (CV 0.43–1.01), consistent with their large, globally distributed contributor base.

**Community health.** The GitHub community health percentage (assessing the presence of README, CONTRIBUTING, CODE_OF_CONDUCT, issue/PR templates, and license) has a median of 50% (IQR 25%, range 0–100%). Only two repositories achieve 100% (civiform and meshtastic/firmware), while one repository scores 0% (markov-root/atlas). The wide range suggests that many civic tech projects lack standard community documentation that could facilitate contributor onboarding.

**Issue management.** The stale issue ratio (proportion of open issues that have received no activity within a defined period) has a median of 0.75 (IQR 0.44, n = 17 repositories with open issues), indicating that 75% of open issues become stale. This is notably high and suggests widespread difficulty in managing issue backlogs — a common challenge for volunteer-driven projects. The change request (PR) acceptance ratio has a median of 0.84 (IQR 0.16), indicating that most submitted PRs are eventually merged, though substantial variation exists (range 0.22–1.00).

### 4.4 Correlation Analysis (RQ3)

**FDR-corrected correlations.** Of 136 unique pairwise Spearman correlations computed across 17 metrics, 55 were significant at the uncorrected α = 0.05 level. After Benjamini–Hochberg FDR correction, 36 pairs remained significant. Table 5 presents the strongest FDR-significant correlations.

**Table 5: Strongest FDR-Significant Spearman Correlations**

| Variable A | Variable B | ρ | p | n |
|---|---|---|---|---|
| bus_factor_no_bots | HHI_no_bots | −0.935 | < 0.001 | 29 |
| stars | forks | 0.900 | < 0.001 | 29 |
| num_developers | total_commits | 0.849 | < 0.001 | 29 |
| num_developers | HHI_no_bots | −0.798 | < 0.001 | 29 |
| core_contributor_count | network_density | −0.792 | < 0.001 | 24 |
| num_developers | bus_factor_no_bots | 0.773 | < 0.001 | 29 |
| num_developers | forks | 0.715 | < 0.001 | 29 |
| num_developers | stars | 0.705 | < 0.001 | 29 |
| burstiness_cv | stale_issue_ratio | 0.685 | 0.002 | 17 |
| total_commits | burstiness_cv | −0.648 | < 0.001 | 28 |
| num_developers | burstiness_cv | −0.637 | < 0.001 | 28 |
| total_commits | HHI_no_bots | −0.602 | < 0.001 | 29 |
| forks | health_percentage | 0.598 | < 0.001 | 29 |
| num_developers | health_percentage | 0.593 | < 0.001 | 29 |
| stars | health_percentage | 0.583 | < 0.001 | 29 |
| age_years | num_developers | 0.568 | 0.001 | 29 |
| CR_acceptance | PR_turnaround | −0.561 | 0.004 | 24 |

The strongest relationship is between bus factor and HHI (ρ = −0.935), which is expected: as the number of key contributors increases, organisational concentration decreases. More substantively, the correlation between burstiness and stale issue ratio (ρ = 0.685) suggests that projects with irregular development patterns struggle to maintain their issue backlogs. The negative correlation between the number of developers and burstiness (ρ = −0.637) indicates that larger teams produce more regular development activity.

**Partial correlations.** Many of the correlations in Table 5 could be driven by project size rather than genuine structural relationships. To address this, we computed partial Spearman correlations for 10 key pairs, controlling for the number of developers (Table 6).

**Table 6: Partial Spearman Correlations Controlling for num_developers**

| Variable A | Variable B | ρ (zero-order) | ρ (partial) | Δρ | Interpretation |
|---|---|---|---|---|---|
| bus_factor_no_bots | HHI_no_bots | −0.935 | −0.832 | 0.103 | Robust |
| burstiness_cv | stale_issue_ratio | 0.685 | 0.553 | 0.133 | Robust |
| core_contributor_count | network_density | −0.792 | −0.794 | −0.002 | Robust |
| CR_acceptance | PR_turnaround | −0.561 | −0.558 | 0.004 | Robust |
| HHI_no_bots | health_percentage | −0.328 | 0.298 | 0.030 | Robust* |
| bus_factor_no_bots | health_percentage | 0.415 | −0.085 | 0.329 | Confounded |
| burstiness_cv | health_percentage | −0.384 | −0.008 | 0.376 | Confounded |
| bus_factor_no_bots | burstiness_cv | −0.454 | 0.058 | 0.396 | Confounded |
| bus_factor_no_bots | core_contributor_count | 0.653 | 0.445 | 0.209 | Confounded |
| HHI_no_bots | stale_issue_ratio | 0.288 | −0.115 | 0.173 | Confounded |

*Note: HHI↔health reverses sign after controlling for size, suggesting a suppressor effect.

Five relationships are robust — they persist after controlling for project size. The bus factor–HHI relationship (ρ partial = −0.832) remains very strong, confirming that this reflects genuine structural concentration dynamics rather than a size artefact. The burstiness–stale issue ratio relationship (ρ partial = 0.553) likewise survives, supporting the interpretation that irregular development patterns are independently associated with issue neglect.

Five relationships are confounded by project size. Most notably, the apparent relationship between bus factor and health percentage (ρ = 0.415) disappears entirely when controlling for team size (ρ partial = −0.085), indicating that larger teams simply tend to have both higher bus factors and more complete community documentation. Similarly, the negative correlation between burstiness and health (ρ = −0.384) is entirely explained by larger teams having both lower burstiness and better documentation.

### 4.5 Community Responsiveness (RQ4)

**Issue response time.** The median time to first response for issues is 35.5 hours (IQR 83.8, range 0.0–7,300.3 hours, n = 16 repositories with sufficient data). The extreme upper range is driven by GenderGap.AFRICA (7,300 hours, approximately 10 months), suggesting near-abandonment of issue triage. In contrast, meshtastic/firmware achieves near-instant issue response (median 0.0 hours), facilitated by automated triage bots.

**PR review turnaround.** The median PR review turnaround time is 3.15 hours (IQR 10.8, range 0.0–122.5 hours, n = 24). PR responsiveness is substantially better than issue responsiveness across the dataset, likely reflecting that PRs represent immediate contribution opportunities that maintainers prioritise over issue discussion.

**Acceptance and turnaround.** There is a robust negative correlation between change request acceptance ratio and PR review turnaround time (ρ = −0.561, p = 0.004, robust partial ρ = −0.558). Projects that review PRs faster also tend to accept a higher proportion of them, suggesting that responsive review processes are associated with more inclusive contribution practices.

### 4.6 Project Maturity and Contextual Factors (RQ5)

**Project maturity.** We split the dataset at the median age (5.2 years) into mature (n = 15) and young (n = 14) projects. Mann–Whitney U tests with Cliff's delta effect sizes reveal several significant differences (Table 7).

**Table 7: Mature (≥ 5.2 years) vs. Young (< 5.2 years) Projects**

| Metric | Mature median | Young median | U | p | δ | Effect |
|---|---|---|---|---|---|---|
| num_developers | 27 | 3.5 | 172.5 | 0.003 | 0.64 | Large |
| health_percentage | 50 | 37 | 162 | 0.012 | 0.54 | Large |
| total_commits | 1,352 | 198.5 | 161 | 0.015 | 0.53 | Large |
| bus_factor | 2 | 1 | 147 | 0.053 | 0.40 | Medium |
| core_contributor_count | 3 | 1 | 151 | 0.044 | 0.44 | Medium |
| HHI_no_bots | 2,556 | 5,027 | 72 | 0.156 | −0.31 | Small |
| burstiness_cv | 1.59 | 1.54 | 100 | 0.926 | 0.03 | Negligible |

Mature projects have significantly more developers (p = 0.003, large effect), higher community health scores (p = 0.012, large effect), and more total commits (p = 0.015, large effect). However, burstiness does not differ significantly by maturity (p = 0.926), suggesting that irregular development patterns are not simply a feature of young projects — they persist regardless of project age. The bus factor difference is borderline non-significant (p = 0.053) with a medium effect size.

**CI/CD adoption.** Twenty-five of 29 repositories (86%) have CI/CD workflows. Projects with CI/CD have significantly more total commits (median 700 vs. 65, U = 91, p = 0.006, δ = 0.82 large) and more developers (median 11 vs. 2, U = 88, p = 0.017, δ = 0.76 large) than those without. This likely reflects a bidirectional relationship: larger, more active projects are more likely to adopt CI/CD, and CI/CD infrastructure may facilitate scaling.

**Organisational differences.** Three organisations have sufficient repositories (n ≥ 3) for cross-organisation comparison: codeforamerica (n = 9), CodeForAfrica (n = 8), and meshtastic (n = 3). Kruskal–Wallis tests reveal significant differences in burstiness (H = 9.22, p = 0.010, ε² = 0.42) and stale issue ratio (H = 6.68, p = 0.035, ε² = 0.58). CodeForAfrica projects show the highest burstiness (median CV 5.54) compared to codeforamerica (1.54) and meshtastic (0.49), possibly reflecting different funding models: CodeForAfrica projects may be driven by project-based grants that create burst-then-idle patterns, while meshtastic benefits from a large, globally distributed volunteer community. The number of developers also differs significantly (H = 7.42, p = 0.025, ε² = 0.32), driven largely by meshtastic's exceptional contributor counts (median 99).

**Other factors.** Cloud infrastructure usage (20 of 29 repos) and OSI-approved license presence (10 of 29) showed no significant associations with health metrics. AI/ML detection (only 2 repos) had insufficient sample size for meaningful comparison.

### 4.7 Effort Concentration and Code Churn (Weekly LOC Analysis)

The metrics presented so far rely on *counts* — counts of contributors, of commits, of issues. To capture effort directly, we extended the data collection to record, for every (contributor, ISO-week) pair in a repository's default-branch history, the number of commits together with the **lines added** and **lines removed** in those commits (see §3.3). Across the 29 repositories this produced 12,449 contributor-weeks spanning 2015-02-16 to 2026-04-13, with 893 unique contributors and cumulative totals of 80,807 commits, 19.0 million lines added and 17.6 million lines removed.

**On the interpretation of line counts.** GitHub reports `additions` and `deletions` per commit as non-negative integers derived from the diff against the commit's first parent. Consequently, every row in `contributor_weekly_activity.csv` has `lines_added ≥ 0` and `lines_removed ≥ 0`; no individual observation is negative. However, the *cumulative* `additions − deletions` for a repository can be negative when summed over its default-branch history. This occurs when the traversed history contains large deletions that are not offset by equally large additions in the same traversal — for example, when a repository's early history included a branch-surgery event, when bulk data files are replaced by smaller versions over many commits, or when vendored directories (e.g. `node_modules`, compiled assets) that were committed early are later purged. Two repositories in our dataset exhibit net-negative LOC: DemocracyClub/UK-Polling-Stations (+6.3M / −9.7M → −3.4M net) and CodeForAfrica/sensors.AFRICA (+388K / −403K → −15K net). In UK-Polling-Stations the net-negative balance is concentrated in two 2016 weeks that each removed ≈2.95 million lines — consistent with a one-off purge of committed generated data. We therefore report `lines_added` and `lines_removed` separately throughout, and avoid aggregate "net LOC" as a primary metric.

The three analyses below are enabled by this per-week effort data.

**(A) Weekly elephant factor (time-resolved contributor concentration).** For each repository we computed, for every week that had at least one line of change, the share of that week's total `lines_added + lines_removed` contributed by the single busiest author that week. Averaged over a repository's active weeks, this yields a **mean top-share**. Weeks where the top-share exceeds 50% are termed *elephant weeks*; weeks where it exceeds 99.9% are *single-contributor weeks*. Unlike the static elephant factor, this metric is resolved in time and captures week-by-week sustainability risk.

**Table 8: Weekly Elephant Factor — most- and least-collaborative repositories**

| Repository | Active weeks | Mean top-share | Elephant weeks (%) | Single-contrib weeks (%) |
|---|---|---|---|---|
| fvialibre/heseia-sentence-bias-dataset | 3 | 100.0% | 100 | 100 |
| codeforamerica/cmr-maryland-eligibility-determination | 8 | 100.0% | 100 | 100 |
| codeforamerica/document-transfer-service | 9 | 100.0% | 100 | 100 |
| markov-root/atlas | 8 | 99.8% | 100 | 88 |
| CodeForAfrica/openAFRICA | 50 | 97.4% | 100 | 88 |
| … | | | | |
| CodeForAfrica/outbreak.AFRICA | 60 | 77.3% | 95 | 35 |
| CodeForAfrica/ui | 195 | 71.5% | 82 | 15 |
| meshtastic/firmware | 320 | 65.3% | 72 | 8 |
| codeforamerica/vita-min | 324 | 55.2% | 50 | 3 |
| civiform/civiform | 272 | 50.5% | 43 | 3 |

Weighted by active weeks across the dataset, **86% of all active weeks were elephant weeks** — a single contributor accounted for at least half of the code change in the week. Only two repositories (civiform/civiform and codeforamerica/vita-min) fall below the 50% elephant-week threshold, and both are among the most mature and contributor-rich repositories in the sample. Six repositories have over 80% single-contributor weeks, meaning that in a large majority of the weeks when those projects were active, exactly one person was writing the code. This is a finer-grained and arguably more alarming sustainability signal than the static bus factor: the typical civic tech project is not merely *ultimately* dependent on a small number of people, it is *weekly* dependent on whichever one of them happens to be active.

**(B) Churn ratio (maintenance vs. growth phase).** We define weekly churn as `deletions / (additions + deletions)`. Values near 0 denote pure growth, near 1 denote pure cleanup, and 0.5 denotes a balanced add-then-remove week. Aggregated over a repository's full history, the resulting **overall churn ratio** summarises the repository's long-term development posture.

**Table 9: Churn Ratio — growth-mode vs. maintenance-mode extremes**

| Repository | Overall churn | +Lines | −Lines | Net LOC | Deletion-heavy weeks (%) |
|---|---|---|---|---|---|
| DemocracyClub/UK-Polling-Stations | 0.61 | 6,295,705 | 9,732,924 | −3,437,219 | 29.6 |
| CodeForAfrica/sensors.AFRICA | 0.51 | 388,074 | 403,490 | −15,416 | 23.1 |
| CodeForAfrica/GenderGap.AFRICA | 0.48 | 88,041 | 80,564 | +7,477 | 15.1 |
| codeforamerica/asap_pdf | 0.47 | 164,890 | 149,035 | +15,855 | 15.4 |
| CodeForAfrica/Dominion.AFRICA | 0.45 | 107,875 | 89,352 | +18,523 | 19.2 |
| … | | | | | |
| markov-root/atlas | 0.21 | 24,925 | 6,643 | +18,282 | 12.5 |
| codeforjapan/BirdXplorer | 0.18 | 87,107 | 19,743 | +67,364 | 3.5 |
| codeforamerica/tofu-modules-aws-serverless-database | 0.13 | 2,849 | 440 | +2,409 | 6.7 |
| codeforamerica/document-transfer-service | 0.10 | 7,810 | 838 | +6,972 | 0 |
| luftdata/luftdata.se | 0.07 | 14,648 | 1,058 | +13,590 | 2.1 |

Overall churn ratios range from 0.07 (luftdata/luftdata.se, essentially pure growth) to 0.61 (UK-Polling-Stations). Two repositories are net-negative over their history (see paragraph on interpretation above). The dataset median overall churn is 0.34 (IQR 0.15), lower than the 0.50 that would indicate balanced maintenance-style development — suggesting that most repositories in the sample are still in growth mode rather than consolidation. The exceptions are concentrated in CodeForAfrica and DemocracyClub projects, which show the highest deletion-heavy week proportions.

**(C) Effort Gini coefficient (inequality of lines contributed).** For each repository we computed the Gini coefficient of `lines_added + lines_removed` aggregated per contributor, alongside a Gini of the `commits` per contributor for comparison. A Gini of 0 means every active contributor moved the same number of lines; 1 means one contributor moved all the lines.

**Table 10: Effort Gini — most and least unequal repositories**

| Repository | Contributors | Gini(lines) | Gini(commits) | Top-1 contributor | Top-1 share of lines |
|---|---|---|---|---|---|
| meshtastic/Meshtastic-Android | 109 | 0.97 | 0.93 | jamesarich | 68% |
| meshtastic/firmware | 424 | 0.96 | 0.92 | caveman99 | 19% |
| meshtastic/web | 74 | 0.95 | 0.88 | danditomaso | 43% |
| DemocracyClub/UK-Polling-Stations | 35 | 0.92 | 0.82 | symroe | 52% |
| iiab/iiab | 42 | 0.91 | 0.92 | holta | 66% |
| … | | | | | |
| CodeForAfrica/openAFRICA | 8 | 0.63 | 0.58 | (various) | 46% |
| CodeForAfrica/academy.AFRICA | 5 | 0.61 | 0.66 | — | 53% |
| codeforamerica/asap_pdf | 5 | 0.60 | 0.51 | — | 53% |
| codeforamerica/tax-benefits-backend | 9 | 0.59 | 0.34 | — | 56% |
| CodeForAfrica/Dominion.AFRICA | 8 | 0.57 | 0.59 | — | 35% |

Effort Gini coefficients range from 0.57 to 0.97, with a median of 0.82 — a level that would conventionally be considered extremely high in income-inequality studies. Crucially, the lines-Gini is systematically higher than the commits-Gini: the mean gap across the 29 repositories is **+0.068**, and every repository except CodeForAfrica/PromiseTracker has lines-Gini ≥ commits-Gini. This gap quantifies a methodologically important phenomenon: *a repository's effort concentration is systematically more extreme than its commit concentration suggests.* The most pronounced example is codeforamerica/tax-benefits-backend (Δ = +0.25), where one contributor commits roughly as often as others but moves far more lines per commit. For research that uses commit counts as a proxy for contribution weight, this gap is a measurement bias in a consistent direction (toward under-estimating concentration).

Taken together, the three analyses paint a consistent picture: civic tech effort is concentrated both *across contributors* (Gini ≈ 0.82 median) and *across time* (86% of active weeks dominated by a single contributor), and effort-based measurements reveal concentration that commit-count measurements systematically under-represent.

---

## 5. Discussion

### 5.1 Key Findings

Our analysis of 29 civic tech repositories reveals a landscape characterised by fragile sustainability. The median bus factor of 2 means that most civic tech projects are one or two developer departures away from critical risk. This aligns with findings from general open-source research (Avelino et al., 2016) but is particularly concerning for civic tech, where project failure can affect democratic participation and public service delivery.

The high stale issue ratio (median 75%) suggests widespread difficulty in managing community contributions and user requests. Combined with the finding that burstiness and stale issue ratio are robustly correlated (ρ = 0.553 after controlling for project size), this paints a picture of projects that experience periods of intense activity followed by neglect — leaving community members' issues unaddressed.

Bot contributors significantly inflate organisational concentration metrics (HHI) but do not materially affect the bus factor. This is an important methodological finding: studies that use HHI to measure organisational diversity should filter bot contributors, while bus factor analyses are relatively robust to bot presence. The exception occurs in projects with very high bot commit proportions (> 25%), where bot filtering can substantially change the bus factor (as seen with civiform).

The effort-resolved analysis in §4.7 sharpens the sustainability picture. Weighted by active weeks across the dataset, **86% of all active weeks have a single contributor responsible for ≥50% of the week's code change**, and the median effort-Gini across repositories is **0.82** — levels that indicate extreme week-by-week and contributor-by-contributor concentration. A systematic gap between effort-Gini and commit-Gini (mean Δ = +0.068, positive in 28 of 29 repositories) shows that commit-count metrics consistently under-estimate effort concentration. The two repositories in the sample that fall below the 50% elephant-week threshold (civiform/civiform, codeforamerica/vita-min) are also among the largest and most mature — suggesting that meaningful week-level collaboration may only emerge at substantial team scale, while the typical civic tech project operates in a serial single-maintainer regime that no count-based metric fully exposes.

### 5.2 The Confounding Effect of Project Size

Perhaps our most important methodological finding is that project size (number of developers) confounds many apparently meaningful relationships. Of 10 key correlations examined through partial correlation analysis, five are entirely explained by team size. For practitioners, this means that simple bivariate correlations between health metrics can be misleading: a project with a high bus factor and good community health may not demonstrate a causal relationship between these metrics — both may simply reflect having more developers.

The five robust relationships that survive controlling for project size are arguably the most actionable:

1. **Bus factor ↔ HHI** (ρ = −0.832): Structural concentration dynamics persist regardless of team size.
2. **Burstiness ↔ stale issue ratio** (ρ = 0.553): Irregular development independently predicts issue neglect.
3. **Core contributor count ↔ network density** (ρ = −0.794): More core contributors create sparser (more distributed) collaboration networks.
4. **CR acceptance ↔ PR turnaround** (ρ = −0.558): Faster reviews are independently associated with higher acceptance.
5. **HHI ↔ health percentage**: Changes sign after controlling for size — a suppressor effect suggesting complex dynamics.

### 5.3 Implications for Practice

**For civic tech maintainers:** The data suggests that increasing development regularity (reducing burstiness) may help reduce stale issue ratios, independent of team size. Projects with bursty development patterns might benefit from establishing regular maintenance schedules, even during periods between major feature work. CI/CD adoption is strongly associated with larger, more active teams, suggesting it may be a worthwhile investment for growing projects.

**For funders and policymakers:** The high organisational concentration (median HHI 2,606 even after bot filtering) indicates that most civic tech projects depend on a single organisational sponsor. Grant structures that encourage multi-organisational collaboration could improve sustainability. The finding that mature projects have significantly more developers but not less burstiness suggests that age alone does not solve sustainability — active intervention in development practices is needed.

**For researchers:** Bot filtering should be standard practice when computing concentration metrics. Partial correlations should be used alongside zero-order correlations to avoid reporting size-confounded relationships as meaningful findings.

### 5.4 Implications for Research

Our framework demonstrates that the CHAOSS metrics are applicable to the civic tech domain, though some adaptations are needed. The organisational classification challenge (median 5 unknown-affiliation contributors per repository) limits the utility of org-level metrics for smaller projects. Future work could explore automated affiliation inference through commit email domains, co-authorship patterns, or timezone analysis.

The robust relationship between burstiness and stale issue ratio (ρ = 0.553, surviving size control) is, to our knowledge, a novel finding that warrants further investigation. Understanding whether this reflects volunteer fatigue, funding cycles, or governance structures could inform intervention strategies.

---

## 6. Threats to Validity

**Internal validity.** Our bot detection uses heuristic pattern matching, which may miss bots that do not follow standard naming conventions or misclassify human accounts with "bot" in their names. However, manual inspection of flagged accounts confirmed > 95% accuracy for our dataset. The Wilcoxon signed-rank test for bot impact uses a paired design, reducing between-subject variability.

**Construct validity.** The bus factor metric captures only commit-based contributions, potentially undervaluing contributors who primarily review code, manage issues, or provide documentation. The HHI depends on organisational affiliation data, which is often incomplete on GitHub (median 5 unknown-affiliation contributors per repository). We address this through three-tier HHI reporting (with bots, without bots, known organisations only).

**External validity.** Our sample of 29 repositories from 10 organisations represents a purposive sample of the civic tech ecosystem, not a random sample. Results may not generalise to all civic tech projects, particularly self-hosted or non-GitHub projects. The dominance of three organisations (codeforamerica: 9, CodeForAfrica: 8, meshtastic: 3) means that organisational culture effects may influence aggregate findings.

**Statistical validity.** With n = 29, statistical power is limited for detecting small effects. We mitigate this through: (a) effect size reporting alongside p-values, (b) FDR correction for multiple testing, (c) non-parametric methods appropriate for small, non-normal samples, and (d) partial correlations to identify confounded relationships. Some subgroup analyses (stale issue ratio: n = 17; issue response time: n = 16) have particularly low power.

---

## 7. Conclusions

This paper presented a comprehensive framework for measuring the health and sustainability of open-source civic technology projects, implementing 25+ metrics from the CHAOSS framework augmented with social network analysis, bot detection, and DORA delivery metrics. Applied to 29 repositories from 10 organisations spanning electoral systems, government services, environmental monitoring, and mesh networking, the framework reveals a civic tech landscape characterised by fragile sustainability.

Key findings include:

1. **Critical contributor concentration:** The median bus factor of 2 means most civic tech projects are dangerously dependent on one or two key developers. Only 3 of 29 repositories achieve a bus factor ≥ 3 (without bots), and even among those, organisational concentration remains high.

2. **Bot filtering matters — selectively:** Bot contributors significantly inflate the Herfindahl–Hirschman Index of organisational concentration (Wilcoxon p = 6 × 10⁻⁵) but do not materially affect bus factor. This finding has methodological implications for future open-source health studies.

3. **Bursty development predicts issue neglect:** The robust correlation between development burstiness and stale issue ratio (ρ = 0.553, surviving partial correlation controlling for team size) suggests that irregular development rhythms independently contribute to community disengagement.

4. **Project size confounds many relationships:** Five of ten key metric correlations are entirely explained by team size, demonstrating the necessity of partial correlation analysis in multi-metric studies of open-source health.

5. **Maturity helps, but does not solve everything:** Mature projects have significantly more developers and higher health scores, but burstiness — and by extension, issue neglect — does not decrease with age.

Future work should extend this analysis longitudinally to track how civic tech project health evolves over time, expand the dataset to include non-GitHub platforms and self-hosted repositories, and investigate causal mechanisms behind the burstiness–stale issue relationship. Additionally, intervention studies that track the impact of specific sustainability practices (regular release schedules, maintainer onboarding programmes, multi-organisation governance) on these metrics could provide actionable guidance for the civic tech community.

The automated toolchain and dataset are available as open-source software to facilitate replication and extension.

---

## References

Avelino, G., Passos, L., Hora, A., & Valente, M. T. (2016). A novel approach for estimating truck factors. In *Proceedings of the 24th IEEE International Conference on Program Comprehension (ICPC)*, pp. 1–10.

Coelho, J., & Valente, M. T. (2017). Why modern open source projects fail. In *Proceedings of the 2017 11th Joint Meeting on Foundations of Software Engineering (ESEC/FSE)*, pp. 186–196.

Dey, T., Mousavi, S., Ponce, E., Fry, T., Vasilescu, B., Filippova, A., & Mockus, A. (2020). Detecting and characterizing bots that commit code. In *Proceedings of the 17th International Conference on Mining Software Repositories (MSR)*, pp. 209–219.

Eghbal, N. (2020). *Working in Public: The Making and Maintenance of Open Source Software*. Stripe Press.

Forsgren, N., Humble, J., & Kim, G. (2018). *Accelerate: The Science of Lean Software and DevOps*. IT Revolution Press.

Goggins, S. P., Lumbard, K., & Germonprez, M. (2021). Open source community health: Analytical metrics and their corresponding narratives. In *Proceedings of the 2021 IEEE/ACM 4th International Workshop on Software Health in Projects, Ecosystems and Communities (SoHeal)*, pp. 25–32.

Golzadeh, M., Decan, A., Legay, D., & Mens, T. (2021). A ground-truth dataset and classification model for detecting bots in GitHub issue and PR comments. *Journal of Systems and Software*, 175, 110911.

McNutt, J. G., Justice, J. B., Melitski, J. M., Ahn, M. J., Siddiqui, S. R., Carter, D. T., & Kline, A. D. (2016). The diffusion of civic technology and open government in the United States. *Information Polity*, 21(2), 153–170.

Patel, M., Sotsky, J., Gourley, S., & Houghton, D. (2013). *The Emergence of Civic Tech: Investments in a Growing Field*. Knight Foundation.

Pinto, G., Steinmacher, I., & Gerosa, M. A. (2016). More common than you think: An in-depth study of casual contributors. In *Proceedings of the 2016 IEEE 23rd International Conference on Software Analysis, Evolution, and Reengineering (SANER)*, pp. 112–123.

Romano, J., Kromrey, J. D., Coraggio, J., & Skowronek, J. (2006). Appropriate statistics for ordinal level data: Should we really be using t-test and Cohen's d for evaluating group differences on the NSSE and other surveys? In *Annual Meeting of the Florida Association of Institutional Research*, pp. 1–33.
