# Weekly Activity Analysis — New Findings
Derived from `output/contributor_weekly_activity.csv` (15,343 rows, 55 repos, 1,092 contributors).
## A. Weekly Elephant Factor (sustainability risk, time-resolved)
For each *week* a repo had any code change, we compute the share of lines added+removed that came from the single busiest contributor. 'Elephant weeks' are weeks where ≥50% of the LOC moved through one person. 'Single-contributor weeks' are weeks where ≥99.9% came from one person (effectively solo).
**Most elephant-dominated repos** (highest share of weeks dominated by one contributor):
- `ton-An/station_reach`: mean top-share 100.0%, 100% of weeks ≥50%, 100% solo
- `oklabflensburg/open-school-map`: mean top-share 100.0%, 100% of weeks ≥50%, 100% solo
- `codeforamerica/document-transfer-service`: mean top-share 100.0%, 100% of weeks ≥50%, 100% solo
- `codeforamerica/cmr-maryland-eligibility-determination`: mean top-share 100.0%, 100% of weeks ≥50%, 100% solo
- `codeforbielefeld/losdb`: mean top-share 100.0%, 100% of weeks ≥50%, 100% solo

**Most collaborative repos** (lowest top-share — effort spread across people):
- `civiform/civiform`: mean top-share 50.6%, 44% of weeks ≥50%, 3% solo
- `codeforamerica/vita-min`: mean top-share 55.8%, 51% of weeks ≥50%, 3% solo
- `CodeForAfrica/actNOW`: mean top-share 61.3%, 95% of weeks ≥50%, 10% solo
- `meshtastic/firmware`: mean top-share 65.1%, 72% of weeks ≥50%, 7% solo
- `CivicTechWR/accessible-housing-portal`: mean top-share 70.4%, 80% of weeks ≥50%, 10% solo

**Dataset-wide**: weighted by weeks, 89% of active weeks had a single contributor responsible for ≥50% of the code change.

## B. Churn Ratio (maintenance vs. growth phase)
`churn = deletions / (additions + deletions)`. Close to 0 = pure growth. Close to 1 = pure cleanup. 0.5 = balanced. We report both the repo-wide aggregate (across the full history) and the weekly mean.

**2 repos have net-negative LOC growth** (more cumulative deletions than additions across their default-branch history):
- `CodeforLeipzig/leipziggiesst`: +4,218,466 / −5,895,574 → net -1,677,108 lines, overall churn 0.58
- `CodeForAfrica/sensors.AFRICA`: +388,124 / −403,492 → net -15,368 lines, overall churn 0.51

**Highest-churn repos** (most deletion-heavy):
- `CodeforLeipzig/leipziggiesst`: overall churn 0.58, 25% weeks deletion-heavy
- `CodeForAfrica/sensors.AFRICA`: overall churn 0.51, 23% weeks deletion-heavy
- `CivicTechWR/accessible-housing-portal`: overall churn 0.48, 10% weeks deletion-heavy
- `CodeForAfrica/GenderGap.AFRICA`: overall churn 0.48, 15% weeks deletion-heavy
- `codeforamerica/asap_pdf`: overall churn 0.47, 15% weeks deletion-heavy

**Lowest-churn repos** (pure growth, little cleanup):
- `oklabflensburg/open-emergency-map`: overall churn 0.00, +6,590 / −18
- `oklabflensburg/open-parcel-map`: overall churn 0.03, +53,903 / −1,565
- `codeforcologne/Denkmal-4D-Koeln`: overall churn 0.05, +5,952 / −307
- `oklabflensburg/open-data-api`: overall churn 0.10, +90,167 / −9,541
- `codeforamerica/document-transfer-service`: overall churn 0.10, +7,810 / −838

## D. Effort Gini Coefficient (inequality of contribution)
Gini of `lines_changed` per contributor per repo. 0 = everyone contributed equally. 1 = one person did everything. This is the **effort-weighted** complement to the existing count-based bus factor / Elephant Factor metrics.
**Most unequal repos** (Gini closest to 1):
- `meshtastic/Meshtastic-Android`: Gini(lines) 0.97, Gini(commits) 0.93, top contributor `jamesarich` did 73%
- `meshtastic/firmware`: Gini(lines) 0.96, Gini(commits) 0.91, top contributor `caveman99` did 19%
- `meshtastic/web`: Gini(lines) 0.95, Gini(commits) 0.88, top contributor `danditomaso` did 43%
- `openlegaldata/oldp`: Gini(lines) 0.92, Gini(commits) 0.84, top contributor `malteos` did 96%
- `iiab/iiab`: Gini(lines) 0.91, Gini(commits) 0.92, top contributor `holta` did 65%

**Most equal repos** (Gini closest to 0, min 5 contributors):
- `CodeForAfrica/actNOW`: Gini(lines) 0.41, 5 contributors, top1 share 46%
- `CodeForAfrica/Dominion.AFRICA`: Gini(lines) 0.57, 8 contributors, top1 share 35%
- `CivicTechWR/go-train-group-pass`: Gini(lines) 0.57, 9 contributors, top1 share 38%
- `CodeForAfrica/academy.AFRICA`: Gini(lines) 0.61, 5 contributors, top1 share 53%
- `codeforamerica/tax-benefits-backend`: Gini(lines) 0.63, 11 contributors, top1 share 54%

**Lines-vs-commits Gini gap** (how much more unequal is effort than activity?):
- Mean gap across 55 repos: +0.060
- Max gap (effort much more concentrated than commits): `CodeforLeipzig/weihnachtsmarktkarte` at +0.311
- Min gap (commits more concentrated than effort): `codeforberlin/we-count` at -0.172

A positive gap means one contributor's commits are unusually large (mega-commits, possibly bots or bulk imports). A negative gap means they commit often but with small changes.
