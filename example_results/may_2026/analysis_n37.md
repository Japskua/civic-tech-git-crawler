# Academic analysis of the n=37 May 2026 refresh

**Companion writeup for `example_results/may_2026/`. All numbers were computed against the May 2026 fresh recrawl on the `claude/full-recrawl-n37-2026-05` branch, with burstiness recomputed from `weekly_snapshots.csv` to fix coverage of the original `/stats/commit_activity`-derived metric.**

This snapshot is the basis for the rewritten `paper_draft.md` at the repository root. The paper expands on the analysis below; this file gives a faster, more methodologically explicit reading geared toward readers who want to understand the relationship between the n=29 paper, the n=37 sample, and the burstiness-coverage methodological correction.

---

## 1. Sample composition

The dataset extends the original n=29 civic-tech sample by 8 projects chosen to widen the dynamic range on age, scale, and contributor breadth. AutoGPT, which was crawled exploratorily in an earlier n=38 snapshot, is excluded from this canonical dataset because its design intent (general-purpose autonomous AI agent framework) does not satisfy the paper's civic-tech selection criterion. See `paper_draft.md` §3.2 for the per-repo justification of the eight included additions and the AutoGPT exclusion rationale.

| Repository | Stars | Commits | First commit | Notes |
|---|---:|---:|---|---|
| `mastodon/mastodon` | 49,930 | 21,215 | 2016-02-20 | Largest contributor base; federated social infrastructure |
| `ForumMagnum/ForumMagnum` | 706 | 52,222 | 2012-08-23 | Largest commit count; deliberation platform (LessWrong / EA Forum) |
| `okfde/froide` | 409 | 7,888 | **2011-04-12** | Oldest project; German freedom-of-information platform |
| `openplans/shareabouts` | 283 | 1,956 | 2011-10-27 | Civic mapping (older project) |
| `codeforamerica/recordtrac` | 60 | 2,570 | 2013-03-28 | Records-request tracking; net-negative LOC trajectory |
| `CitizensFoundation/your-priorities-app` | 142 | 8,011 | 2014-08-22 | Deliberation platform |
| `CodeForAfrica/actNOW` | 4 | 2,111 | 2021-04-19 | Civic-action tool (low-star end of range) |
| `mysociety/ceuk-marking` | 0 | 674 | 2022-12-13 | UK climate-emergency local-council scoring (smallest) |

Combined with the original 29 civic-tech projects this gives n=37 spanning 16 organisations, 16 primary languages, **15 years of project history (2011–2026)**, and a star range of 0 to 49,930 (5 orders of magnitude). The expanded sample is wide enough to test extrapolation of the original paper's findings to substantially larger and substantially older civic-tech projects.

---

## 2. Dataset summary

```
total_repositories         : 37
unique_organisations       : 16
unique_primary_languages   : 16
total_contributors         : 703
  human_contributors       : 654
  bot_contributors         : 49     (6.98% of population)
total_commits (repo)       : 178,099
total_commits (CWA)        : 162,033
total_stars                : 63,564
total_forks                : 11,308
repos_with_ci_cd           : 31 / 37   (84%)
repos_with_cloud_signals   : 27 / 37   (73%)
repos_with_ai_ml_signals   :  3 / 37   (8%)
repos_with_osi_license     : 12 / 37   (32%)
median_age_years           : 6.3
```

Distributional summaries appear in `statistical_analysis/descriptive_statistics.csv`. The sample is highly skewed across nearly every metric: stars range 0 → 49,930 (median 9), commits 9 → 52,222 (median 1,272), num_developers 1 → 414 (median 11). Shapiro–Wilk normality tests on 12 key metrics (`statistical_analysis/normality_tests.csv`) reject normality at α=0.05 for 11 of 12. All inferential analyses use non-parametric methods.

---

## 3. Headline statistical results

### 3.1 The bus-factor ↔ HHI mechanism is robust to sample expansion

The relationship between effort concentration (HHI) and resilience (bus factor), excluding bots in both:

| Sample | n | ρ (zero-order) | ρ (partial, controlling num_developers) | Interpretation |
|---|---:|---:|---:|---|
| n=29 paper original | 29 | −0.935 | −0.832 | Robust |
| **n=37 (this dataset)** | **37** | **−0.920** | **−0.872** | **Robust, slightly stronger after size control** |

Interpretation: as expected, projects with more concentrated effort (higher HHI) have lower bus factor. The relationship is mechanically near-tautological in direction but the *strength* is informative. At n=37 the partial correlation strengthens (−0.832 → −0.872), meaning the underlying mechanism survives even when a wider range of project sizes is included. This is the strongest evidence in the dataset that the paper's central concentration-of-effort framing is not an artefact of the original sample's size truncation.

### 3.2 Bots inflate HHI but do not change bus factor

Paired Wilcoxon signed-rank tests across all 37 repositories (`wilcoxon_bot_impact.csv`):

```
HHI:           median 6,344 → 4,357 (Δ = -1,987)   W=2,    p=7e-6   significant
bus_factor:    median 2.0  →  2.0  (Δ =     0)     W=5,    p=1.00   NS
elephant_factor: 1.0       →  1.0  (Δ =     0)     -                NS
```

The original n=29 paper reported the same direction with p=6e-5 on a smaller sample. At n=37 the test is more powerful (more repositories with bots) and the p-value drops by an order of magnitude. **Bot filtering is essential for HHI-based concentration analysis but unnecessary for bus-factor and elephant-factor analyses** — the wider sample reproduces the original methodological recommendation with stronger statistical evidence.

### 3.3 Burstiness ↔ stale-issue-ratio attenuates after the coverage fix

This is the most important result of the n=37 expansion, both substantively and methodologically. The original n=29 paper reported:

> The robust correlation between development burstiness and stale issue ratio (ρ = 0.685, surviving partial correlation controlling for team size, ρ_partial = 0.553)

That correlation was computed on n=17 — the only repos in the n=29 sample for which both metrics were populated. Burstiness coverage was limited because GitHub's `/stats/commit_activity` endpoint is asynchronously computed and frequently times out; only 17 of 29 repos returned in time. The 17 were not a random subset — they were the ones GitHub happened to have stats cached for, which correlates with project activity.

In this snapshot we recompute burstiness from `weekly_snapshots.csv` (derived from a separate GraphQL bulk commit fetch), raising coverage to 37 of 37. Re-examining the burstiness ↔ stale-issue-ratio correlation:

| Sample | Coverage | n pairs | ρ (zero-order) | p | FDR? | ρ partial | p partial |
|---|---:|---:|---:|---:|---|---:|---:|
| n=29 paper | /stats endpoint | 17 | 0.685 | 0.002 | Yes | 0.553 | (paper) |
| n=37 recomputed | weekly_snapshots | 26 | **0.444** | 0.023 | **No** | **0.393** | 0.047 |

The relationship persists in direction and remains significant under uncorrected α=0.05 testing, but **it does not survive Benjamini–Hochberg FDR correction at the wider sample, and the partial correlation is borderline at uncorrected α=0.05.** The 8 repositories that gained burstiness measurements through the recompute carry weaker burstiness↔stale signal than the original 17 — consistent with positive selection bias in the original paper: the repos GitHub had cached stats for were disproportionately those with the strongest burstiness↔stale relationship.

This is not a refutation of the original finding. The relationship is real and moderate (ρ ≈ 0.44 is well above zero), and it survives partial-correlation controls without sign reversal. But the original ρ=0.685 should be interpreted as an upper bound conditional on a biased subset, not a population estimate.

### 3.4 Cohort comparison: AutoGPT exclusion does not change the picture

We split the n=37 sample into the **8 May extensions** (mastodon, ForumMagnum, okfde/froide, openplans/shareabouts, recordtrac, actNOW, your-priorities-app, ceuk-marking) and the **29 original civic-tech projects** to test whether the new repos differ systematically.

| Metric (median) | Extension (n=8) | Core (n=29) | Mann–Whitney p | Cliff's δ | Interpretation |
|---|---:|---:|---:|---:|---|
| stars | 213 | 7 | 0.062 | +0.44 | medium (NS) |
| forks | 70 | 4 | **0.045** | **+0.47** | medium ✓ |
| total_commits | 5,229 | 603 | **0.008** | **+0.60** | large ✓ |
| num_developers | 17 | 11 | 0.37 | +0.22 | small (NS) |
| health_percentage | 37 | 50 | 0.43 | −0.19 | small (NS) |
| bus_factor_no_bots | 1.5 | 2.0 | 0.94 | −0.02 | negligible (NS) |
| HHI no-bots | 5,798 | 4,092 | 0.70 | +0.10 | negligible (NS) |
| burstiness_cv | 1.35 | 0.91 | 0.48 | +0.18 | small (NS) |
| stale_issue_ratio | 1.00 | 0.85 | 0.081 | +0.43 | medium (NS, borderline) |
| Median issue first response (h) | 18 | 46 | 0.76 | +0.09 | negligible (NS) |
| Median PR review turnaround (h) | 27 | 3 | 0.17 | +0.40 | medium (NS) |

Differences between cohorts are concentrated on **scale** (commits, forks) rather than on **sustainability** (bus factor, HHI, health). The 8 new repos are systematically larger and more popular but no less resilient by the paper's headline metrics. Combined with §3.1's robustness result, this supports the conclusion that the paper's bus-factor ↔ HHI ↔ effort-concentration framework extrapolates to substantially larger civic-tech projects.

The one borderline difference is `stale_issue_ratio` (extension median 1.00 vs core 0.85, p=0.08 Mann–Whitney, Cliff's δ=+0.43 medium). The 8 extension repos have less-actively-maintained issue trackers despite being larger. This is consistent with the older mature projects in the extension set (okfde/froide, openplans/shareabouts, recordtrac) having accumulated long-tail issue backlogs.

### 3.5 Maturity (≥6.3 years) vs Young split

Mann–Whitney U tests on the median-age split (n=19 mature, n=18 young; `maturity_analysis.csv`):

| Metric | Mature median | Young median | p | Cliff's δ | Magnitude |
|---|---:|---:|---:|---:|---|
| num_developers | 27 | 5 | **0.004** | +0.55 | large |
| total_commits | 3,521 | 638 | **0.009** | +0.51 | large |
| bus_factor_no_bots | 2 | 1 | **0.036** | +0.38 | medium |
| hhi_no_bots | 3,186 | 5,206 | **0.040** | −0.40 | medium |
| stale_issue_ratio | 0.99 | 0.75 | 0.143 | +0.34 | medium (NS) |
| burstiness_cv | 1.12 | 0.88 | 0.183 | +0.26 | small (NS) |
| health_percentage | 50 | 46 | 0.124 | +0.29 | small (NS) |

Mature projects are systematically larger, more resilient, and less concentrated. **The bus_factor effect that was borderline non-significant (p=0.053) at n=29 reaches significance at n=37 (p=0.036)**, with a medium effect size. This is one of the cleanest cases in the dataset where a wider sample sharpens an existing finding.

### 3.6 Effort concentration regime change at scale

`weekly_activity_analysis/effort_gini.csv` reports the Gini coefficient of total lines changed per contributor per repository. A Gini of 0 indicates perfectly equal effort distribution; 1 means one person did everything.

The five most unequal repositories at n=37:

| Repo | Gini(lines) | Gini(commits) | Top-1 contributor | Top-1 share |
|---|---:|---:|---|---:|
| mastodon/mastodon | 0.98 | 0.92 | `Gargron` | 44% |
| ForumMagnum/ForumMagnum | 0.97 | 0.95 | `jimrandomh` | 24% |
| meshtastic/firmware | 0.95 | 0.76 | `Jorropo` | 64% |
| meshtastic/web | 0.95 | 0.88 | `danditomaso` | 43% |
| okfde/froide | 0.94 | 0.95 | `stefanw` | 80% |

All five are in or above the 5,000-commit range. The Gini-extremity profile (≥0.95 on lines, with single-person contributing 24-80% of all lines) is consistent across the high-scale projects regardless of the headline contributor count. **This is a regime that is essentially absent in the original n=29 sample**, where the highest line-Gini was around 0.85.

Below ~5,000 commits the line-Gini distribution flattens out: the 5 most equal repositories at n=37 are all in the 1,000-commit-or-less range. The implication is not that scaling causes inequality but that line-Gini saturates near 1 at large scale even when commit-Gini stays moderate. This is consistent with mega-commits — large refactor or batch-merge commits that move thousands of lines per author event — being the dominant pattern at flagship scale.

### 3.7 Weekly elephant factor: 83% of active weeks are dominated by one contributor

Aggregated across 22,486 contributor-weeks at n=37:

> **83% of active weeks dataset-wide had a single contributor responsible for ≥50% of the code change.**

The original n=29 paper reported 86% on the corresponding April refresh; this figure is essentially unchanged. The change from 86% to 83% is consistent with the 8 added repositories including a few large multi-contributor projects (mastodon, ForumMagnum, okfde/froide) that pull the weighted average down slightly. The result is robust: the typical civic-tech project, weighted by active weeks, is dependent on a single contributor each week.

The five least-elephant-dominated repositories at n=37 — `civiform/civiform` (51% mean top-share), `codeforamerica/vita-min` (55%), `CodeForAfrica/actNOW` (61%), `mastodon/mastodon` (62%), `meshtastic/firmware` (65%) — are the only repositories where weekly contribution is genuinely shared rather than rotating between solo authors. Note these are all at substantial team scale (≥5 contributors); below that, single-author weeks are the norm.

### 3.8 Net-negative LOC trajectories (3 of 37)

Three repositories show more cumulative deletions than additions across their full default-branch history:

```
DemocracyClub/UK-Polling-Stations: +6,297,063 / -9,733,304 → net -3,436,241
codeforamerica/recordtrac:         +333,219   / -366,883   → net    -33,664
CodeForAfrica/sensors.AFRICA:      +388,122   / -403,490   → net    -15,368
```

All three are above the median age (6.3 years) and represent the dataset's clearest examples of mature-maintenance projects past the growth phase. UK-Polling-Stations is an outlier even within net-negative projects — the −3.4M imbalance is concentrated in two 2016 weeks that each removed ≈2.95M lines, consistent with a one-off purge of committed generated data. The two CodeForAfrica/codeforamerica entries have smaller, more evenly distributed deletion patterns, suggesting ordinary refactor.

---

## 4. Methodological notes

### 4.1 Burstiness recompute

`burstiness_cv` in `chaoss_summary.csv` is the **trailing-52-week** coefficient of variation of weekly commit counts, derived from `weekly_snapshots.csv`. This recomputed value supersedes whatever GitHub's `/stats/commit_activity` returned (which timed out for 32 of 37 repos in the original crawl). Validation on the 5 repos where both metrics were available shows the trailing-52-week CV from `weekly_snapshots` agrees with the `/stats`-derived value within ±0.07 for 4 of 5, with one larger discrepancy (CodeForAfrica/ui: 1.20 vs 0.88) attributable to subtly different 52-week window alignments.

A second column, `burstiness_cv_full_history`, applies the same CV computation to the full default-branch history. This is a richer alternative not subject to the 52-week truncation bias of the original metric — for projects with long histories it may be a more meaningful measure. The paper uses the trailing-52-week metric for the §4.4 burstiness↔stale-issue-ratio analysis to maintain comparability with the n=29 paper's metric definition.

### 4.2 The 5,000-issue cap

`issue_analytics.py` caps total issues per repository at 5,000 to bound runtime on very large issue trackers. **Only `mastodon/mastodon` hit the cap** in this sample. Its `issue_summary.total_issues = 5,000` should be treated as right-censored for any analysis that uses `total_issues`, `closed_issues`, or aggregated time-to-close metrics for mastodon specifically.

### 4.3 The two `total_commits` figures

`repo_metrics.total_commits` (178,099) and the sum of `contributor_weekly_activity.commits` (162,033) differ by ~9% on this sample. Most of the gap is a single repo: `CitizensFoundation/your-priorities-app` reports 8,018 commits via repo_metrics but only 1,000 attributable in CWA. This 8× discrepancy suggests a non-trivial fraction of commits live on non-default branches and are squash-merged at unattributable points. For analyses where contributor attribution matters (effort Gini, weekly elephant factor, partial correlations on contributor-derived metrics), use the CWA-derived counts. For population-level commit volume, use `repo_metrics.total_commits`.

### 4.4 Per-repository data freshness

The 37 per-repository JSON files have crawl timestamps spanning 28 hours (2026-05-05 09:18 UTC to 2026-05-06 13:44 UTC) due to four sandbox-imposed process kills and respawns during the crawl. The aggregate CSVs in this directory were generated in a single pass after all 37 repos completed, so cross-repo analyses are temporally consistent at the *aggregation* level. For research uses requiring identical as-of moments per repository, delete `output/*.json` and re-run with the auto-respawn wrapper in a single uninterrupted session.

### 4.5 Stats endpoint resilience

The crawler now self-heals when `/stats/commit_activity` is unavailable: `commit_history` is collected before `chaoss_metrics`, and chaoss derives `weekly_commits` from the last 52 `weekly_snapshots` if the stats endpoint times out. This means future crawls do not need the recompute step. The `scripts/recompute_burstiness.py` script remains useful for retrofitting older snapshots.

---

## 5. Threats to validity

### 5.1 Selection bias remains
The 37 repositories were chosen to represent civic technology, but several judgment calls underlie that selection. mastodon and ForumMagnum are platforms with substantial non-civic uses; their inclusion reflects the paper's working definition of civic technology as software with a public-interest design intent rather than software whose only or primary use is civic. AutoGPT was crawled exploratorily but excluded from the canonical dataset because it does not satisfy that criterion (general-purpose AI agent framework). Other reasonable definitions would include or exclude different subsets.

### 5.2 GitHub-only perspective
Every metric is derived from GitHub's API. Projects that mirror to GitHub but develop primarily on Codeberg, GitLab, or self-hosted Forgejo would be misrepresented; their bus-factor and elephant-factor would look artificially extreme.

### 5.3 Bot detection is heuristic
The `is_bot` flag is set by login-pattern matching against 49 of 703 contributors (7%). This catches the major automation services but will miss organisation-specific bots that don't follow the pattern, and may miscategorise human accounts whose username happens to match. The bot-impact analyses in §3.2 are robust to a few mis-classifications but per-repo claims should account for this.

### 5.4 Issue cap censors mastodon
Mastodon's issue analytics is right-censored at 5,000 issues. Any per-repo analysis that uses `total_issues`, `closed_issues`, `unique_openers`, or `unique_closers` for mastodon should treat those values as lower bounds, not exact counts.

### 5.5 The 178,099 ≠ 162,033 commit discrepancy
The 10% gap between the two commit-count estimators is documented in §4.3. Most of the discrepancy is `CitizensFoundation/your-priorities-app` alone (8,018 vs 1,000). This is flagged but not investigated in this snapshot.

### 5.6 The burstiness recompute changes the metric, slightly
Although the recomputed `burstiness_cv` agrees with the original `/stats/commit_activity`-derived metric within ±0.07 in 4 of 5 cases where both are available, the two are not strictly identical. Replication of the n=29 paper's burstiness numbers would require either the original `/stats` data (no longer reliably retrievable for the affected repositories) or accepting the small definitional difference as an additional source of uncertainty. The paper's substantive conclusion — that the burstiness↔stale-issue-ratio relationship attenuates at the wider sample — is robust to this uncertainty.

---

*Generated 6 May 2026 against branch `claude/full-recrawl-n37-2026-05`.*
