# Per-Repository Findings (May 2026 refresh, n = 37)

Short descriptive findings for each of the 37 repositories in the May 2026 refresh. Each entry surfaces the most distinctive aspect of the repo's metric profile rather than rehashing every column. Numbers come from `repo_metrics.csv`, `chaoss_summary.csv`, `issue_summary.csv`, and the three derived files in `weekly_activity_analysis/`. Repos are listed alphabetically.

---

## CitizensFoundation/your-priorities-app

A Reykjavík-based participatory democracy platform (HTML, started 2014). The crawl finds 4 attributable contributors and an extreme effort profile: **Gini = 0.00 because 100% of every active week is `rbjarnason`** — the platform's lead developer. The repo has 1.8M lines added vs. 1.7M removed (churn 0.49), characteristic of a long-running balanced rewrite. Note the discrepancy flagged in `analysis_n37.md` §4.3: `repo_metrics.total_commits` reports 8,011 vs. 800 attributable in `contributor_weekly_activity` — most history is likely on non-default branches or squash-merged. **One-line summary**: a textbook single-maintainer civic platform with a decade of solo evolution.

## CodeForAfrica/Dominion.AFRICA

A small JavaScript dashboard (started 2019), 7 developers, 0 issues recorded. Effort is moderately concentrated (Gini 0.57) with `kilemensi` taking 35% of lines and 89% of weekly top-shares. PR review is fast (median 3.2 h) and 83% of PRs are accepted — the team has a smooth merge cadence despite being small. **Summary**: representative civic-tech rotation pattern with one anchor contributor and few external issues.

## CodeForAfrica/GenderGap.AFRICA

A 2017 JavaScript visualisation project, 11 developers, bus factor 3 — one of the most resilient cores in CodeForAfrica's portfolio. `DavidLemayian` carries 51% of lines but only as the median weekly top contributor (the role rotates). **Issue first response is very slow (median 7,300 hours = 304 days)** — the slowest in the entire dataset, suggesting the issue tracker is not the team's primary coordination channel. **Summary**: small but well-distributed core, but the issue tracker functions more as an archive than a living queue.

## CodeForAfrica/PromiseTracker

A new TypeScript rewrite (first commit August 2025, ~9 months of history at crawl time). Bus factor 1, HHI 9,558 — one of the most concentrated repos in the sample, with `kelvinkipruto` doing 84% of all lines and 95% of weekly top-shares. Issue response is fast (median 50 h, PR turnaround 0.2 h) and stale ratio is 100% — short backlog because the project is so young. Cloud + AI/ML signals are both detected. **Summary**: a one-developer rapid-iteration phase typical of green-field civic projects.

## CodeForAfrica/academy.AFRICA

A PHP learning platform (2023, 3 developers). Bus factor 2, modest concentration (Gini 0.61). `kelvinkipruto` again is the top contributor at 53% of lines. **PR acceptance ratio is 22%** — the lowest in the sample, indicating either heavy review gatekeeping or a high churn of abandoned WIP branches. **Summary**: a small project where PRs are mostly used for stash/discussion rather than durable contributions.

## CodeForAfrica/actNOW

A young (2021) Python civic-action tool with only 4 stars but 5 attributable developers. **Most equal repo in the sample on the lines-Gini metric: 0.41**, top-1 share 46%, single-contributor weeks just 10%. Net LOC delta is +10k (still in growth phase). **Summary**: rare example in this dataset of an actually balanced contributor distribution; the small absolute scale doesn't prevent meaningful collaboration.

## CodeForAfrica/openAFRICA

A Dockerfile-led data portal (2017, 6 developers). Health % is 75 — highest in CodeForAfrica's portfolio for this metric. Issue first response is slow (146 hours), PR review steady (16 h). 88% of weeks are single-contributor weeks despite 6 attributable people. **Summary**: a mature data-publishing project with good documentation hygiene but workflows centred on a single weekly maintainer.

## CodeForAfrica/outbreak.AFRICA

JavaScript/COVID-era dashboard (March 2020). 11 developers, no issues recorded, 92% PR acceptance. `kilemensi` again leads (57% of lines). **Summary**: archetype of a "rapid-response" civic project — high PR throughput, no issue tracker activity, contribution distribution skewed toward the launch team.

## CodeForAfrica/sensors.AFRICA

Air-quality sensor network (2018, 19 developers). One of the dataset's three **net-negative LOC repos**: +388k / −403k = 51% churn. Bus factor 3, HHI 3,186 — among the better-distributed cores. Stale-issue ratio 100% on 82 issues. **Summary**: a maintenance-phase project with good code-stewardship distribution but a stagnant issue queue.

## CodeForAfrica/ui

The CodeForAfrica shared component library (2022, 19 developers, 443 issues, 5.4M lines added). Health % only 37 (no contributing/governance file), but **bus factor 2 and HHI 2,152 — the second-most-distributed core in CodeForAfrica's set**. Top-1 lines share is just 26% (much lower than its siblings). **Summary**: the most actively-collaborated CodeForAfrica project; serves as the org's design-system anchor.

## DemocracyClub/UK-Polling-Stations

A long-running (2015) Python data pipeline for UK polling-station data. **Largest net-negative LOC trajectory in the sample**: +6.3M / −9.7M = −3.4M net, 61% churn over its lifetime. 33 developers, 3,851 issues (3,786 closed). Effort concentration is high (Gini 0.92) with `symroe` carrying 52% of lines. **Summary**: the dataset's clearest example of a project past the growth phase; large vendored datasets being pruned consistently exceeds new code.

## DemocracyClub/WhoCanIVoteFor

Companion Python project (2016, 30 developers, 420 issues). PR acceptance ratio 50% — among the lowest in the dataset, suggesting a strict review process. `symroe` again leads (56% of lines, 88% of weekly top-shares). Issue first response 156 h. **Summary**: the policy-and-data discipline of UK-Polling-Stations carries over here, but with a smaller codebase and slower issue triage.

## ForumMagnum/ForumMagnum

The community-forum platform behind LessWrong and the Effective Altruism Forum (TypeScript, 2012). **Largest commit count in the sample (52,222) and largest net-positive LOC delta (+7M)**. Bus factor 4, HHI 1,059 — **the lowest HHI / most distributed core in the dataset** despite individual `jimrandomh` accounting for 24% of all lines. PR turnaround 0.2 h is exceptional; 264 attributable developers. **Summary**: the example of how a long-lived, modestly-popular project can build a genuinely distributed core team.


## civiform/civiform

A Java case-management platform for state benefits (2021, 91 developers, 4,409 issues). **Most collaborative repo in the sample on the weekly elephant factor: mean top-share 53.5%, only 5% solo weeks**. Bus factor 3, HHI 1,483. Top contributor `gwendolyngoetz` does 36% of lines. Health % 100. **Summary**: well-resourced government-services project; the rare civic-tech repo where weekly contribution is genuinely shared rather than rotating between solo authors.

## codeforamerica/asap_pdf

A young (Jan 2025) Ruby PDF accessibility tool. Bus factor 1, 5 developers, 4 issues. `lkacenja` carries 53% of lines. Cloud detected, AI/ML signals not (despite the docs mentioning ML — likely too new for dependency-based detection). **Summary**: 8-month-old single-maintainer build-out, looks like it's nearing first stable release.

## codeforamerica/cmr-maryland-eligibility-determination

A 2025 Python project, **1 developer (`victorSauceda`) doing 100% of every commit**. HHI 10,000, Gini 0. No issues, no PRs to review. Health % 25 — lowest community-profile score among repos with active commits. **Summary**: pure single-author government work, included as a lower-bound on what "civic-tech repository" means.

## codeforamerica/document-transfer-service

A Ruby document-transfer service (May 2024, 1 attributable developer). Bus factor 1, HHI 10,000, **lowest churn ratio in the sample (0.10)** — pure growth, almost no rewriting. `jamesiarmes` does 100% of weekly contribution. **Summary**: a green-field service project still in additive scaffolding mode.

## codeforamerica/form-flow

A Java form-flow library (2022, 18 developers, 0 issues). Bus factor 1, but lines-Gini is moderate (0.69) — `cram-cfa` carries only 26% of lines, with rotation among 18 people. PR turnaround 5.4 h. **Summary**: a shared-library project where the "one-bus-factor" warning is technical (HHI > 6,000) but masks a healthier rotation in practice.

## codeforamerica/honeycrisp-gem

Code for America's design-system Ruby gem (2018, 30 developers, 155 issues). **Bus factor 4 — second-highest in the codeforamerica portfolio**. HHI 1,551 (well-distributed). Median issue first-response is 467 h (≈ 19 days) — slow. **Summary**: a long-running shared library with healthy core team rotation but slow issue triage; archetypal "internal tool that became a public artifact" pattern.

## codeforamerica/pya

A new (May 2025) Ruby project, 9 developers in <1 year. Bus factor 2, HHI 3,877. Most weeks (54%) are single-contributor. **Summary**: an early-stage codeforamerica project still finding its core team.

## codeforamerica/recordtrac

A 2013 records-request tracking platform (CSS-primary, 17 developers). One of the dataset's three **net-negative LOC repos** (−34k net, 52% churn). 149 issues, all 84 closed ones likely from initial deployment phase. **Summary**: a 12-year-old project visibly in mature-maintenance mode; deletions outpace additions and the issue queue has stalled.

## codeforamerica/tax-benefits-backend

A young (April 2024) HCL-based infrastructure project. Bus factor 3, HHI 1,754 — well-distributed for an infra project. PR turnaround 0.4 h is exceptional. **Summary**: the textbook "Terraform module owned by a small infrastructure team" pattern; fast iteration, no issue-tracker overhead.

## codeforamerica/tofu-modules-aws-serverless-database

An AWS-serverless OpenTofu module (August 2024, 3 developers). Bus factor 1, but `jamesiarmes` carries 85% of lines and the project has the second-lowest churn ratio (0.13). 97% PR acceptance. **Summary**: classic infrastructure-as-code pattern — one author, careful additive growth, almost no rewriting.

## codeforamerica/vita-min

The Volunteer Income Tax Assistance backend (2019, 50 developers, 1.5M LOC added). Bus factor 4 (one of the most resilient cores in codeforamerica). **Lowest single-contributor week percentage in the sample (3%)** alongside civiform — these two are the only n=37 repos where solo weeks fall below 5% of all active weeks. **Summary**: the codeforamerica project that most resembles a sustainable open-source community.

## codeforjapan/BirdXplorer

A Python research tool (2023, 9 developers). 97% PR acceptance, 9 issues with 50% stale ratio. Effort moderately concentrated (Gini 0.74). **Lowest churn ratio in the new-9 cohort (0.19)** alongside ceuk-marking. **Summary**: small Japanese research project still in linear-growth phase; clean PR workflow but solo-week dominance.

## fvialibre/edia

An ML/NLP bias-evaluation Jupyter notebook project (2022, 3 developers). **Median PR review turnaround is 47 h** — among the slowest. `LMartinezEXEX` carries 79% of lines. AI/ML signals correctly detected. **Summary**: research-team rhythm — slow async reviews, narrow contributor set, single dominant author per active week (72%).

## fvialibre/heseia-sentence-bias-dataset

A May 2025 dataset repository (no primary language detected — pure data). 1 developer, 0 issues, single-author 100% of weeks. Health % 14 — lowest in the sample (no community files). **Summary**: a static research artifact rather than an evolving codebase; included as a lower-bound on "what a civic-tech repository can be".

## iiab/iiab

The Internet-In-A-Box offline-server project (Jinja, 2017, 27 developers, 1,855 stars, 1,530 issues). Bus factor 1, HHI 5,431 — high concentration despite a long history; `holta` carries 70% of lines and 87% of weekly top-shares. Issue first response is fast (2.9 h). **Summary**: long-running educational-infrastructure project visibly dependent on one expert maintainer; healthy issue triage but high bus-factor risk.

## luftdata/luftdata.se

A Swedish air-quality sensor site (SCSS, 2018, 4 developers). **Lowest churn ratio in the dataset (0.07)** — pure additive growth, almost no deletion. `ebner` does 88% of lines and 81% of weeks are solo. **Summary**: a small, low-traffic civic-data site that has only ever grown, never been refactored.

## markov-root/atlas

A January-2026 Astro static-site project (2 attributable developers). Health % 0 (no community profile files at all). 100% of weeks are dominated by `git@xfe.li` (an email-only contributor not linked to a GitHub login). **Summary**: very early-stage personal project; appears in the dataset because it self-identified as civic-tech.

## mastodon/mastodon

The Mastodon federation server (Ruby, 2016, 50k★, 406 attributable developers). **Issue analytics capped at 5,000 — the only repo in the sample to hit the cap**; actual issue total is higher and any total/closed/stale ratio for mastodon should be treated as right-censored. Bus factor 3, HHI 1,462 — well-distributed despite scale. `Gargron` carries 44% of lines and 62% of weekly top-shares. **Summary**: the dataset's clearest example of sustained large-scale community development with one founder still meaningfully central.

## meshtastic/Meshtastic-Android

The Android client for Meshtastic mesh radios (Kotlin, 2020, 107 developers, 1,475 issues). Bus factor 1, HHI 9,384 despite 107 contributors — driven by `jamesarich` doing 99% of lines (vs. 76% of commits). **Lines-vs-commits Gini gap of +0.13** is the second-largest in the sample, indicating mega-commits. Median issue response 1.4 h, PR turnaround 0.4 h. **Summary**: a small core team operating at very high velocity, with one author landing very large refactor commits.

## meshtastic/firmware

The C++ device firmware for Meshtastic (2020, 414 developers, 7,411★, 3,307 issues). Bus factor 3, HHI 1,322 — well-distributed core. `Jorropo` carries 64% of lines (Gini-lines 0.95), but only 0% of weeks are pure solo — true rotation. **Median issue response is 0 hours** (essentially instant). **Summary**: an embedded-systems project with surprisingly mature community workflows; among the dataset's exceptional examples of large-scale collaboration.

## meshtastic/web

The Meshtastic web UI (TypeScript, 2021, 73 developers). Bus factor 1, HHI 5,331. `danditomaso` is the dominant top-share (43% of lines, 91% of weekly top-shares). 53% of weeks are single-contributor. **Summary**: a fast-iteration UI project with the typical "one full-time maintainer + many drive-bys" shape.

## mysociety/ceuk-marking

A small (0★, 5 developers) Python project for UK climate-emergency local-council assessment (2022). `struan` carries 84% of lines. **Median issue first response 1,006 hours (≈ 42 days)** — third-slowest in the dataset. **Summary**: an internal tool published openly; quiet, effective, but the issue tracker is not actively monitored.

## okfde/froide

The German Freedom-of-Information request platform from Open Knowledge DE. **Oldest project in the sample (first commit 2011-04-12, 15 years)**. 38 developers, 436 issues, bus factor 2. `stefanw` carries 80% of lines and 95% of weekly top-shares — extreme dependence on the founding maintainer despite a long history. Effort-Gini 0.95. **Summary**: the canonical "long-lived single-founder civic platform" — long history, broad contribution surface, but a single author still essentially holds the codebase.

## openplans/shareabouts

A pioneering civic-mapping platform (JavaScript, 2011, 16 developers). **Slowest median PR review turnaround in the dataset: 902 hours (≈ 38 days)**. Top contributor `mjumbewu` carries 40% of lines and 92% of weekly top-shares. 100% stale-issue ratio, 126 issues, only 41% closed. **Summary**: a mature project whose active development has substantially slowed; the long-tail PR turnaround time and high open-issue ratio mark it as effectively in archive maintenance.

---

## Cross-cutting observations

**Bus-factor 1 is the modal outcome** — 16 of 37 repositories (42%) have `bus_factor_no_bots = 1`, meaning a single contributor accounts for ≥50% of the project's commits. The rate is similar in both cohorts (new 8: 4/8, original 29: 13/29) so this isn't a sample-composition artefact.

**Effort concentration scales sub-linearly with project size**. The four most-collaborative weekly profiles (mean top-share <60%) come from civiform, vita-min, mastodon, and meshtastic/firmware — projects with 90+ developers and active corporate or community sponsorship. Below that scale threshold, single-author weeks are the norm regardless of organisation.

**Three repositories have net-negative LOC trajectories**: UK-Polling-Stations, recordtrac, sensors.AFRICA. All three have median ages above the dataset median (6.2 years). No project under 4 years old shows this pattern, suggesting it is a maturity signal rather than a project-type signal.

**Issue first-response times span four orders of magnitude** — from 0 hours (meshtastic/firmware) to 7,300 hours (CodeForAfrica/GenderGap.AFRICA). The median is 24 hours, but 25% of repositories take more than 60 hours and 12% take more than 800 hours. Issue-tracker hygiene varies more across this dataset than any other behavioural metric we measure.

**Founder dependency is high even in projects with broad contribution**. mastodon/Gargron, ForumMagnum/jimrandomh, okfde/stefanw, and civiform/gwendolyngoetz all show top-1 line shares between 24% and 80% — meaning even on the most distributed projects, removing one specific person would substantially change the LOC trajectory.
