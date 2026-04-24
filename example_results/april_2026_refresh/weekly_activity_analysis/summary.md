# Weekly Activity Analysis — New Findings
Derived from `output/contributor_weekly_activity.csv` (12,449 rows, 29 repos, 893 contributors).
## A. Weekly Elephant Factor (sustainability risk, time-resolved)
For each *week* a repo had any code change, we compute the share of lines added+removed that came from the single busiest contributor. 'Elephant weeks' are weeks where ≥50% of the LOC moved through one person. 'Single-contributor weeks' are weeks where ≥99.9% came from one person (effectively solo).
**Most elephant-dominated repos** (highest share of weeks dominated by one contributor):
- `fvialibre/heseia-sentence-bias-dataset`: mean top-share 100.0%, 100% of weeks ≥50%, 100% solo
- `codeforamerica/cmr-maryland-eligibility-determination`: mean top-share 100.0%, 100% of weeks ≥50%, 100% solo
- `codeforamerica/document-transfer-service`: mean top-share 100.0%, 100% of weeks ≥50%, 100% solo
- `markov-root/atlas`: mean top-share 99.8%, 100% of weeks ≥50%, 88% solo
- `CodeForAfrica/openAFRICA`: mean top-share 97.4%, 100% of weeks ≥50%, 88% solo

**Most collaborative repos** (lowest top-share — effort spread across people):
- `civiform/civiform`: mean top-share 50.5%, 43% of weeks ≥50%, 3% solo
- `codeforamerica/vita-min`: mean top-share 55.2%, 50% of weeks ≥50%, 3% solo
- `meshtastic/firmware`: mean top-share 65.3%, 72% of weeks ≥50%, 8% solo
- `CodeForAfrica/ui`: mean top-share 71.5%, 82% of weeks ≥50%, 15% solo
- `CodeForAfrica/outbreak.AFRICA`: mean top-share 77.3%, 95% of weeks ≥50%, 35% solo

**Dataset-wide**: weighted by weeks, 86% of active weeks had a single contributor responsible for ≥50% of the code change.

## B. Churn Ratio (maintenance vs. growth phase)
`churn = deletions / (additions + deletions)`. Close to 0 = pure growth. Close to 1 = pure cleanup. 0.5 = balanced. We report both the repo-wide aggregate (across the full history) and the weekly mean.

**2 repos have net-negative LOC growth** (more cumulative deletions than additions across their default-branch history):
- `DemocracyClub/UK-Polling-Stations`: +6,295,705 / −9,732,924 → net -3,437,219 lines, overall churn 0.61
- `CodeForAfrica/sensors.AFRICA`: +388,074 / −403,490 → net -15,416 lines, overall churn 0.51

**Highest-churn repos** (most deletion-heavy):
- `DemocracyClub/UK-Polling-Stations`: overall churn 0.61, 30% weeks deletion-heavy
- `CodeForAfrica/sensors.AFRICA`: overall churn 0.51, 23% weeks deletion-heavy
- `CodeForAfrica/GenderGap.AFRICA`: overall churn 0.48, 15% weeks deletion-heavy
- `codeforamerica/asap_pdf`: overall churn 0.47, 15% weeks deletion-heavy
- `CodeForAfrica/Dominion.AFRICA`: overall churn 0.45, 19% weeks deletion-heavy

**Lowest-churn repos** (pure growth, little cleanup):
- `luftdata/luftdata.se`: overall churn 0.07, +14,648 / −1,058
- `codeforamerica/document-transfer-service`: overall churn 0.10, +7,810 / −838
- `codeforamerica/tofu-modules-aws-serverless-database`: overall churn 0.13, +2,849 / −440
- `codeforjapan/BirdXplorer`: overall churn 0.18, +87,107 / −19,743
- `markov-root/atlas`: overall churn 0.21, +24,925 / −6,643

## D. Effort Gini Coefficient (inequality of contribution)
Gini of `lines_changed` per contributor per repo. 0 = everyone contributed equally. 1 = one person did everything. This is the **effort-weighted** complement to the existing count-based bus factor / Elephant Factor metrics.
**Most unequal repos** (Gini closest to 1):
- `meshtastic/Meshtastic-Android`: Gini(lines) 0.97, Gini(commits) 0.93, top contributor `jamesarich` did 68%
- `meshtastic/firmware`: Gini(lines) 0.96, Gini(commits) 0.92, top contributor `caveman99` did 19%
- `meshtastic/web`: Gini(lines) 0.95, Gini(commits) 0.88, top contributor `danditomaso` did 43%
- `DemocracyClub/UK-Polling-Stations`: Gini(lines) 0.92, Gini(commits) 0.82, top contributor `symroe` did 52%
- `iiab/iiab`: Gini(lines) 0.91, Gini(commits) 0.92, top contributor `holta` did 66%

**Most equal repos** (Gini closest to 0, min 5 contributors):
- `CodeForAfrica/Dominion.AFRICA`: Gini(lines) 0.57, 8 contributors, top1 share 35%
- `codeforamerica/tax-benefits-backend`: Gini(lines) 0.59, 9 contributors, top1 share 56%
- `codeforamerica/asap_pdf`: Gini(lines) 0.60, 5 contributors, top1 share 53%
- `CodeForAfrica/academy.AFRICA`: Gini(lines) 0.61, 5 contributors, top1 share 53%
- `CodeForAfrica/openAFRICA`: Gini(lines) 0.63, 8 contributors, top1 share 46%

**Lines-vs-commits Gini gap** (how much more unequal is effort than activity?):
- Mean gap across 29 repos: +0.068
- Max gap (effort much more concentrated than commits): `codeforamerica/tax-benefits-backend` at +0.251
- Min gap (commits more concentrated than effort): `CodeForAfrica/PromiseTracker` at -0.037

A positive gap means one contributor's commits are unusually large (mega-commits, possibly bots or bulk imports). A negative gap means they commit often but with small changes.
