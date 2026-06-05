# New AI-Related Signals & Values — 2026-06 vs 2026-05

A reference for cowriters. Everything below is **new in the 2026-06 dataset** and
absent from 2026-05. All AI-usage measures are a **lower bound** — only disclosed,
configured, or automated AI traces are detectable; inline autocomplete / chat-paste
usage leaves no artifact.

---

## 1. New output files

| File | Granularity | Contents |
|---|---|---|
| `ai_usage.csv` | 1 row / repo (56) | Per-repo AI-usage summary (§2) |
| `ai_signals.csv` | 1 row / signal (94 rows) | Every individual piece of AI evidence (§3) |
| `ai_usage_analysis/` | directory (7 files) | `adoption_summary.csv`, `tool_frequency.csv`, `provider_frequency.csv`, `signal_source_breakdown.csv`, `adoption_timeline.csv`, `adopter_vs_nonadopter.csv`, `summary.md` |

Also new in the analysis pass: per-repo `repo_results.md` files gained
**"AI-assisted development"** and **"Ships LLM product feature"** rows.

---

## 2. `ai_usage.csv` — columns (data dictionary)

| Column | Type | Meaning |
|---|---|---|
| `repo_full_name` | str | owner/repo |
| `dev_ai_detected` | bool | Any AI-assisted-development signal present |
| `dev_ai_tools` | list (`;`) | Distinct dev tools detected |
| `agent_config_files` | list (`;`) | Agent config files/dirs found |
| `ai_coauthored_commit_count` | int | Commits carrying an AI co-author trailer |
| `ai_authored_commit_count` | int | Commits authored by an AI agent bot |
| `commits_scanned` | int | Total commits walked (denominator) |
| `ai_commit_ratio` | float | (coauthored + authored) / commits_scanned |
| `ai_agent_pr_count` | int | PRs opened by AI agent bots |
| `ci_ai_workflows` | list (`;`) | Workflow files referencing an AI action |
| `review_bot_tools` | list (`;`) | AI review/comment bots on recent PRs |
| `first_dev_ai_date` | datetime | Earliest datable AI-dev signal (first appearance) |
| `product_llm_detected` | bool | Project ships LLM/GenAI functionality |
| `product_llm_providers` | list (`;`) | Distinct LLM providers |
| `product_llm_signals` | list (`;`) | Evidence strings for product-LLM detection |

---

## 3. `ai_signals.csv` — columns + controlled vocabularies

Columns: `repo_full_name, group, tool, source, evidence, count, first_seen`

- **`group`** (2 values): `dev` (AI-assisted development), `product` (LLM shipped as a feature)
- **`source`** (7 observed): `file`, `commit_trailer`, `commit_author`, `pr_author`,
  `pr_body`, `workflow`, `dependency`
  *(schema also supports `topic`, `bot_comment`; neither fired in this corpus)*
- **`tool`** (15 observed):
  - dev tools: `claude_code`, `github_copilot`, `agents_md`, `cursor`, `devin`,
    `jules`, `roo`, `openai_codex`, `gemini_cli`, `mcp`
  - product providers: `openai`, `anthropic`, `cohere`, `deepseek`, `groq`
- **`evidence`** — human-readable token (e.g. `file:CLAUDE.md`, `commit_trailer:claude_code`,
  `pr_author:devin-ai-integration[bot]`, `dependency:anthropic`)
- **`count`** — occurrences (e.g. number of AI-coauthored commits for that tool)
- **`first_seen`** — date the signal is datable to (empty if undatable)

**Evidence-strength tiers** (for confidence weighting): `file`, `commit_trailer`,
`commit_author`, `pr_author` = **strong**; `workflow`, `pr_body`, `dependency` =
**medium**; `topic` = **weak**.

---

## 4. New fields inside `full_results.json` / `<repo>/data.json`

- New object **`ai_usage_metrics`** — all 15 `ai_usage.csv` fields **plus** `signals`
  (the full structured evidence list: each `{group, tool, source, evidence, count, first_seen}`).
- **`commit_history`** gained 6 keys:
  `total_commits_scanned`, `ai_coauthored_commit_count`, `ai_authored_commit_count`,
  `ai_coauthor_tool_counts` (dict), `ai_author_tool_counts` (dict),
  `ai_commit_tool_first_dates` (dict tool→ISO date).

---

## 5. Changed meaning of an existing field (5 → 6 migration)

`repo_metrics.ai_ml_detected` / `ai_ml_signals` now denote **classical ML only**
(TensorFlow, PyTorch, scikit-learn, Jupyter, …). LLM SDKs (`openai`, `langchain`)
moved to the product-LLM group, so the corpus count dropped **6 → 4**. The two
reclassified repos — `CivicTechWR/connectedkw`, `CodeForAfrica/PromiseTracker` —
had `dependency:openai`, now reported under `product_llm_*`.

---

## 6. Detected values (the corpus numbers)

**Adoption**

| Measure | Value |
|---|---|
| Repos with AI-assisted development | 24 / 56 (42.9%) |
| Repos shipping an LLM product feature | 2 / 56 (3.6%) |
| Repos with any AI signal | 25 / 56 (44.6%) |
| Adopters with active-use evidence (commits/PRs) | 21 |
| Adopters with agent-opened PRs | 9 |
| Adopters with bot-authored commits | 6 |
| Adopters with only declared intent (config files) | 3 |

**Tool frequency (repos):** claude_code 20 · github_copilot 12 · agents_md 6 ·
cursor 1 · devin 1 · jules 1 · roo 1 · openai_codex 1 · gemini_cli 1 · mcp 1.

**Product-LLM provider frequency (repos):** openai 2 · anthropic 1 · cohere 1 ·
deepseek 1 · groq 1.

**Evidence sources (repos detected via, with tier):**

| Source | Repos | Tier |
|---|---|---|
| commit_trailer | 20 | strong |
| file | 14 | strong |
| pr_author | 9 | strong |
| commit_author | 6 | strong |
| pr_body | 9 | medium |
| workflow | 3 | medium |
| dependency | 2 | medium |

**Adoption timeline (first dev-AI signal per repo):**

| Quarter | New | Cumulative |
|---|--:|--:|
| 2025-Q1 | 1 | 1 |
| 2025-Q2 | 6 | 7 |
| 2025-Q3 | 2 | 9 |
| 2025-Q4 | 3 | 12 |
| 2026-Q1 | 7 | 19 |
| 2026-Q2 | 4 | 23 |

(23 of 24 adopters datable; 1 is config-file-only. Earliest signal corpus-wide:
`civiform/civiform`, 2025-03-07.)

**Adopters vs non-adopters (median; Mann-Whitney U):**

| Metric | Adopter | Non-adopter | p |
|---|--:|--:|--:|
| Total commits | 575 | 268 | 0.008 |
| Developers | 11 | 5 | 0.001 |
| Stars | 7 | 3 | 0.058 |
| Health % | 50 | 50 | 0.25 |
| Project age (yr) | 3.8 | 3.3 | 0.97 |
| Bus factor (no bots) | 1 | 1 | 0.088 |

(adopters n = 24, non-adopters n = 32)

**Adoption by civic-tech community:** Meshtastic 3/3 (100%) · Code for Japan 2/2
(100%) · CivicTechWR/Canada 6/8 (75%) · CfA/CiviForm 5/9 (56%) · Code for Africa
3/9 (33%) · German OK-Lab 3/18 (17%) · Other 2/7 (29%).

---

*Reproduce: `uv run python scripts/ai_usage_analysis.py datasets/2026_06/`.
Narrative writeups: `ai_usage_findings.md` (findings & discussion),
`analysis_n56.md` (full analysis), `README.md` (dataset overview).*
