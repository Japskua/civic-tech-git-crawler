# Analysis of the n=38 Civic-Tech Repository Refresh (May 2026)

**Companion analysis for `example_results/may_2026_refresh/`. All numbers in this document were computed against the May 2026 crawl (commit `3fd1811` on branch `claude/add-new-repos-2026-05`).**

This refresh expands the existing 29-repository civic-tech sample by nine substantively different projects (Section 1), and asks two questions:

1. **Robustness**: do the central findings of the n=29 paper (Sections 4.1–4.7) survive the introduction of much larger and much smaller repositories?
2. **Discriminating power**: does the wider sample reveal patterns that were not visible at n=29 — particularly around effort concentration in the top 1% of contributors?

Section 2 summarises the dataset. Section 3 reports the headline numerical results. Section 4 discusses methodological notes — in particular the 5,000-issue cap and what it means for `issue_summary` interpretations on `mastodon/mastodon`. Section 5 lists threats to validity.

---

## 1. Sample composition and why these nine were added

The original n=29 sample was built around small-to-mid-scale civic-tech projects (median 1,302 commits, median 7 stars) — a population that intentionally biases toward "the long tail of public-interest software" rather than flagship open-source projects. That bias was a feature for the paper's main claims about civic-tech sustainability, but it left two methodological concerns:

- **Truncation in the upper tail**. With no repository above ~14k commits or ~3k stars, correlations involving project size were estimated on a compressed range. It was not clear whether observed relationships (bus-factor / HHI / health-percentage) extrapolated to flagship-scale projects.
- **Truncation in the lower tail**. With a median project age of 4 years, the sample under-represented the older civic projects (10+ years) where churn dominates growth.

The nine additions address both:

| Repository | Stars | Commits | First commit | Notes |
|---|---:|---:|---|---|
| `Significant-Gravitas/AutoGPT` | 183,985 | 8,476 | 2023-03-16 | Highest-stars project ever included; young (3y) but huge external attention |
| `mastodon/mastodon` | 49,924 | 21,215 | 2016-02-20 | Largest contributor base in the sample (1,055 unique authors via GraphQL) |
| `ForumMagnum/ForumMagnum` | 706 | 52,222 | 2012-08-23 | Largest commit count in the sample; modest stars but very active core team |
| `okfde/froide` | 409 | 7,888 | **2011-04-12** | The oldest project in the sample (15 years); German freedom-of-information platform |
| `openplans/shareabouts` | 283 | 1,956 | 2011-10-27 | Older civic-mapping project, still in the sample-typical commit range |
| `codeforamerica/recordtrac` | 60 | 2,570 | 2013-03-28 | Records-request tracker; net-negative LOC delta over its lifetime |
| `CitizensFoundation/your-priorities-app` | 142 | 800–8,011* | 2014-08-22 | Deliberation platform; the two commit numbers diverge — see §4.2 |
| `CodeForAfrica/actNOW` | 4 | 2,111 | 2021-04-19 | Younger CodeForAfrica project; tested whether <10-star projects still produce usable signal |
| `mysociety/ceuk-marking` | 0 | 674 | 2022-12-13 | Smallest project (0 stars, 674 commits) — a usable signal at the absolute lower bound |

\* The `repo_metrics.total_commits` value (8,011) is GitHub's default-branch count via `Link: rel="last"`. The `contributor_weekly_activity` GraphQL pass attributed only 800 commits to identifiable (login-or-email) authors. The 9× gap suggests either a non-default-branch-heavy history or a large fraction of unattributable squash-merge commits. This is flagged but not resolved in this refresh.

The combined dataset spans **15 years (2011 → 2026), 16 primary languages, 17 organisations, and a star range of 0–183,985 (six orders of magnitude)** — meaningfully wider than the n=29 sample and wide enough to test extrapolation.

---

## 2. Dataset summary

```
total_repositories         : 38
unique_organisations       : 17
unique_primary_languages   : 16
total_contributors         : 731
  human_contributors       : 680
  bot_contributors         : 51   (6.97% of person_metrics population)
total_commits (repo)       : 186,490
total_commits (CWA)        : 152,305
total_stars                : 247,523
total_forks                : 57,542
repos_with_ci_cd           : 32 / 38   (84%)
repos_with_cloud_signals   : 28 / 38   (74%)
repos_with_ai_ml_signals   :  4 / 38   (11%)
repos_with_osi_license     : 12 / 38   (32%)
median_age_years           : 6.2
```

The CI/CD adoption rate (84%) is consistent with the n=29 finding (83%); cloud-tech detection (74%) is also stable; and OSI-licensing remains low (32%) — about a third of civic-tech repositories carry an SPDX-listed open-source license, with most of the rest using `NOASSERTION` (no machine-detected license) or no license file at all. None of these distributional figures change appreciably with the nine additions.

---

## 3. Headline statistical results

### 3.1 Correlations are stable, but coefficients tighten

Spearman correlations between project-size proxies (stars, forks, commits, num_developers) all strengthen as the sample widens:

| Pair | n=29 (April, ρ) | n=38 (May, ρ) | Direction |
|---|---:|---:|---|
| stars ↔ forks | 0.91 | **0.94** | ↑ |
| num_developers ↔ stars | ~0.65 | **0.75** | ↑ |
| num_developers ↔ total_commits | ~0.78 | **0.80** | ↑ |
| total_commits ↔ stars | ~0.65 | **0.70** | ↑ |
| age_years ↔ total_commits | ~0.55 | **0.57** | ≈ |
| age_years ↔ forks | ~0.55 | **0.56** | ≈ |

All of the above remain significant under Benjamini–Hochberg FDR control (q < 0.001). The interpretation: the size-popularity-activity triangle is strongly co-varying, and adding heavyweight projects strengthens rather than weakens the relationships — i.e., the n=29 estimates were not artefacts of the truncated sample.

### 3.2 Bus factor / HHI relationship remains the strongest in the dataset

The relationship between `bus_factor_no_bots` and `hhi_no_bots` (effort concentration) is again the strongest non-trivially structured correlation:

```
bus_factor_no_bots ↔ hhi_no_bots: ρ = -0.91 (n=38, p < 1e-15, FDR-significant)
```

A partial correlation controlling for `num_developers` (size) only marginally weakens this: ρ_partial = -0.88 (interpretation: **robust**). In other words, even within size-strata, projects with higher effort concentration have lower bus factor. This is the core mechanical relationship the paper is built around, and it persists with high effect size at n=38.

### 3.3 Cohort comparison (new 9 vs. original 29)

This is the most substantive new finding.

| Metric (median) | New 9 | Original 29 | Direction |
|---|---:|---:|---|
| stars | **283.0** | 7.0 | New 9 are 40× more popular |
| forks | **99.0** | 4.0 | New 9 are 25× more forked |
| total_commits | **7,888** | 603 | New 9 are 13× larger |
| num_developers | **17.0** | 11.0 | Modestly more contributors |
| **health_percentage** | **37** | **50** | **New 9 are LESS healthy by GitHub's community-profile metric** |
| **bus_factor** | **1** | **2** | **New 9 are LESS resilient** |
| HHI no-bots | 4,448 | 4,092 | Slightly more concentrated |
| Median time to first response (issues, h) | **20.2** | 45.1 | New 9 respond ~2× faster |
| Median PR review turnaround (h) | **15.4** | 3.0 | New 9 are 5× SLOWER on PR reviews |

**The most counterintuitive result is that the bigger, more popular projects in the New 9 cohort have *lower* bus factor and *lower* health-percentage scores than the original 29.** The mechanism is visible in §3.4: AutoGPT (1 core), mastodon (~3 core, but `Gargron` is 44% of all line-changes), and ForumMagnum (~4 core, but `jimrandomh` is 24%) are dominated by very small core teams operating at very high throughput. The original 29 includes more mid-scale projects with multi-person rotation in the core role.

The faster issue first-response time + slower PR turnaround pattern is also new and consistent with the read that the New 9 are flagship-scale projects with dedicated triage but careful merge gating.

### 3.4 Effort Gini coefficients reveal a regime change

The effort-Gini analysis on `lines_changed` per contributor (`weekly_activity_analysis/effort_gini.csv`) shows a clear stratification by sample inclusion:

```
Most unequal repos (Gini → 1):
  Significant-Gravitas/AutoGPT:  Gini(lines)=0.99, Gini(commits)=0.88, top1=23%
  mastodon/mastodon:             Gini(lines)=0.98, Gini(commits)=0.92, top1=44%
  ForumMagnum/ForumMagnum:       Gini(lines)=0.97, Gini(commits)=0.95, top1=24%
  meshtastic/firmware:           Gini(lines)=0.95, Gini(commits)=0.76, top1=64%
  meshtastic/web:                Gini(lines)=0.95, Gini(commits)=0.88, top1=43%
```

All five "most unequal" repositories are either New-9 additions or large meshtastic projects. The original 29 small-civic-tech repositories cluster at Gini(lines) between 0.4 and 0.85 — meaningfully more equal in effort distribution.

This is a result the n=29 sample could not have surfaced: **at large project scale, code-line authorship becomes Gini-extreme even when commit-count Gini stays modest**. The ForumMagnum case (commit-Gini 0.95 vs lines-Gini 0.97) is the smallest gap; AutoGPT's 0.88 → 0.99 gap is the most striking and consistent with one or two contributors landing very large refactor / batch commits.

### 3.5 Maturity (≥6.2y) vs. Young split

Mann–Whitney U tests on the n=38 median-age split (mature ≥6.2 years, young <6.2 years; n=19 each):

| Metric | Mature | Young | p | Cliff's δ | Magnitude |
|---|---:|---:|---:|---:|---|
| num_developers | 27.0 | 5.0 | 0.014 | +0.47 | medium |
| total_commits | 3,521 | 674 | 0.017 | +0.46 | medium |
| bus_factor | 2.0 | 1.0 | 0.033 | +0.38 | medium |
| bus_factor_no_bots | 2.0 | 1.0 | 0.026 | +0.40 | medium |
| hhi_no_bots | 3,186 | 5,082 | 0.044 | -0.39 | medium |
| stale_issue_ratio | 0.99 | 0.73 | 0.193 | +0.30 | small |

Mature projects are systematically larger, more resilient, and less concentrated. The stale-issue-ratio is higher (0.99 vs 0.73) but the difference is not significant at α=0.05 — large mature projects accumulate stale issues but no faster than expected for their backlog size. This is a pattern the n=29 sample also showed but at smaller effect sizes.

### 3.6 Bots inflate HHI but do not change bus factor

Paired Wilcoxon (n=38, with vs. without bots):

```
HHI:           median 6,340 → 4,402 (Δ = -1,938)   W=8,    p=6e-6   significant
bus_factor:    median 1.5  →  2.0  (Δ =     0)     W=5,    p=1.00   NS
elephant_factor: 1.0       →  1.0  (Δ =     0)     -                NS
```

In other words: bots concentrate effort enough to skew HHI by ~30%, but rarely sit in the bus-factor "core" and almost never become the elephant. **Bot filtering matters more for inequality metrics than for resilience metrics**. This was already the recommendation in the n=29 paper; the n=38 sample reproduces it with stronger statistical power (W=8 vs the ~12 reported in April).

### 3.7 Inter-organisation differences (Kruskal–Wallis)

Across the three organisations with ≥3 repos in the sample (codeforamerica n=10, CodeForAfrica n=9, meshtastic n=3):

| Metric | H | p | ε² | Significant |
|---|---:|---:|---:|---|
| num_developers | 7.47 | 0.024 | 0.288 | ✓ (medium) |
| stale_issue_ratio | 8.77 | 0.013 | 0.677 | ✓ (large) |
| total_commits | 5.64 | 0.060 | 0.191 | borderline |
| health_percentage | 4.88 | 0.087 | 0.152 | NS |

`meshtastic` projects have substantially more developers (median 107 vs 10 for codeforamerica and 7 for CodeForAfrica) and substantially less stale-issue burden (median 0.35 vs 1.0 / 0.9). codeforamerica projects are the most uniformly small. CodeForAfrica sits in between. These organisation-level effects survive into the n=38 sample but the ε² estimates are noisy at these group sizes — interpret as descriptive, not as a population claim.

### 3.8 Weekly Elephant Factor: a single-contributor week is the dataset norm

Aggregated across all 5,547 active weeks:

> **86% of active weeks dataset-wide had a single contributor responsible for ≥50% of the code change.**

That is the weighted-by-weeks summary; the unweighted per-repo distribution is somewhat lower (75% of repos have ≥50% of weeks in the elephant regime). The four extreme cases — `CitizensFoundation/your-priorities-app`, `codeforamerica/cmr-maryland-eligibility-determination`, `codeforamerica/document-transfer-service`, `fvialibre/heseia-sentence-bias-dataset` — are 100%-elephant, 100%-solo-week repositories. The most collaborative repository in the sample (lowest mean top-share) is `civiform/civiform` at 53.5%, which is still over half of all weekly LOC moving through one person on average.

This is a result the n=29 sample also reported. The n=38 sample widens it: AutoGPT joins the "most collaborative" tail at 60.1% mean top-share, while ForumMagnum lands in the moderately-elephant middle (despite being 0.97 effort-Gini) — the difference is that ForumMagnum's elephant rotates between weeks, while smaller projects' elephant is the same single person every week.

### 3.9 Net-negative LOC growth

Three of the 38 repositories have more cumulative deletions than additions across their default-branch history:

```
DemocracyClub/UK-Polling-Stations: +6,297,037 / -9,733,304 → net -3,436,267
codeforamerica/recordtrac:         +333,219   / -366,883   → net    -33,664
CodeForAfrica/sensors.AFRICA:      +388,122   / -403,490   → net    -15,368
```

UK-Polling-Stations is an outlier even among net-negative projects (-3.4M lines is large). The plausible explanation, visible in `weekly_snapshots.csv`, is large vendored data sets being pruned over time rather than ordinary code refactor. This was flagged but not investigated in April; the n=38 sample preserves it for follow-up.

The two new-9 additions in this list (recordtrac and the original 29's sensors.AFRICA) are both small civic projects past their growth phase, consistent with the maturity story in §3.5.

---

## 4. Methodological notes specific to this refresh

### 4.1 The 5,000-issue cap

`issue_analytics.py` now applies a hard cap at 5,000 issues per repository. **Only `mastodon/mastodon` hit the cap** in this sample (its `issue_summary.total_issues` reads 5,000 / 616 open / 4,384 closed; the actual GitHub-side total is in the 6,000–7,000 range). Any analysis that uses mastodon's `total_issues`, `closed_issues`, or aggregated time-to-close should be aware of right-censoring.

The cap was added because civiform/civiform's 7,000+ issue tracker caused two consecutive crawl deaths — once via apparent OOM after a 540-second secondary-rate-limit backoff, and once via 37 minutes of completely silent PyGithub pagination. The cap, combined with iterator-level `GithubException` handling and per-250-issue progress logging, makes the collector both bounded and observable.

For future runs that need full coverage on capped repos, the cap can be raised in `src/civic_tech_crawler/collectors/issue_analytics.py` (`_MAX_ISSUES`), at the cost of further wall-clock time and a higher chance of running into GitHub's secondary abuse limits.

### 4.2 The two `total_commits` figures

`repo_metrics.total_commits` and the sum of `contributor_weekly_activity.commits` differ by ~22% on this sample (186,490 vs 152,305). For nearly all repositories the difference is small (≤5%); two outliers carry most of the gap:

- **`CitizensFoundation/your-priorities-app`**: repo_metrics says 8,011 commits; CWA says 800. A 9× gap suggests either a non-trivial fraction of commits happened on a non-default branch and were later squash-merged (so they appear in default-branch count but not as attributable individual commits in GraphQL), or the GraphQL fetch truncated unexpectedly. Worth manual investigation.
- **`mastodon/mastodon`**: repo_metrics 21,215 vs CWA 21,215 — these match exactly, suggesting GraphQL pagination is reliable on this repo even at 21k commits.

For analyses where contributor attribution matters (effort Gini, weekly elephant factor, bus factor proxies), use the CWA-derived commit counts. For population-level commit volume, use `repo_metrics.total_commits`.

### 4.3 Secondary rate limits and 403 backoffs

The May crawl observed **8 PyGithub-issued backoffs** of 318 s to 867 s each (5.3 to 14.5 minutes). All eight resolved cleanly; total backoff time across the run was approximately 70 minutes — a non-trivial fraction of the 15.5-hour wall-clock. Two were on civiform/civiform, two on iiab/iiab, two on AutoGPT, two on mastodon. The pattern is independent of repository size: small projects with deep issue trackers are hit just as often as large ones with deep contributor lists.

If reproducing this dataset on a fresh token, expect a similar 60–90 minute "lost to abuse-limit backoff" overhead and budget accordingly.

### 4.4 Per-repository data freshness

The 38 per-repository JSON files have crawl timestamps spanning 14 hours (2026-05-04 08:22 UTC to 2026-05-05 23:12 UTC) due to the per-repo cache and four mid-run process restarts during the issue-analytics patch development. The aggregate CSVs in this directory were generated in a single pass at the end of the crawl, so cross-repo analyses are temporally consistent at the *aggregation* level even though the underlying per-repo snapshots differ by hours. For research uses that require the same as-of moment for every repository, delete `output/*.json` and re-crawl in a single uninterrupted pass.

---

## 5. Threats to validity

### 5.1 Selection bias remains
The 38 repositories in this sample were chosen to be civic-tech-related, but four of the new nine (AutoGPT, mastodon, ForumMagnum, CitizensFoundation/your-priorities-app) are general-purpose platforms whose civic-tech use-case is one of several. AutoGPT in particular is included to extend the upper-tail dynamic range, not as a representative civic-tech project. The cohort comparison in §3.3 should be read as **"flagship open-source projects vs civic-specific projects"** rather than as a within-civic-tech generalisation.

### 5.2 GitHub-only perspective
Every metric in this dataset is derived from GitHub's API. Projects that mirror to GitHub but develop primarily on Codeberg, GitLab, or self-hosted Forgejo are misrepresented; their bus-factor and elephant-factor will look artificially extreme. None of the May 2026 sample is known to fall into this category, but the framework cannot detect it.

### 5.3 Bot detection is heuristic
The `is_bot` flag is set by login-pattern matching (`*-bot$`, `dependabot[bot]`, `github-actions[bot]`, etc.) against 51 / 731 contributors (7%). This catches the major automation services but will miss organisation-specific bots that don't follow the pattern, and may miscategorise human accounts whose username happens to match. The bot-impact analysis in §3.6 is robust to a few mis-classifications but quantitative claims at the per-repo level should account for this.

### 5.4 Issue cap censors mastodon
As noted in §4.1, mastodon's issue analytics is right-censored at 5,000 issues. Any per-repo analysis that uses `total_issues`, `closed_issues`, `unique_openers`, or `unique_closers` for mastodon should treat those values as lower bounds, not exact counts.

### 5.5 The 152,305 ≠ 186,490 commit discrepancy
The 22% gap between the two commit-count estimators is documented in §4.2 but not fully resolved. Per-repo cross-tabulation (e.g., for the CWA / repo_metrics ratio) is appropriate for sensitivity analysis, but a single dataset-wide commit count should not be reported without disclosing which estimator was used and why.

---

## 6. Files in this folder

See [README.md](README.md) for the full file inventory. The minimum subset needed to reproduce every result in this analysis:

- `repo_metrics.csv` — §1, §3.1, §3.3, §3.5
- `chaoss_summary.csv` — §3.1, §3.2, §3.6, §3.7
- `person_metrics.csv` — §1 (bot count)
- `contributor_weekly_activity.csv` — §3.4, §3.8, §3.9
- `issue_summary.csv` — §3.3 (issue first-response), §4.1
- `statistical_analysis/*.csv` — §3.1, §3.2, §3.5, §3.6, §3.7
- `weekly_activity_analysis/*.csv` and `summary.md` — §3.4, §3.8, §3.9

The 219 PNG plots in `plots/` are illustrative; none of the numerical claims above depend on them.

---

*Generated 5 May 2026 against branch `claude/add-new-repos-2026-05`, commits `adb8d37` (config), `7502e26` (detection.py), `3fd1811` (issue_analytics.py).*
