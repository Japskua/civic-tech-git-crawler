# Measuring Open-Source Civic Technology: A Multi-Dimensional Analysis of Repository Health, Contributor Networks, and Community Sustainability

**[DRAFT — For internal review and feasibility assessment]**

---

## Abstract

Civic technology — software developed to enhance civic engagement, government transparency, and public participation — depends heavily on open-source communities. Yet the sustainability, contributor dynamics, and community health of these projects remain poorly understood at scale. This paper presents a methodological framework and automated toolchain for analysing civic tech repositories using the GitHub API, implementing metrics from the CHAOSS (Community Health Analytics in Open Source Software) framework alongside standard software engineering indicators. We apply the framework to a pilot dataset of three civic tech repositories spanning electoral information systems (DemocracyClub/UK-Polling-Stations, DemocracyClub/WhoCanIVoteFor) and AI fairness research (fvialibre/edia). Our pilot analysis reveals significant variation in contributor concentration (bus factor 1–2), development burstiness (CV 0.00–1.27), and community infrastructure maturity across projects of different ages and institutional backing. **[MOCKUP: The full study will expand to N=50–200 repositories across multiple civic tech categories and geographic regions.]** We discuss implications for civic tech sustainability, contributor onboarding, and the application of CHAOSS metrics to domain-specific open-source ecosystems.

**Keywords:** civic technology, open source, CHAOSS metrics, contributor networks, community health, GitHub mining, software sustainability

---

## 1. Introduction

### 1.1 Background

Civic technology encompasses a broad range of software tools developed to facilitate civic engagement, enhance government transparency, improve public service delivery, and strengthen democratic processes (Patel et al., 2013; Steinberg, 2019). **[MOCKUP: Full literature review to be expanded with 20–30 additional references.]** These projects range from voter information platforms and open data portals to participatory budgeting tools and civic AI applications.

Unlike commercial or enterprise open-source software, civic tech projects frequently operate under distinctive constraints: limited funding, reliance on volunteer contributors, electoral or legislative calendars that create cyclical demand spikes, and a user base that may lack technical expertise (Shaw, 2020). Understanding how these constraints manifest in development patterns, contributor behaviour, and project sustainability is critical for policy-makers, funders, and the civic tech community itself.

### 1.2 Research Gap

While the mining of software repositories (MSR) community has produced extensive work on open-source project health (e.g., Jergensen et al., 2011; Coelho & Valente, 2017), relatively few studies have focused specifically on the civic technology domain. Existing civic tech research tends to be qualitative, case-study-based, or focused on adoption rather than development dynamics (Peixoto & Fox, 2016). **[MOCKUP: Systematic literature search to confirm the exact extent of this gap.]**

The CHAOSS (Community Health Analytics in Open Source Software) project, a Linux Foundation initiative, has produced a comprehensive framework of implementation-agnostic metrics for assessing open-source community health (CHAOSS, 2023). However, the application of CHAOSS metrics to domain-specific ecosystems — particularly civic technology — remains largely unexplored.

### 1.3 Research Questions

This study addresses the following research questions:

- **RQ1:** What patterns of contributor concentration and code ownership characterise civic tech projects, and how do these patterns relate to project sustainability risk?
- **RQ2:** How do development activity patterns (burstiness, release frequency, commit cadence) vary across civic tech projects of different maturity levels and institutional contexts?
- **RQ3:** To what extent do civic tech projects adopt community health practices (contributing guidelines, governance documentation, newcomer-friendly labelling, codes of conduct)?
- **RQ4:** What is the relationship between technology choices (cloud infrastructure, AI/ML, CI/CD) and project maturity in the civic tech domain?

**[MOCKUP: RQ5 on contributor network analysis (cross-project contributors, organisational bridges) to be added when the full dataset supports network modelling.]**

### 1.4 Contributions

This paper makes three contributions:

1. **Methodological:** An open-source, reproducible toolchain for collecting multi-dimensional repository metrics from GitHub, implementing 12 CHAOSS metrics alongside standard software engineering indicators.
2. **Empirical:** A quantitative analysis of civic tech repository health across contributor dynamics, development patterns, community infrastructure, and technology adoption. **[MOCKUP: Pilot data only; full empirical contribution requires expanded dataset.]**
3. **Practical:** Actionable insights for civic tech project maintainers, funders, and contributors regarding sustainability risks and community health improvement opportunities.

---

## 2. Related Work

### 2.1 Open-Source Project Health

The concept of open-source project health has been studied through multiple lenses. Jansen (2014) proposed a health metaphor encompassing productivity, robustness, and niche creation. Crowston et al. (2006) identified coordination mechanisms in free/libre open-source software teams. More recently, Goggins et al. (2021) formalised community health indicators through the CHAOSS project.

The bus factor (or truck factor) — the minimum number of developers whose departure would halt a project — has been studied extensively as a sustainability indicator (Avelino et al., 2016; Ferreira et al., 2019). Cosentino et al. (2015) demonstrated that a significant proportion of GitHub projects have a bus factor of 1, indicating extreme contributor concentration.

**[MOCKUP: Expand with 15–20 additional references on: code review practices, PR acceptance patterns, release management, contributor onboarding, and newcomer-friendliness.]**

### 2.2 CHAOSS Metrics Framework

The CHAOSS project defines metrics across five working groups: Common, Diversity Equity & Inclusion, Evolution, Risk, and Value (CHAOSS, 2023). Key metrics relevant to this study include:

- **Contributor Absence Factor** (bus factor): Identifies project resilience to contributor loss.
- **Change Request Acceptance Ratio**: Measures the proportion of pull requests merged versus submitted.
- **Burstiness**: Quantifies variability in development activity patterns.
- **Organisational Diversity**: Measures the distribution of contributors across affiliations.
- **Defect Resolution Duration**: Tracks responsiveness to bug reports.
- **Release Frequency**: Measures how often a project ships stable versions.

While tools such as Augur (Goggins et al., 2021) and GrimoireLab (Dueñas et al., 2021) implement CHAOSS metrics at scale, they are designed for large-scale community analytics and require substantial infrastructure. Our toolchain provides a lightweight, researcher-friendly alternative for focused domain-specific studies.

### 2.3 Civic Technology Research

Civic technology research has primarily focused on adoption, participation, and democratic outcomes (Peixoto & Fox, 2016; Boehner & DiSalvo, 2016). Studies of civic tech *development* processes are scarcer. Steinberg (2019) examined the organisational structures of civic tech organisations but did not analyse repository-level metrics. McNutt et al. (2016) surveyed civic tech tools but focused on functionality rather than community health.

**[MOCKUP: Expand with literature on civic tech sustainability challenges, volunteer developer motivation, and the relationship between institutional backing and project longevity.]**

---

## 3. Methodology

### 3.1 Data Collection Framework

We developed an open-source Python tool, *Civic Tech Git Crawler*, that collects repository metrics from the GitHub REST API. The tool implements a five-stage pipeline for each repository:

1. **Repository Metrics:** Basic metadata (stars, forks, watchers, languages, license, creation date), community health indicators (contributing guidelines, code of conduct, governance documentation, issue/PR templates), CI/CD workflow detection, and deployment counts.

2. **Contributor Metrics:** Per-person commit counts, code additions, and code deletions derived from GitHub's contributor statistics API, which provides weekly breakdowns of activity per contributor.

3. **Technology Detection:** Automated multi-signal detection of cloud infrastructure and AI/ML technology usage through four signal categories: GitHub topics, programming languages, root-level file presence, and dependency analysis (parsing `requirements.txt`, `pyproject.toml`, and `package.json`).

4. **Temporal Metrics:** Complete records of all pull requests (with creation, merge, and closure timestamps), git tags, and GitHub releases.

5. **CHAOSS Metrics:** Twelve metrics from the CHAOSS framework (Table 1), computed from data collected in stages 1–4.

**Table 1.** CHAOSS metrics implemented in this study.

| # | Metric | CHAOSS Working Group | Data Source | Calculation |
|---|--------|---------------------|-------------|-------------|
| 1 | Code Changes (Commits) | Common | Commit activity API | Weekly commit counts over past year |
| 2 | Change Request Acceptance Ratio | Common | Pull requests | Merged PRs / Total PRs |
| 3 | Bus Factor | Common | Contributor stats | Min. contributors for 50% of commits |
| 4 | Types of Contributions | Common | Multiple APIs | Counts of commits, PRs, and issues |
| 5 | Organisational Diversity | DEI | User profiles | Contributors grouped by company affiliation |
| 6 | Issue Label Inclusivity | DEI | Issue labels | Count of newcomer-friendly labels (e.g., "good first issue", "help wanted") |
| 7 | Release Frequency | Evolution | Releases API | Releases per month over project lifespan |
| 8 | Technical Fork | Evolution | Repository API | Total fork count |
| 9 | Burstiness | Evolution | Commit activity | Coefficient of variation (CV) of weekly commits |
| 10 | Defect Resolution Duration | Risk | Issues API | Median days to close issues labelled "bug" |
| 11 | OSI Approved License | Risk | Repository API | SPDX identifier checked against OSI list |
| 12 | Community Health Score | Common | Community profile API | GitHub's community health percentage (0–100) |

### 3.2 Repository Selection

**[MOCKUP: The pilot study uses three repositories selected purposively to represent variation in project maturity, institutional context, and technology domain. The full study will use a systematic sampling strategy described below.]**

#### Pilot Dataset

For the pilot analysis, we selected three civic tech repositories representing different project archetypes:

| Repository | Category | Origin | Age | Language |
|-----------|----------|--------|-----|----------|
| DemocracyClub/UK-Polling-Stations | Electoral infrastructure | UK NGO | 11 years | Python |
| DemocracyClub/WhoCanIVoteFor | Electoral information | UK NGO | 10 years | Python |
| fvialibre/edia | AI fairness research | Argentine NGO | 2 years | Jupyter Notebook/Python |

#### Full Study Sampling Strategy [MOCKUP]

**[MOCKUP: The full study will construct a dataset of 50–200 civic tech repositories using the following sampling strategy:**

1. **Curated lists:** Repositories listed in the Civic Tech Field Guide (civictech.guide), Code for All network projects, and the Participatory Politics Foundation catalogue.
2. **Topic-based search:** GitHub repositories tagged with topics including `civic-tech`, `open-government`, `democracy`, `transparency`, `civic-engagement`, `e-participation`, `open-data`, `gov-tech`.
3. **Snowball sampling:** Repositories identified through the organisational affiliations and cross-project contributions of developers found in seed repositories.
4. **Inclusion criteria:** Public GitHub repository, minimum 10 commits, at least 2 contributors, last commit within the past 3 years.
5. **Exclusion criteria:** Forks without original commits, personal homework/tutorial repositories, archived repositories with no community activity.
6. **Stratification:** Ensure representation across geographic regions, project sizes, institutional types (government, NGO, volunteer collective, academic), and domain categories (elections, transparency, participation, service delivery, civic AI).**]**

### 3.3 Data Collection Process

Data was collected on 20 February 2026 using the Civic Tech Git Crawler tool (v0.1.0) with the following configuration:

- GitHub REST API with Personal Access Token authentication
- Rate limit: 5,000 requests/hour; approximately 200 API calls consumed for 3 repositories
- Statistics endpoints (contributor stats, commit activity) used automatic retry with linear backoff (max 5 attempts) to handle GitHub's asynchronous 202 responses
- All pull requests, tags, and releases were fetched exhaustively (no pagination limits)

### 3.4 Analysis Approach

**Descriptive statistics** were computed for all collected metrics. **[MOCKUP: The full study will additionally employ:**

- **Correlation analysis** between project age, contributor count, bus factor, and community health indicators.
- **Cluster analysis** to identify archetypes of civic tech project health profiles.
- **Social network analysis** of contributor networks across projects, using login-based identity matching to construct bipartite (contributor × repository) graphs.
- **Regression modelling** to examine predictors of project sustainability (operationalised as continued commit activity in the most recent 6-month window).
- **Comparative analysis** across institutional types, geographic regions, and technology domains.**]**

### 3.5 Limitations

Several methodological limitations should be noted:

1. **GitHub-centric:** The tool currently supports only GitHub-hosted repositories. Civic tech projects hosted on GitLab, Gitea, or other platforms are excluded. **[MOCKUP: GitLab support is planned for future versions.]**
2. **API constraints:** GitHub's contributor statistics API only identifies the first 500 author email addresses linked to GitHub users; additional contributors appear as anonymous.
3. **Organisational diversity:** The `company` field in GitHub profiles is self-reported, unstructured, and frequently empty ("Unknown" in our data). This limits the reliability of organisational diversity metrics.
4. **Issue classification:** Defect resolution duration depends on the presence of a "bug" label. Projects using different labelling conventions (or no labels) will have missing data for this metric.
5. **Temporal window:** The commit activity API returns only the most recent 52 weeks of weekly data, limiting longitudinal burstiness analysis.
6. **Code changes attribution:** Additions and deletions include auto-generated code, dependency updates, and bot commits, which may inflate individual contribution metrics.

---

## 4. Results

### 4.1 Repository Overview

Table 2 presents the overview metrics for the three pilot repositories.

**Table 2.** Repository overview metrics.

| Metric | UK-Polling-Stations | WhoCanIVoteFor | EDIA |
|--------|:-------------------:|:--------------:|:----:|
| Age (years) | 11 | 10 | 2 |
| Total commits | 8,419 | 3,327 | 81 |
| Unique contributors | 33 | 29 | 3 |
| Stars | 36 | 43 | 6 |
| Watchers | 6 | 9 | 2 |
| Forks | 29 | 35 | 0 |
| Repository size (KB) | 173,904 | 231,786 | 2,111 |
| Primary language | Python | Python | Jupyter Notebook |
| License (SPDX) | MIT | — | MIT |
| OSI-approved license | Yes | No | Yes |
| Community health score | 75% | 50% | 42% |

The two DemocracyClub repositories are mature, decade-old projects with substantial commit histories (3,327–8,419 commits) and contributor bases (29–33 developers). EDIA, by contrast, is an early-stage research tool with 81 commits from 3 contributors over 2 years. Notably, WhoCanIVoteFor lacks a formal license despite being hosted by a civic-sector NGO and having 10 years of development history.

### 4.2 Contributor Concentration and Bus Factor (RQ1)

**Table 3.** Contributor concentration metrics.

| Metric | UK-Polling-Stations | WhoCanIVoteFor | EDIA |
|--------|:-------------------:|:--------------:|:----:|
| Bus factor | 2 | 2 | 1 |
| Top contributor (% of commits) | chris48s (24.2%) | symroe (27.3%) | LMartinezEXEX (67.9%) |
| Top 2 contributors (% of commits) | 41.3% | 43.2% | 95.1% |
| Top 5 contributors (% of commits) | 65.6% | 65.7% | 100% |
| Total contributors | 33 | 29 | 3 |

All three projects exhibit high contributor concentration. Both DemocracyClub projects have a bus factor of 2, meaning only two individuals account for half of all commits. EDIA has a bus factor of 1, with a single developer (LMartinezEXEX) responsible for 55 of 81 commits (67.9%).

The top 5 contributors account for approximately two-thirds of commits in both DemocracyClub projects (65.6% and 65.7% respectively), despite having 29–33 total contributors. This indicates a long-tail distribution common in open-source projects, but the concentration ratio is notably high for projects backed by a dedicated organisation.

**Table 4.** Top contributors by commits (per repository, top 5).

| Rank | UK-Polling-Stations | Commits | WhoCanIVoteFor | Commits | EDIA | Commits |
|------|-------|---------|------|---------|------|---------|
| 1 | chris48s | 2,038 | symroe | 907 | LMartinezEXEX | 55 |
| 2 | polling-bot-4000 | 1,437 | VirginiaDooley | 530 | nanom | 22 |
| 3 | GeoWill | 1,271 | michaeljcollinsuk | 348 | fvialibre | 1 |
| 4 | symroe | 468 | chris48s | 220 | — | — |
| 5 | dependabot[bot] | 311 | dependabot[bot] | 93 | — | — |

A notable finding is the presence of bot accounts among top contributors. In UK-Polling-Stations, `polling-bot-4000` (an automation account) is the second-most prolific committer with 1,437 commits, and `dependabot[bot]` ranks fifth. In WhoCanIVoteFor, `dependabot[bot]` accounts for 93 commits. These bot contributions inflate commit counts and should be considered when interpreting bus factor and contributor concentration metrics.

Additionally, `chris48s` and `symroe` appear as significant contributors to *both* DemocracyClub projects, indicating shared developer resources within the organisation — a cross-project contributor network pattern that warrants further investigation in the full study.

### 4.3 Code Change Patterns

**Table 5.** Code contribution patterns (human contributors only, top 3 per repository).

| Contributor | Commits | Additions | Deletions | Avg Add/Commit | Avg Del/Commit |
|-------------|---------|-----------|-----------|----------------|----------------|
| **UK-Polling-Stations** | | | | | |
| symroe | 468 | 627,199 | 1,092,770 | 1,340.2 | 2,335.0 |
| davidmiller | 175 | 208,252 | 92,320 | 1,190.0 | 527.5 |
| GeoWill | 1,271 | 171,586 | 65,787 | 135.0 | 51.8 |
| **WhoCanIVoteFor** | | | | | |
| symroe | 907 | 94,890 | 63,222 | 104.6 | 69.7 |
| VirginiaDooley | 530 | 26,067 | 23,909 | 49.2 | 45.1 |
| chris48s | 220 | 17,020 | 11,547 | 77.4 | 52.5 |
| **EDIA** | | | | | |
| LMartinezEXEX | 55 | 29,999 | 16,759 | 545.4 | 304.7 |
| nanom | 22 | 1,197 | 1,128 | 54.4 | 51.3 |

Contributor profiles show distinct patterns. In UK-Polling-Stations, `symroe` has extremely high average additions (1,340 lines) and deletions (2,335 lines) per commit, suggesting large-scale refactoring or data file updates. By contrast, `GeoWill`, despite having the third-highest commit count (1,271), averages only 135 additions per commit, indicating a pattern of frequent, incremental changes.

In EDIA, the sole primary developer (`LMartinezEXEX`) averages 545 additions per commit, consistent with the exploratory, notebook-driven development pattern typical of research projects.

### 4.4 Development Activity Patterns (RQ2)

**Table 6.** Activity and burstiness metrics.

| Metric | UK-Polling-Stations | WhoCanIVoteFor | EDIA |
|--------|:-------------------:|:--------------:|:----:|
| Mean weekly commits | 8.50 | 3.40 | 0.00 |
| Std. dev. weekly commits | 10.78 | 3.93 | 0.00 |
| Coefficient of variation (CV) | 1.27 | 1.16 | — |
| Total PRs | 5,265 | 1,902 | 4 |
| PR acceptance ratio | 0.739 | 0.483 | 0.750 |
| Merged PRs | 3,891 | 918 | 3 |
| Open PRs | 40 | 15 | 1 |
| Closed (unmerged) PRs | 1,334 | 969 | 0 |
| Tags | 0 | 0 | 0 |
| Releases | 0 | 0 | 0 |

**Burstiness.** Both DemocracyClub projects exhibit high development burstiness (CV > 1.0), meaning the standard deviation of weekly commits exceeds the mean. This is consistent with election-cycle-driven development: activity spikes during election periods and subsides between them. UK-Polling-Stations (CV = 1.27, mean = 8.5 commits/week) shows slightly more variability than WhoCanIVoteFor (CV = 1.16, mean = 3.4 commits/week). EDIA's statistics reflect an inactive project in the measurement window (the most recent 52 weeks), as its last commit was in September 2023.

**PR acceptance.** UK-Polling-Stations merges 73.9% of submitted PRs, while WhoCanIVoteFor merges only 48.3%. The higher rejection rate in WhoCanIVoteFor may indicate stricter code review standards, more speculative contributions, or a higher proportion of dependency-update PRs from automated tools that are superseded before merging.

**Release management.** None of the three repositories use formal tagging or release management, with zero tags and zero releases across all projects. This suggests a continuous deployment model, particularly for the DemocracyClub projects which use AWS-based deployment infrastructure (detected via `appspec.yml` and `cdk.json`).

### 4.5 Community Health Infrastructure (RQ3)

**Table 7.** Community documentation and health indicators.

| Indicator | UK-Polling-Stations | WhoCanIVoteFor | EDIA |
|-----------|:-------------------:|:--------------:|:----:|
| README | Yes | Yes | Yes |
| Contributing guidelines | Yes | No | No |
| Code of conduct | Yes | Yes | No |
| Governance document | No | No | No |
| Issue templates | Yes | Yes | No |
| PR templates | Yes | Yes | No |
| Community health score | 75% | 50% | 42% |
| Newcomer labels | 2 | 1 | 2 |
| Total issue labels | 32 | 23 | 9 |
| Newcomer label names | help wanted; recommended for beginners | help wanted | good first issue; help wanted |

Community infrastructure maturity correlates with project age and organisational backing, but the relationship is not uniform. UK-Polling-Stations, the most mature project, has the most comprehensive documentation suite (contributing guide, code of conduct, issue/PR templates) and the highest health score (75%). WhoCanIVoteFor, despite being nearly as old and from the same organisation, lacks a contributing guide and scores only 50%.

EDIA, despite its early stage, includes default GitHub labels ("good first issue", "help wanted") — likely auto-generated during repository creation — resulting in a nominally higher newcomer label count than WhoCanIVoteFor. This illustrates a limitation of label-based inclusivity metrics: the mere presence of newcomer labels does not indicate active use or community engagement strategy.

None of the three projects maintain governance documentation (GOVERNANCE.md), which aligns with findings from the broader open-source ecosystem where formal governance is rare outside large foundation-hosted projects.

### 4.6 Organisational Diversity

**Table 8.** Organisational affiliation of contributors.

| Organisation | UK-Polling-Stations | WhoCanIVoteFor | EDIA |
|-------------|:-------------------:|:--------------:|:----:|
| DemocracyClub | 1 | 1 | — |
| Unknown (not specified) | 24 | 22 | 2 |
| Other identified orgs | 8 | 5 | 1 (FaMAF - UNC) |
| **Total unique organisations** | **11** | **8** | **2** |

Organisational diversity data is severely limited by the low completion rate of the GitHub `company` field. In UK-Polling-Stations, 24 of 33 contributors (72.7%) have no organisational affiliation listed. Among those who do list an affiliation, we observe contributions from diverse sectors: academia (Cardiff University), government-adjacent organisations (mySociety, alphagov), the private sector (Astronomer.io, BT Labs, TrustedHousesitters, Cognizant/NHS England), and the host organisation itself (DemocracyClub).

The presence of only a single self-identified DemocracyClub contributor in each project — despite both being DemocracyClub projects — suggests either that staff members do not consistently set their company field or that much of the development is performed by external contributors.

### 4.7 Technology Adoption (RQ4)

**Table 9.** Technology detection results.

| Signal Type | UK-Polling-Stations | WhoCanIVoteFor | EDIA |
|-------------|:-------------------:|:--------------:|:----:|
| **Cloud detected** | Yes | Yes | No |
| Cloud signals | file:cdk.json, file:appspec.yml, file:Procfile, file:.buildpacks, dep:boto3, dep:aws-cdk | file:appspec.yml, dep:boto3 | — |
| **AI/ML detected** | No | No | Yes |
| AI/ML signals | — | — | lang:Jupyter Notebook, dep:torch, dep:scikit-learn, dep:transformers |
| **CI/CD** | Yes (Dependabot Updates) | Yes (Dependabot Updates) | No |

The DemocracyClub projects show substantial cloud infrastructure investment: UK-Polling-Stations uses AWS CDK (infrastructure-as-code), AWS deployment specifications, Heroku-style buildpacks, and the boto3 SDK — indicating a multi-platform cloud deployment strategy. WhoCanIVoteFor shows a simpler cloud footprint with only `appspec.yml` and `boto3`.

EDIA's technology profile is characteristically different: Jupyter Notebook as the primary language, with PyTorch, scikit-learn, and Hugging Face Transformers as dependencies — a typical AI/ML research stack. The absence of CI/CD, cloud infrastructure, and deployment pipelines is consistent with its nature as a research tool rather than a production service.

### 4.8 Defect Resolution

Of the three pilot repositories, only WhoCanIVoteFor had closed issues labelled "bug" (n = 2). The resolution times were 14.1 days and 145.2 days (median = 79.6 days). **[MOCKUP: The full study with 50–200 repositories will provide sufficient data for meaningful defect resolution analysis, including comparisons across project types and institutional contexts.]**

---

## 5. Discussion

### 5.1 Contributor Concentration as a Systemic Risk

The pilot data reveals a consistent pattern of extreme contributor concentration across civic tech projects. Bus factors of 1–2 across all three repositories, regardless of project age (2–11 years) or contributor base (3–33 developers), suggest that civic tech projects are structurally vulnerable to key-person dependencies.

This is particularly concerning for projects serving democratic infrastructure. UK-Polling-Stations — a tool used to help UK citizens locate their polling stations — depends on a bus factor of 2, with only two developers accounting for half of all code changes. In a domain where reliability during election periods is critical, this concentration represents a systemic risk that funders and policymakers should address.

**[MOCKUP: The full study will examine whether bus factor correlates with institutional type (government vs. NGO vs. volunteer), project age, or the presence of paid contributors.]**

### 5.2 Election-Driven Burstiness

The high burstiness coefficients (CV = 1.16–1.27) observed in the DemocracyClub projects are consistent with the hypothesis that civic tech development follows political calendars rather than standard release cycles. This distinguishes civic tech from commercial software (where steady iteration is the norm) and from research software (where development is grant-cycle-driven).

The complete absence of formal releases (zero tags, zero releases across all projects) further supports a continuous-deployment model where code changes are pushed directly to production. While this approach enables rapid iteration during election periods, it lacks the versioning and rollback infrastructure that would support stability analysis.

**[MOCKUP: Temporal analysis of commit patterns against known UK election dates would test this hypothesis quantitatively. This analysis is planned for the full study.]**

### 5.3 Community Health: Documentation vs. Practice

The pilot reveals a gap between newcomer-facing documentation and actual community practice. EDIA has "good first issue" and "help wanted" labels (likely GitHub defaults) but lacks a contributing guide, code of conduct, issue templates, and PR templates. WhoCanIVoteFor has a code of conduct but no contributing guide. This suggests that label-based CHAOSS metrics (Issue Label Inclusivity) may overestimate newcomer-friendliness when labels exist without supporting infrastructure.

A more robust assessment might combine label presence with:
- The number of issues actually labelled with newcomer tags
- Time-to-first-response on newcomer-labelled issues
- The proportion of newcomer-labelled issues that result in merged PRs

**[MOCKUP: These supplementary analyses are planned for the full study.]**

### 5.4 Bot Contributions and Metric Validity

The significant presence of bot accounts among top contributors (polling-bot-4000, dependabot[bot], pyup-bot) raises questions about metric validity. In UK-Polling-Stations, bot accounts account for approximately 22.5% of total commits among the top 10 contributors. When bot commits are included in bus factor calculations, the metric may understate the true contributor concentration among human developers.

Future iterations of the methodology should implement bot detection (based on the `[bot]` suffix in GitHub usernames and known bot accounts) and report metrics both including and excluding automated contributions.

### 5.5 Cross-Project Contributor Networks

Even in this small pilot, we observe cross-project contributors: `chris48s` and `symroe` are significant contributors to both DemocracyClub repositories, and `awdem` contributes to both as well. This suggests that organisational-level contributor networks may be more important than individual project-level metrics for understanding civic tech sustainability.

**[MOCKUP: The full study will construct bipartite contributor-repository networks and analyse:**
- **Bridge contributors** who connect otherwise disconnected projects
- **Organisational clusters** of contributors working across institutional boundaries
- **Knowledge transfer patterns** inferred from shared contributor activity
- **Network centrality** metrics (degree, betweenness) as predictors of project sustainability**]**

### 5.6 Implications for Civic Tech Sustainability

Based on the pilot findings, we identify several implications:

1. **Funding for contributor diversification.** Bus factors of 1–2 in production civic tech tools represent a fragility that funders should address through supported onboarding programmes and contributor stipends.

2. **Community infrastructure investment.** The inconsistent adoption of contributing guidelines, governance documents, and newcomer labelling — even within the same organisation (DemocracyClub) — suggests that community health practices are not systematically prioritised.

3. **License compliance.** WhoCanIVoteFor, a 10-year-old project with 43 stars and 35 forks, lacks a formal license. This creates legal ambiguity for contributors and reusers, and should be resolved.

4. **Release management.** The complete absence of semantic versioning, tags, and releases across all pilot projects limits auditability and reproducibility. For civic infrastructure serving democratic processes, this is a governance concern.

---

## 6. Threats to Validity

### 6.1 Internal Validity

- **Bot contamination:** Automated accounts inflate commit counts and may distort contributor concentration metrics. Mitigation: future versions will implement bot filtering.
- **Self-reported organisational data:** GitHub's `company` field is self-reported and frequently empty (67–73% missing in our data), limiting the reliability of organisational diversity metrics.
- **Issue labelling variance:** The defect resolution metric depends on a "bug" label, which not all projects use. Only 2 of 3 pilot repositories yielded defect data.

### 6.2 External Validity

- **Pilot sample size (n = 3):** The current results are illustrative only and cannot be generalised to the broader civic tech ecosystem. **[MOCKUP: The full study will address this with n = 50–200 repositories.]**
- **GitHub only:** Projects hosted on GitLab, Bitbucket, or self-hosted platforms are excluded.
- **English-language bias:** The repository selection may over-represent English-speaking civic tech communities. **[MOCKUP: The full study will include non-English projects from Latin America, Europe, and Asia.]**

### 6.3 Construct Validity

- **Bus factor as sustainability proxy:** A low bus factor indicates contributor concentration but does not directly measure project resilience, as it ignores factors such as documentation quality, code modularity, and institutional support.
- **Community health score:** GitHub's community health percentage weights documentation presence but does not assess quality or currency.
- **Technology detection heuristics:** Keyword-based detection may produce false positives (e.g., a project discussing Docker in documentation but not using it) or false negatives (e.g., cloud infrastructure configured outside the repository).

---

## 7. Conclusions and Future Work

### 7.1 Conclusions

This paper has presented a methodological framework and open-source toolchain for analysing civic technology repositories using CHAOSS metrics and standard software engineering indicators. The pilot analysis of three civic tech projects reveals:

1. **Extreme contributor concentration** (bus factor 1–2) exists even in mature, organisationally-backed projects, representing a sustainability risk for civic infrastructure.
2. **Election-driven burstiness** (CV > 1.0) distinguishes civic tech development patterns from both commercial and research software, reflecting the domain's political-calendar dependencies.
3. **Community health infrastructure is inconsistently adopted**, even within a single organisation, and newcomer-friendliness metrics based on label presence alone may be misleading.
4. **Technology choices clearly differentiate project archetypes**: cloud infrastructure for production civic services vs. ML/AI stacks for civic research tools.
5. **Cross-project contributor networks** suggest that civic tech sustainability may be better understood at the organisational or ecosystem level than at the individual project level.

### 7.2 Future Work

**[MOCKUP: The following extensions are planned for the full study:]**

1. **Scale:** Expand the dataset from 3 to 50–200 repositories across multiple civic tech categories and geographic regions.
2. **GitLab support:** Extend the toolchain to support GitLab-hosted projects.
3. **Bot filtering:** Implement automated detection and filtering of bot accounts in contributor metrics.
4. **Longitudinal analysis:** Track repository metrics over time (monthly snapshots) to analyse sustainability trajectories.
5. **Network analysis:** Construct and analyse cross-project contributor networks to identify bridge developers, organisational clusters, and knowledge transfer patterns.
6. **Qualitative validation:** Conduct interviews with civic tech maintainers to validate quantitative findings and contextualise the metrics.
7. **Election-cycle analysis:** Correlate development burstiness with known electoral calendars to test the election-driven development hypothesis.
8. **Predictive modelling:** Develop models to predict project abandonment or sustainability based on early-stage metric profiles.

---

## References

**[MOCKUP: The following reference list includes both real citations used in the text and placeholder references. References marked with * are real; others should be verified and expanded during the full literature review.]**

*Avelino, G., Passos, L., Hora, A., & Valente, M. T. (2016). A novel approach for estimating truck factors. In Proceedings of the 24th International Conference on Program Comprehension (ICPC), pp. 1–10. IEEE.

*CHAOSS. (2023). CHAOSS Metrics. https://chaoss.community/kb/

*Coelho, J., & Valente, M. T. (2017). Why modern open source projects fail. In Proceedings of the 2017 11th Joint Meeting on Foundations of Software Engineering (ESEC/FSE), pp. 186–196. ACM.

*Cosentino, V., Izquierdo, J. L. C., & Cabot, J. (2015). Assessing the bus factor of Git repositories. In 2015 IEEE 22nd International Conference on Software Analysis, Evolution, and Reengineering (SANER), pp. 499–503. IEEE.

*Crowston, K., Wei, K., Li, Q., & Howison, J. (2006). Core and periphery in free/libre and open source software team communications. In Proceedings of the 39th Annual Hawaii International Conference on System Sciences (HICSS). IEEE.

*Dueñas, S., Cosentino, V., Gonzalez-Barahona, J. M., Robles, G., & Izquierdo, J. L. C. (2021). GrimoireLab: A toolset for software development analytics. PeerJ Computer Science, 7, e601.

*Ferreira, M., Valente, M. T., & Ferreira, K. (2019). A comparison of three algorithms for computing truck factors. In Proceedings of the 27th International Conference on Program Comprehension (ICPC), pp. 207–217. IEEE.

*Goggins, S., Lumbard, K., & Germonprez, M. (2021). Open source community health: Analytical metrics and their corresponding narratives. In 2021 IEEE/ACM 4th International Workshop on Software Health in Projects, Ecosystems and Communities (SoHeal), pp. 25–32. IEEE.

Jansen, S. (2014). Measuring the health of open source software ecosystems: Beyond the scope of project health. Information and Software Technology, 56(11), 1508–1519.

Jergensen, C., Sarma, A., & Wagstrom, P. (2011). The onion patch: Migration in open source ecosystems. In Proceedings of the ACM 2011 Conference on Foundations of Software Engineering (ESEC/FSE), pp. 70–80. ACM.

McNutt, J. G., Justice, J. B., Melitski, J. M., et al. (2016). The diffusion of civic technology and open government in the United States. Information Polity, 21(2), 153–170.

Patel, M., Sotsky, J., Gourley, S., & Houghton, D. (2013). The emergence of civic tech: Investments in a growing field. Knight Foundation.

Peixoto, T., & Fox, J. (2016). When does ICT-enabled citizen voice lead to government responsiveness? World Development Report 2016 Background Paper, World Bank.

Shaw, A. (2020). Do civic tech projects usually fail, and if so, why? Knight Foundation Informed Cities Working Paper.

Steinberg, T. (2019). The rise of civic technology. In European Commission Joint Research Centre (JRC) Technical Reports.

**[MOCKUP: Additional references to be added during full literature review. Expect 30–50 references in the final version, covering: MSR methodology, contributor motivation, open-source governance, civic tech policy, social network analysis of developer communities, and CHAOSS metric validation studies.]**

---

## Appendix A: Tool Availability

The Civic Tech Git Crawler tool is available as open-source software at: **[MOCKUP: Insert repository URL upon publication.]**

The tool is implemented in Python 3.13, managed with `uv`, and requires a GitHub Personal Access Token. It collects data through the GitHub REST API and exports results in both CSV (6 files) and JSON (per-repository + aggregated) formats.

### Reproduction instructions

```bash
git clone <repository-url>
cd civic_tech_git_crawler
uv sync
export GITHUB_TOKEN="ghp_your_token"
uv run civic-tech-crawler --config config.example.yaml
```

Results will be written to `./output/`.

## Appendix B: Complete Metric Definitions

For the complete technical specification of all 33 repository-level metrics, 8 contributor-level metrics, and 12 CHAOSS metrics, including calculation formulas, API endpoints, and data type definitions, see the tool's README documentation.

---

**[END OF DRAFT]**

**Mockup annotations summary:**
- Full literature review (Sections 1, 2): needs 20–30 additional references
- Repository sampling strategy (Section 3.2): needs systematic approach for 50–200 repos
- Statistical analysis methods (Section 3.4): correlation, clustering, network analysis, regression
- Expanded results (Section 4): all tables show pilot data only (n=3)
- Network analysis (Section 5.5): requires multi-project contributor data
- Longitudinal analysis: requires time-series data collection
- Election-cycle correlation: requires electoral calendar data
- Bot filtering: not yet implemented in tool
- GitLab support: not yet implemented
- Qualitative validation: not conducted
