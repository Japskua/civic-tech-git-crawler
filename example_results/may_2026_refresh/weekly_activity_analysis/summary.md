# Weekly Activity Analysis — New Findings
Derived from `output/contributor_weekly_activity.csv` (20,162 rows, 38 repos, 2,684 contributors).
## A. Weekly Elephant Factor (sustainability risk, time-resolved)
For each *week* a repo had any code change, we compute the share of lines added+removed that came from the single busiest contributor. 'Elephant weeks' are weeks where ≥50% of the LOC moved through one person. 'Single-contributor weeks' are weeks where ≥99.9% came from one person (effectively solo).
**Most elephant-dominated repos** (highest share of weeks dominated by one contributor):
- `CitizensFoundation/your-priorities-app`: mean top-share 100.0%, 100% of weeks ≥50%, 100% solo
- `codeforamerica/cmr-maryland-eligibility-determination`: mean top-share 100.0%, 100% of weeks ≥50%, 100% solo
- `codeforamerica/document-transfer-service`: mean top-share 100.0%, 100% of weeks ≥50%, 100% solo
- `fvialibre/heseia-sentence-bias-dataset`: mean top-share 100.0%, 100% of weeks ≥50%, 100% solo
- `markov-root/atlas`: mean top-share 99.8%, 100% of weeks ≥50%, 88% solo

**Most collaborative repos** (lowest top-share — effort spread across people):
- `civiform/civiform`: mean top-share 53.5%, 55% of weeks ≥50%, 5% solo
- `codeforamerica/vita-min`: mean top-share 55.4%, 51% of weeks ≥50%, 3% solo
- `meshtastic/firmware`: mean top-share 58.1%, 63% of weeks ≥50%, 0% solo
- `Significant-Gravitas/AutoGPT`: mean top-share 60.1%, 57% of weeks ≥50%, 3% solo
- `CodeForAfrica/actNOW`: mean top-share 61.4%, 95% of weeks ≥50%, 10% solo

**Dataset-wide**: weighted by weeks, 86% of active weeks had a single contributor responsible for ≥50% of the code change.

## B. Churn Ratio (maintenance vs. growth phase)
`churn = deletions / (additions + deletions)`. Close to 0 = pure growth. Close to 1 = pure cleanup. 0.5 = balanced. We report both the repo-wide aggregate (across the full history) and the weekly mean.

**3 repos have net-negative LOC growth** (more cumulative deletions than additions across their default-branch history):
- `DemocracyClub/UK-Polling-Stations`: +6,297,037 / −9,733,304 → net -3,436,267 lines, overall churn 0.61
- `codeforamerica/recordtrac`: +333,219 / −366,883 → net -33,664 lines, overall churn 0.52
- `CodeForAfrica/sensors.AFRICA`: +388,122 / −403,490 → net -15,368 lines, overall churn 0.51

**Highest-churn repos** (most deletion-heavy):
- `DemocracyClub/UK-Polling-Stations`: overall churn 0.61, 30% weeks deletion-heavy
- `codeforamerica/recordtrac`: overall churn 0.52, 20% weeks deletion-heavy
- `CodeForAfrica/sensors.AFRICA`: overall churn 0.51, 23% weeks deletion-heavy
- `CitizensFoundation/your-priorities-app`: overall churn 0.48, 12% weeks deletion-heavy
- `CodeForAfrica/GenderGap.AFRICA`: overall churn 0.48, 15% weeks deletion-heavy

**Lowest-churn repos** (pure growth, little cleanup):
- `luftdata/luftdata.se`: overall churn 0.07, +14,648 / −1,058
- `codeforamerica/document-transfer-service`: overall churn 0.10, +7,810 / −838
- `codeforamerica/tofu-modules-aws-serverless-database`: overall churn 0.13, +2,849 / −440
- `codeforjapan/BirdXplorer`: overall churn 0.18, +87,107 / −19,743
- `mysociety/ceuk-marking`: overall churn 0.19, +62,746 / −14,454

## D. Effort Gini Coefficient (inequality of contribution)
Gini of `lines_changed` per contributor per repo. 0 = everyone contributed equally. 1 = one person did everything. This is the **effort-weighted** complement to the existing count-based bus factor / Elephant Factor metrics.
**Most unequal repos** (Gini closest to 1):
- `Significant-Gravitas/AutoGPT`: Gini(lines) 0.99, Gini(commits) 0.88, top contributor `waynehamadi` did 23%
- `mastodon/mastodon`: Gini(lines) 0.98, Gini(commits) 0.92, top contributor `Gargron` did 44%
- `ForumMagnum/ForumMagnum`: Gini(lines) 0.97, Gini(commits) 0.95, top contributor `jimrandomh` did 24%
- `meshtastic/firmware`: Gini(lines) 0.95, Gini(commits) 0.76, top contributor `Jorropo` did 64%
- `meshtastic/web`: Gini(lines) 0.95, Gini(commits) 0.88, top contributor `danditomaso` did 43%

**Most equal repos** (Gini closest to 0, min 5 contributors):
- `CodeForAfrica/actNOW`: Gini(lines) 0.41, 5 contributors, top1 share 46%
- `CodeForAfrica/Dominion.AFRICA`: Gini(lines) 0.57, 8 contributors, top1 share 35%
- `codeforamerica/asap_pdf`: Gini(lines) 0.60, 5 contributors, top1 share 53%
- `CodeForAfrica/academy.AFRICA`: Gini(lines) 0.61, 5 contributors, top1 share 53%
- `CodeForAfrica/openAFRICA`: Gini(lines) 0.63, 8 contributors, top1 share 46%

**Lines-vs-commits Gini gap** (how much more unequal is effort than activity?):
- Mean gap across 38 repos: +0.059
- Max gap (effort much more concentrated than commits): `meshtastic/firmware` at +0.194
- Min gap (commits more concentrated than effort): `CodeForAfrica/actNOW` at -0.084

A positive gap means one contributor's commits are unusually large (mega-commits, possibly bots or bulk imports). A negative gap means they commit often but with small changes.
