# May 2026 Refresh (n = 38)

This directory contains a **full re-crawl on 4–5 May 2026 of an expanded 38-repository civic-tech dataset**. It supersedes the 29-repository [April 2026 refresh](../april_2026_refresh/) by adding nine substantially larger or older projects: **ForumMagnum, AutoGPT, mastodon, okfde/froide, openplans/shareabouts, codeforamerica/recordtrac, CodeForAfrica/actNOW, CitizensFoundation/your-priorities-app, mysociety/ceuk-marking**.

The April refresh remains the dataset cited in the paper's Sections 4.1–4.7. This May refresh is a **broader, more heterogeneous sample** that brings in well-known open-source projects (AutoGPT at 184k stars, mastodon at 50k) alongside very small civic experiments (mysociety/ceuk-marking at 0 stars). It is intended both as a robustness check on the n=29 findings and as the dataset for any follow-up work that needs the wider distribution. See `analysis_n38.md` in this folder for the accompanying writeup.

---

## What's new vs. April 2026

| Addition | Why |
|---|---|
| **9 new repositories** (24% of the dataset) | Adds high-visibility projects (AutoGPT, mastodon, ForumMagnum) and three older mature codebases (okfde/froide from 2011, openplans/shareabouts from 2011, codeforamerica/recordtrac from 2013), expanding the dynamic range on every metric |
| **`detection.py` 422-tolerance** | GitHub's REST `/topics` endpoint started returning 422 *"Could not resolve to a node with the global id of …"* for several repositories during the May crawl. The crawler now catches `GithubException`, logs a warning, and continues with empty topics rather than aborting the whole repository |
| **`issue_analytics.py` runtime cap** | Civiform/civiform (~7,000 issues) caused two consecutive crash modes in earlier crawl attempts: a silent SIGKILL after a 403 secondary-rate-limit backoff and 37 minutes of completely silent PyGithub pagination. The collector now caps total issues at 5,000, emits a progress line every 250 issues, and catches `GithubException` at the iterator's `next()` so partial data is preserved on irrecoverable pagination failure |

---

## Data Collection Details

| | |
|---|---|
| **Date collected** | 4–5 May 2026 (crawl spanned ~15.5 wall-clock hours) |
| **Configuration** | `config.example.yaml` (38 repositories from 17 GitHub organisations) |
| **Repositories** | 38 |
| **Organisations** | 17 (CodeForAfrica, codeforamerica, DemocracyClub, fvialibre, luftdata, markov-root, codeforjapan, meshtastic, civiform, iiab, ForumMagnum, Significant-Gravitas, mastodon, okfde, openplans, CitizensFoundation, mysociety) |
| **Primary languages** | 16 (Python, JavaScript, Ruby, TypeScript, Java, HCL, Jupyter Notebook, SCSS, PHP, Astro, C++, CSS, Dockerfile, HTML, Jinja, Kotlin) |
| **Contributors (`person_metrics`)** | 731 total (680 human, 51 bot) |
| **Contributors (`contributor_weekly_activity`)** | 2,684 unique |
| **Total commits (sum across `repo_metrics`)** | 186,490 |
| **Total commits (sum of `contributor_weekly_activity.commits`)** | 152,305 |
| **Lines added (cumulative)** | 48,549,707 |
| **Lines removed (cumulative)** | 38,227,850 |
| **Pull requests** | 85,603 |
| **Issues** | 27,761 |
| **Tags** | 2,786 |
| **Earliest commit** | 2011-04-12 (`okfde/froide`) |
| **Median project age** | 6.2 years |
| **Crawl wallclock** | ~15.5 h (4 process restarts during development of the issue-analytics patch — see "Implementation history" below) |

### Why two commit totals differ

The 186,490 figure comes from `repo_metrics.total_commits`, which is GitHub's per-repository commit count for the default branch (returned by the `/commits` endpoint with `per_page=1` and reading the `Link: rel="last"` header — the cheapest exact count available).

The 152,305 figure is the sum of `contributor_weekly_activity.commits`, which uses the GraphQL bulk commit fetcher to attribute every commit to its (contributor, ISO-week) pair. It excludes a small number of commits where the contributor cannot be resolved (e.g. detached HEAD merges, vendored history, GraphQL truncation on heavy repos).

Use `repo_metrics.total_commits` when you want the canonical per-repo count; use the CWA-summed figure when you need contributor-resolved attribution.

### Why contributor counts differ between files

- `person_metrics.csv` (731 contributors) is built from the `/stats/contributors` endpoint, which summarises weekly contribution activity for default-branch commits linked to GitHub user accounts, plus a commit-history fallback (capped at 500 commits) for repositories where stats are unavailable.
- `contributor_weekly_activity.csv` (2,684 unique `contributor_id`s) is built from GraphQL over **every** commit on the default branch, with contributors keyed by GitHub login *or* author email when no login is linked. It therefore includes email-only authors that `stats/contributors` omits. The two files are consistent but describe slightly different populations; use `contributor_weekly_activity.csv` when you need the long tail of drive-by or anonymous contributors.

---

## Output Files

### Crawl data (same schema as April snapshot)

| File | Rows | Notes |
|---|---|---|
| `repo_metrics.csv` | 38 | Repository-level metrics |
| `person_metrics.csv` | 731 | Per-contributor metrics; includes `is_bot` flag |
| `temporal_summary.csv` | 38 | PR / tag / release counts |
| `chaoss_summary.csv` | 38 | 45+ CHAOSS and extended columns |
| `pull_requests.csv` | 85,603 | PR records |
| `tags.csv` | 2,786 | Git tags |
| `core_periphery.csv` | 285 | Per-contributor network role from PR-review collaboration graph |
| `weekly_snapshots.csv` | 5,547 | Weekly commit/contributor snapshots |
| `contributor_lifecycles.csv` | 2,852 | Per-contributor first/last commit, active/departed |
| `contributor_weekly_activity.csv` | 20,162 | Per-(contributor, ISO-week) commit + lines_added + lines_removed |
| `issue_records.csv` | 27,761 | Individual issue records (capped at 5,000 per repo — only `mastodon/mastodon` hit the cap) |
| `issue_summary.csv` | 38 | Aggregated issue analytics |
| `cross_project_overlap.csv` | 536 | Contributors active in multiple crawled repos |
| `full_results.json` | — | Complete nested data for all 38 repositories (52 MB) |
| `<owner>_<repo>/data.json` × 38 | — | Per-repository cache file, inside the repo's own folder |

### Per-repository folders (38)

Each repository has its own folder named `<owner>_<repo>/` containing:

- `repo_results.md` — at-a-glance metadata, key metrics table, main finding, and any caveats specific to that repo (e.g. mastodon's right-censored issue cap, your-priorities-app's commit-count discrepancy)
- `data.json` — full crawler output for the repository
- 5–6 PNG plots: `growth.png`, `weekly_activity.png`, `lifecycle.png`, `new_contributors.png`, `top_contributors.png`, plus `issue_trends.png` if the repo has issues

To rebuild these folders from a freshly-crawled `output/` (or from the flat layout this folder was generated from), run `python scripts/build_repo_folders.py` after first having `cp -r output/* example_results/may_2026_refresh/` and the analysis scripts.

| Folder | Stars | Commits | Bus factor | Top contributor |
|---|---:|---:|---:|---|
| [`CitizensFoundation_your-priorities-app/`](CitizensFoundation_your-priorities-app/repo_results.md) | 142 | 8,011 | 1 | `rbjarnason` |
| [`CodeForAfrica_Dominion.AFRICA/`](CodeForAfrica_Dominion.AFRICA/repo_results.md) | 2 | 257 | 2 | `kilemensi` |
| [`CodeForAfrica_GenderGap.AFRICA/`](CodeForAfrica_GenderGap.AFRICA/repo_results.md) | 9 | 207 | 3 | `DavidLemayian` |
| [`CodeForAfrica_PromiseTracker/`](CodeForAfrica_PromiseTracker/repo_results.md) | 1 | 386 | 1 | `kelvinkipruto` |
| [`CodeForAfrica_academy.AFRICA/`](CodeForAfrica_academy.AFRICA/repo_results.md) | 0 | 359 | 2 | `kelvinkipruto` |
| [`CodeForAfrica_actNOW/`](CodeForAfrica_actNOW/repo_results.md) | 4 | 2,111 | 1 | `kilemensi` |
| [`CodeForAfrica_openAFRICA/`](CodeForAfrica_openAFRICA/repo_results.md) | 32 | 134 | 2 | `thepsalmist` |
| [`CodeForAfrica_outbreak.AFRICA/`](CodeForAfrica_outbreak.AFRICA/repo_results.md) | 1 | 246 | 2 | `kilemensi` |
| [`CodeForAfrica_sensors.AFRICA/`](CodeForAfrica_sensors.AFRICA/repo_results.md) | 23 | 1,180 | 3 | `kilemensi` |
| [`CodeForAfrica_ui/`](CodeForAfrica_ui/repo_results.md) | 2 | 10,966 | 2 | `kilemensi` |
| [`DemocracyClub_UK-Polling-Stations/`](DemocracyClub_UK-Polling-Stations/repo_results.md) | 36 | 8,767 | 2 | `symroe` |
| [`DemocracyClub_WhoCanIVoteFor/`](DemocracyClub_WhoCanIVoteFor/repo_results.md) | 44 | 3,521 | 2 | `symroe` |
| [`ForumMagnum_ForumMagnum/`](ForumMagnum_ForumMagnum/repo_results.md) | 706 | 52,222 | 4 | `jimrandomh` |
| [`Significant-Gravitas_AutoGPT/`](Significant-Gravitas_AutoGPT/repo_results.md) | 183,985 | 8,476 | 1 | `waynehamadi` |
| [`civiform_civiform/`](civiform_civiform/repo_results.md) | 124 | 7,768 | 3 | `gwendolyngoetz` |
| [`codeforamerica_asap_pdf/`](codeforamerica_asap_pdf/repo_results.md) | 46 | 1,024 | 1 | `lkacenja` |
| [`codeforamerica_cmr-maryland-eligibility-determination/`](codeforamerica_cmr-maryland-eligibility-determination/repo_results.md) | 1 | 9 | 1 | `victorSauceda` |
| [`codeforamerica_document-transfer-service/`](codeforamerica_document-transfer-service/repo_results.md) | 3 | 27 | 1 | `jamesiarmes` |
| [`codeforamerica_form-flow/`](codeforamerica_form-flow/repo_results.md) | 4 | 661 | 1 | `cram-cfa` |
| [`codeforamerica_honeycrisp-gem/`](codeforamerica_honeycrisp-gem/repo_results.md) | 7 | 1,108 | 4 | `hartsick` |
| [`codeforamerica_pya/`](codeforamerica_pya/repo_results.md) | 2 | 110 | 2 | `DrewProebstel` |
| [`codeforamerica_recordtrac/`](codeforamerica_recordtrac/repo_results.md) | 60 | 2,570 | 2 | `criscristina` |
| [`codeforamerica_tax-benefits-backend/`](codeforamerica_tax-benefits-backend/repo_results.md) | 3 | 358 | 3 | `jamesiarmes` |
| [`codeforamerica_tofu-modules-aws-serverless-database/`](codeforamerica_tofu-modules-aws-serverless-database/repo_results.md) | 0 | 67 | 1 | `jamesiarmes` |
| [`codeforamerica_vita-min/`](codeforamerica_vita-min/repo_results.md) | 34 | 7,232 | 4 | `bytheway875` |
| [`codeforjapan_BirdXplorer/`](codeforjapan_BirdXplorer/repo_results.md) | 11 | 754 | 2 | `yu23ki14` |
| [`fvialibre_edia/`](fvialibre_edia/repo_results.md) | 6 | 60 | 1 | `LMartinezEXEX` |
| [`fvialibre_heseia-sentence-bias-dataset/`](fvialibre_heseia-sentence-bias-dataset/repo_results.md) | 0 | 9 | 1 | `guidoivetta` |
| [`iiab_iiab/`](iiab_iiab/repo_results.md) | 1,855 | 12,100 | 1 | `holta` |
| [`luftdata_luftdata.se/`](luftdata_luftdata.se/repo_results.md) | 3 | 105 | 1 | `ebner` |
| [`markov-root_atlas/`](markov-root_atlas/repo_results.md) | 9 | 110 | 1 | `git@xfe.li` |
| [`mastodon_mastodon/`](mastodon_mastodon/repo_results.md) | 49,924 | 21,215 | 3 | `Gargron` |
| [`meshtastic_Meshtastic-Android/`](meshtastic_Meshtastic-Android/repo_results.md) | 1,584 | 2,170 | 1 | `jamesarich` |
| [`meshtastic_firmware/`](meshtastic_firmware/repo_results.md) | 7,411 | 7,768 | 3 | `Jorropo` |
| [`meshtastic_web/`](meshtastic_web/repo_results.md) | 757 | 2,170 | 1 | `danditomaso` |
| [`mysociety_ceuk-marking/`](mysociety_ceuk-marking/repo_results.md) | 0 | 674 | 1 | `struan` |
| [`okfde_froide/`](okfde_froide/repo_results.md) | 409 | 7,888 | 2 | `stefanw` |
| [`openplans_shareabouts/`](openplans_shareabouts/repo_results.md) | 283 | 1,956 | 1 | `mjumbewu` |

### Weekly activity analysis

Generated by `scripts/weekly_activity_analysis.py` against `contributor_weekly_activity.csv`.

| File | Description |
|---|---|
| `weekly_activity_analysis/weekly_elephant_factor.csv` | Per repo: mean top-contributor share per week, % elephant weeks, % single-contributor weeks |
| `weekly_activity_analysis/churn_ratio.csv` | Per repo: overall churn ratio (deletions / (additions+deletions)), net LOC delta, % deletion-heavy weeks |
| `weekly_activity_analysis/effort_gini.csv` | Per repo: Gini coefficient of `lines_changed` per contributor, Gini of `commits` per contributor, top1 share |
| `weekly_activity_analysis/summary.md` | Human-readable rundown of the most striking findings (now including AutoGPT / mastodon / ForumMagnum) |

### Statistical analysis

Generated by `scripts/statistical_analysis.py output/`.

| File | Rows | Description |
|---|---|---|
| `statistical_analysis/dataset_summary.csv` | 1 | Dataset-wide aggregates |
| `statistical_analysis/descriptive_statistics.csv` | 25 | Per-metric mean / median / IQR / std |
| `statistical_analysis/normality_tests.csv` | 12 | Shapiro–Wilk on every continuous metric |
| `statistical_analysis/spearman_correlations.csv` | 17 | Spearman ρ matrix |
| `statistical_analysis/spearman_p_values.csv` | 17 | Matching p-value matrix |
| `statistical_analysis/correlation_pairs_fdr.csv` | 136 | Pairwise correlations with Benjamini–Hochberg FDR control |
| `statistical_analysis/partial_correlations.csv` | 10 | Partial Spearman controlling for `num_developers` (project size) |
| `statistical_analysis/group_comparisons.csv` | 19 | Mann–Whitney U + Cliff's δ on CI/CD, Cloud, AI/ML, OSI-license groupings |
| `statistical_analysis/maturity_analysis.csv` | 11 | Mann–Whitney U on Mature (≥6.2y) vs Young splits |
| `statistical_analysis/org_kruskal_wallis.csv` | 7 | Kruskal–Wallis across organisations with ≥3 repos |
| `statistical_analysis/bot_impact.csv` | 38 | Per-repo bot/human breakdown and HHI with vs without bots |
| `statistical_analysis/wilcoxon_bot_impact.csv` | 3 | Paired Wilcoxon on HHI / bus / elephant factor with vs without bots |

### Visualizations

219 PNG plots, 5–6 per repository (where data exists), live inside each repo's folder:

- `<owner>_<repo>/growth.png` — cumulative commits + contributors over time
- `<owner>_<repo>/weekly_activity.png` — weekly commit volume
- `<owner>_<repo>/lifecycle.png` — contributor lifecycles (first→last commit per person)
- `<owner>_<repo>/new_contributors.png` — weekly new-contributor arrivals
- `<owner>_<repo>/issue_trends.png` — opens, closes, and backlog size over time (where issues exist)
- `<owner>_<repo>/top_contributors.png` — top 20 contributors by commit count

---

## Implementation history (May 4 crawl)

The crawl required five process attempts before completing successfully. All of these are reproduced (and patched) in the source tree on branch `claude/add-new-repos-2026-05`; the per-repo cache made resumption from each death cheap.

| Attempt | PID | Outcome |
|---|---|---|
| 1 | 2558 | Died at 09:18 UTC, SIGHUP from non-detached parent shell (10 repos saved). **Fix**: launch with `setsid nohup`. |
| 2 | (same chain) | Aborted on 9 consecutive repos because GitHub returned 422 from `/topics` on `repo.get_topics()`. **Fix**: catch `GithubException` in `detection.py`. |
| 3 | 2839 | Silent SIGKILL at 15:43 UTC during `civiform/civiform` issue analytics, after a 403 secondary-rate-limit backoff. Likely sandbox quota. (27 repos saved.) |
| 4 | 2466 | Looped silently for 37 minutes on `civiform/civiform` issue analytics — PyGithub's urllib3 requests do not log via the same logger that captures the rest of the crawler, so the silence was indistinguishable from a hang. **Fix**: `issue_analytics.py` now caps total issues at 5,000, emits a progress line every 250 issues, and catches `GithubException` at the iterator level. |
| 5 | 6749 | **Completed.** Survived a container restart partway through (thanks to `setsid`). 38 repos saved, 8 PyGithub backoffs survived, 1 issue cap hit (mastodon at 5,000), 0 repo crawl failures, 0 topic-fetch warnings. |

The two patches (`detection.py` and `issue_analytics.py`) are committed on branch `claude/add-new-repos-2026-05` and apply cleanly going forward.

---

## How to reproduce

```bash
# From repo root
git checkout claude/add-new-repos-2026-05
uv sync
export GITHUB_TOKEN=ghp_...        # public_repo scope; ~7-15 hours run time
uv run civic-tech-crawler --config config.example.yaml

# Then derive analyses
uv run python scripts/statistical_analysis.py output/
uv run python scripts/weekly_activity_analysis.py
uv run python scripts/visualize.py --output-dir output

# And copy into a refresh snapshot folder
cp -r output/ example_results/may_2026_refresh/
```

API budget: ~2,000 / 5,000 hourly REST and ~500 / 5,000 hourly GraphQL calls remained at end of the May crawl, so the run is well within a single token's quota for that day.
