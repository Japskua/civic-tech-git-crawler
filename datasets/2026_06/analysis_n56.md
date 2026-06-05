# AI Adoption and Contributor Dynamics in Open-Source Civic Technology: A 56-Project Snapshot (2026-06)

This writeup accompanies the **2026-06 refresh** of the civic-tech corpus (n = 56).
It re-crawls the same roster as [2026-05](../2026_05/analysis_n57.md) and adds a
new measurement layer — **AI-usage detection** — making AI adoption in civic-tech
the headline subject of this snapshot. All figures are generated against this
folder; see `statistical_analysis/`, `weekly_activity_analysis/`, and
`ai_usage_analysis/` for the underlying tables.

## 1. Dataset

56 open-source civic-technology projects across 24 organisations and seven
regions (US, Canada, Africa, Japan, Taiwan, Germany, UK/Sweden). Projects are
selected on *design intent* — civic engagement, government services,
participation, transparency, open data, or democratic process — not on whether
their only use is civic. The roster is identical to 2026-05, enabling
month-over-month comparison. Aggregate: 90,669 commits, 661 contributors (607
human, 54 bot), median project age 3.5 years, 17 primary languages.

### 1.1 Methodology

Metrics are collected by `civic-tech-crawler` (CHAOSS-aligned community-health
metrics, full commit history via GraphQL, issue/PR analytics). New in this
refresh, **AI-usage detection** separates two phenomena:

- **AI-assisted development** (`dev_*`): AI coding tools helped *build* the code.
  Evidence sources, in descending strength: agent config files (`CLAUDE.md`,
  `AGENTS.md`, `.cursorrules`, …), commit co-author trailers
  (`Co-authored-by: Claude`), AI agent-bot commits/PRs (`copilot-swe-agent[bot]`,
  `devin-ai-integration[bot]`, …), CI agents, and review bots.
- **Product LLM** (`product_*`): the project *ships* LLM/GenAI functionality
  (LLM SDK dependencies, GenAI topics).

Statistical tests are non-parametric (Spearman ρ with Benjamini-Hochberg FDR
control; Mann-Whitney U for group comparisons; Cliff's δ for effect size). With
n = 56 these are **exploratory**; AI-usage comparisons in particular are
**correlational, not causal**.

## 2. Results

### 2.1 Effort is highly concentrated, and concentration falls with team size

Across the corpus, contributor effort is dominated by a small number of people.
Team size correlates strongly and negatively with organisational concentration
(`num_developers` vs `hhi_no_bots`, ρ = −0.76, FDR-significant), and the busiest
contributor dominates most *weeks*: many repositories are 100% solo across their
entire active history (e.g. `ton-An/station_reach`,
`oklabflensburg/open-school-map`, several Code-for-America services).

### 2.2 Scale grows with age; single-maintainer risk barely moves

Mature projects (≥ 3.5 yr) have far more developers (median 15.5 vs 4, p < 0.001,
large effect) and commits (1,358 vs 186, p < 0.001), and are meaningfully less
concentrated (HHI 4,568 vs 8,618, p = 0.007). Yet the **bus factor improves only
marginally** with maturity (median 1.5 vs 1.0, p = 0.026, small effect): scale and
deconcentration grow with age, but the risk of a single departure halting a
project does not meaningfully recede.

### 2.3 AI-assisted development is already mainstream — and recent

**24 of 56 projects (43%)** show at least one AI-assisted-development signal. The
tooling is concentrated: **Claude Code leads (20 repos)**, followed by **GitHub
Copilot (12)**; the cross-tool `AGENTS.md` convention appears in 6, and Cursor,
Devin, Jules, OpenAI Codex, Gemini CLI, Roo, and MCP configs appear once each.
Evidence is dominated by strong sources — commit co-author trailers (20 repos) and
agent config files (14) — rather than weak ones, lending confidence to the
detection.

### 2.4 Adoption is a 2025–2026 phenomenon

Dating the first AI-dev signal per repository shows adoption is almost entirely
recent: the earliest datable signal falls in 2025-Q1, and the cumulative adopter
count climbs 1 → 7 → 9 → 12 → 19 → 23 across 2025-Q1 through 2026-Q2. Civic-tech's
embrace of AI coding tools tracks the broader 2025 surge in agentic developer
tooling.

### 2.5 AI-adopters are larger and busier — but not better-bussed

Comparing adopters (n = 24) against non-adopters (n = 32):

| Metric | Adopter median | Non-adopter median | Mann-Whitney p |
|---|---|---|---|
| Total commits | 575 | 268 | **0.008** |
| Developers | 11 | 5 | **0.001** |
| Stars | 7 | 3 | 0.058 |
| Health % | 50 | 50 | 0.25 |
| Project age (yr) | 3.8 | 3.3 | 0.97 |
| Bus factor (no bots) | 1 | 1 | 0.09 |

Adopters are significantly larger and more active, but show **no** difference in
single-maintainer risk (bus factor) or project age. The most plausible reading is
**selection, not effect**: AI coding tools are taken up by already-active,
multi-contributor projects. This snapshot cannot distinguish whether AI tooling
raises activity or whether active teams are simply more likely to adopt it.

### 2.6 Civic-tech *uses* AI more than it *ships* AI

Only **2 of 56 projects ship an LLM product feature** (`CodeForAfrica/PromiseTracker`,
with OpenAI/Anthropic/Cohere/DeepSeek/Groq SDKs, and the inherited signal in the
`CivicTechWR/connectedkw` fork). The civic-tech AI story in this corpus is
overwhelmingly about **development tooling**, not LLM-powered product surfaces.

## 3. Threats to validity

- **AI-usage detection is a lower bound.** Only disclosed/configured/automated
  traces are visible; inline autocomplete and chat-paste usage are invisible.
  True AI-assistance rates are necessarily *higher* than the 43% reported.
- **Correlational, not causal.** §2.5 comparisons cannot establish direction;
  reverse causation (active projects adopt AI) is at least as plausible as the
  forward effect.
- **Small n and dependency-ecosystem bias.** n = 56 limits power; product-LLM
  detection reads only root-level Python/JS manifests, so non-Python/JS projects
  are under-sampled for the `product_*` group.
- **Forks (3)** inherit upstream history; their AI and concentration signals may
  belong to the parent.
- **Scale outliers** (meshtastic ×3, iiab) dominate scale-sensitive aggregates;
  medians are reported throughout.

## 4. Conclusion

By mid-2026, AI-assisted development has become mainstream in open-source civic
technology — **43% of this corpus** carries a durable trace of it, almost entirely
acquired during 2025–2026, and concentrated in Claude Code and GitHub Copilot. AI
adoption co-varies with project scale and activity but not with the structural
fragility that defines the sector: the median civic-tech project, AI-assisted or
not, still has a **bus factor of 1**. AI tooling is changing how civic-tech code
gets written; it has not yet changed who is left holding it.
