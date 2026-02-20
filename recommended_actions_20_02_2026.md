# Recommended Additional Metrics for Civic Tech Analysis

**Date:** 2026-02-20
**Context:** Academic review of metrics gaps in the Civic Tech Git Crawler, aligned with the paper's four research questions.

---

## 1. Contributor Concentration & Sustainability Risk (RQ1)

### Social Network Analysis Metrics

Current tool captures per-person commit counts but does not model the **network structure** between contributors.

- **Degree/Betweenness/Closeness Centrality** -- Identify key bridge contributors and influence flows within the project
- **Core-Periphery Structure** -- Classifies contributors as core (densely connected, high-activity) vs. peripheral (sporadic). Tracking movement from periphery to core over time is a strong sustainability signal

**Key references:**
- Crowston, K. & Howison, J. (2006). "Hierarchy and centralization in free and open source software team communications." *Knowledge, Technology & Policy*, 18(4), 65-85.
- Joblin, M. et al. (2017). "From developer networks to verified communities: A fine-grained approach." *Proc. ICSE 2017*.
- Jergensen, C. et al. (2011). "The Onion Patch: Migration in Open Source Ecosystems." *Proc. ESEC/FSE 2011*. -- Describes the onion model of OSS contributor structure (core to periphery).

### Advanced Bus Factor / Knowledge Distribution

Current bus factor looks at commits. Stronger models also consider:

- **Degree of Authorship (DOA)** -- % of commits per developer per *file*, revealing knowledge silos
- **Degree of Interest (DOI)** -- Engagement depth across code areas
- **Code review knowledge** -- Contributors who review but do not commit still carry institutional knowledge

**Key references:**
- Avelino, G. et al. (2016). "A Novel Approach for Estimating Truck Factors." *Proc. ICPC 2016*.
- Ferreira, M. et al. (2019). "Algorithms for Estimating Truck Factor." *arXiv:2202.01523*.
- Ricca, F. et al. (2011). "Assessing the Bus Factor of Git Repositories." *SANER 2011*.

---

## 2. Development Activity Patterns (RQ2)

### Contributor Retention & Cohort Analysis

A major gap in the current metrics -- the tool can derive *who* contributed, but not retention patterns over time:

- **New vs. Casual vs. Regular contributor classification** -- Categorize contributors by activity frequency per time window
- **Retention rate** -- % of new contributors who return for a second contribution
- **Contributor half-life** -- Time after which 50% of contributors become inactive
- **Onboarding success rate** -- Correlation of "good first issue" labels with new contributor conversion

**Key references:**
- Zhou, M. & Mockus, A. (2012). "What Make Long Term Contributors: Willingness and Opportunity in OSS Community." *Proc. ICSE 2012*.
- Steinmacher, I. et al. (2015). "A systematic literature review on the barriers faced by newcomers to open source software projects." *IST*, 59, 67-85.
- Qiu, H. et al. (2019). "Going Farther Together: The Impact of Social Capital on Sustained Participation in Open Source." *Proc. ICSE 2019*.

### Code Review Quality Metrics

Current PR metrics capture counts and merge status but not the **quality of the review process**:

- **Time to First Response** -- How quickly a PR or issue gets initial feedback (strong signal of community responsiveness)
- **Review Turnaround Time** -- Duration from PR open to first review comment
- **Review Depth** -- Number of review comments per PR (4+ indicates substantive review)
- **PR Size** -- Lines changed per PR (smaller PRs correlate with faster, higher-quality feedback)
- **Review Cycle Time** -- Full duration from PR open to merge

**Key references:**
- Rigby, P. & Bird, C. (2013). "Convergent Contemporary Software Peer Review Practices." *Proc. ESEC/FSE 2013*.
- Baysal, O. et al. (2016). "Investigating technical and non-technical factors influencing modern code review." *EMSE*, 21(3), 932-959.
- Bosu, A. et al. (2017). "Process Aspects and Social Dynamics of Contemporary Code Review." *IEEE TSE*, 43(1), 56-75.

### Issue Responsiveness

- **Median Time to First Response** on issues (not just bugs)
- **Issue triage effectiveness** -- % of issues that get labeled within 48h
- **Stale issue ratio** -- % of issues with no activity for 90+ days

**Key reference:**
- GitHub issue-metrics action (github/issue-metrics). Also: CHAOSS metric "Time to First Response."

---

## 3. Institutional Affiliation & Organizational Dynamics (RQ3)

### Organizational Diversity Metrics

Current tool has basic org diversity from GitHub profiles. More nuanced approaches:

- **Institutional type classification** -- Government agency, nonprofit, academic institution, private company, individual volunteer. Critical for civic tech, where the mix of institutional types is a defining characteristic.
- **Elephant Factor** -- The minimum number of *organizations* whose contributors account for 50% of commits (organizational-level bus factor). A CHAOSS metric not yet implemented.
- **Organizational contribution concentration** -- Herfindahl-Hirschman Index (HHI) of organizational commit shares

**Key references:**
- Goggins, S. et al. (2021). "Open Source Community Health: Analytical Metrics and Their Corresponding Narratives." *Proc. CHASE 2021*.
- Vasilescu, B. et al. (2015). "Gender and Tenure Diversity in GitHub Teams." *Proc. CHI 2015*. -- Demonstrates how team diversity affects productivity.
- Daniel, S. & Stewart, K. (2016). "Open Source Project Success: Resource Access, Flow, and Integration." *JAIS*, 17(1).

---

## 4. Community Health Practices (RQ3)

### Documentation & Governance Quality

The tool checks for the *presence* of docs (CONTRIBUTING, CODE_OF_CONDUCT, etc.). More granular metrics:

- **Documentation freshness** -- Age of last commit to documentation files
- **README comprehensiveness score** -- Length, presence of sections (install, usage, contributing, license)
- **Governance model classification** -- Benevolent dictator, meritocracy, committee, foundation-backed
- **Communication channel diversity** -- Discord, Slack, mailing list, forum presence

**Key references:**
- Prana, G.A. et al. (2019). "Categorizing the Content of GitHub README Files." *EMSE*, 24, 1296-1327.
- Trinkenreich, B. et al. (2020). "Hidden Figures: Roles and Pathways of Successful OSS Contributors." *Proc. ACM HCI*, 4(CSCW2).

### DEI-Specific Metrics (CHAOSS DEI Working Group)

- **Communication inclusivity** -- Language accessibility, tone analysis
- **Sponsorship/mentorship programs** -- Presence of formal onboarding programs
- **Contributor covenant adoption** -- Specific code of conduct version and enforcement procedures

---

## 5. Software Ecosystem-Level Metrics (Cross-Project)

### Ecosystem Health Framework

Going beyond individual projects to understand civic tech as an *ecosystem*:

- **Cross-project contributor overlap** -- Contributors active in multiple civic tech repos (network bridges)
- **Dependency graph analysis** -- Shared dependencies across civic tech projects
- **Ecosystem productivity/robustness/niche creation** -- Jansen's three-pillar model

**Key references:**
- Jansen, S. (2014). "Measuring the Health of Open Source Software Ecosystems: Beyond the Scope of Project Health." *IST*, 56(11), 1508-1519.
- Manikas, K. & Hansen, K.M. (2013). "Software ecosystems -- A systematic literature review." *JSS*, 86(5), 1294-1306.
- Mens, T. et al. (2014). "Evolving Dependency Structures in the Linux Kernel." *J. Software: Evolution and Process*.

### DORA / Four Keys Metrics

From the DevOps Research and Assessment framework -- measures software delivery performance:

- **Deployment Frequency** -- How often code is deployed to production
- **Lead Time for Changes** -- Time from commit to production deployment
- **Change Failure Rate** -- % of deployments causing failures
- **Time to Restore Service** -- Recovery time after incidents

**Key reference:**
- Forsgren, N. et al. (2018). *Accelerate: The Science of Lean Software and DevOps*. IT Revolution Press.

---

## 6. Civic Tech-Specific Frameworks

### Civic Tech Research Taxonomy

- **Circular framework**: designers to tools to users to impact to designers
- Unique to civic tech: electoral calendars create **cyclical demand spikes** that affect burstiness metrics differently than in general OSS

**Key references:**
- Boehner, K. & DiSalvo, C. (2016). "Data, Design and Civics: An Exploratory Study of Civic Tech." *Proc. CHI 2016*.
- Steinberg, T. (2019). *mySociety* reports on civic tech organizational sustainability.
- Peixoto, T. & Fox, J. (2016). "When Does ICT-Enabled Citizen Voice Lead to Government Responsiveness?" *IDS Bulletin*, 47(1).
- Saldivar, J. et al. (2019). "Civic Technology for Social Innovation: A Systematic Literature Review." *Computer Supported Cooperative Work*, 28, 169-207.

### Civic Tech Index

The **Civic Tech Index** project catalogs open-source civic tech projects globally and could serve as the sampling frame for the expanded study.

**Reference:**
- Civic Tech Index -- https://github.com/civictechindex -- Code for America

---

## Summary: Recommended Additions by Priority

| Priority | Metric | Maps to RQ | Implementation Effort |
|----------|--------|-----------|----------------------|
| HIGH | Time to First Response (issues/PRs) | RQ2, RQ3 | Low |
| HIGH | Contributor Retention Cohorts (new/casual/regular) | RQ1, RQ2 | Medium |
| HIGH | Elephant Factor (org-level bus factor) | RQ1, RQ3 | Low |
| MEDIUM | PR Review Depth & Turnaround Time | RQ2 | Medium |
| MEDIUM | Core-Periphery Network Analysis | RQ1 | High |
| MEDIUM | Institutional Type Classification | RQ3 | Medium |
| MEDIUM | Cross-Project Contributor Overlap | RQ5 | Medium |
| LOW | Documentation Freshness | RQ3 | Low |
| LOW | Stale Issue Ratio | RQ2 | Low |
| LOW | DORA Lead Time / Deploy Frequency | RQ4 | High |
