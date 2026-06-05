# AI Usage in Open-Source Civic Technology: Findings & Discussion

*Companion findings document for the research paper, generated against the
**2026-06** civic-tech corpus (n = 55). Underlying tables: `ai_usage.csv`,
`ai_signals.csv`, and `ai_usage_analysis/`. All AI-usage measures are a **lower
bound** (see §5).*

---

## 1. Research questions

- **RQ1 — Prevalence.** How widespread is AI involvement in open-source
  civic-technology projects, and in what form (used to *build* the code vs.
  *shipped* as an LLM product feature)?
- **RQ2 — Tooling.** Which AI tools and conventions do civic-tech projects adopt,
  and how deep is the evidence (declared intent vs. active use)?
- **RQ3 — Timing.** When did AI adoption occur?
- **RQ4 — Correlates.** How does AI adoption relate to project structure — scale,
  activity, community, and single-maintainer risk?

We answer these with a multi-signal detector that separates **AI-assisted
development** (`dev_*` — agent config files, commit co-author trailers, AI
agent-bot commits/PRs, CI agents, review bots) from **product LLM** (`product_*` —
shipped LLM/GenAI dependencies and topics), with each signal carrying an evidence
source and a first-appearance date.

---

## 2. Findings

### F1 — AI-assisted development is already mainstream; shipped-AI is rare

**24 of 55 projects (44%)** carry at least one AI-assisted-development signal,
while only **2 of 55 (4%)** ship an LLM product feature. Civic technology, in this
corpus, **uses AI to build software far more than it ships AI to users.** The two
product-LLM cases are `CodeForAfrica/PromiseTracker` (OpenAI, Anthropic, Cohere,
DeepSeek, Groq SDKs) and an inherited signal in the `CivicTechWR/connectedkw`
fork.

### F2 — Tooling is concentrated in two assistants

Among the 24 adopters, the toolchain is dominated by **Claude Code (20 repos)** and
**GitHub Copilot (12 repos)**; the cross-tool **`AGENTS.md`** convention appears in
6. Cursor, Devin, Google Jules, OpenAI Codex, Gemini CLI, Roo, and MCP configs
each appear once. The market visible in public artifacts is effectively a duopoly
of Claude Code and Copilot, with a long tail of agentic tools.

### F3 — Most adoption is *active use*, not just *declared intent*

Distinguishing evidence depth matters. Of the 24 adopters:

- **21** show **active use** — actual AI-attributed commits and/or agent-opened
  pull requests;
- **3** show only **declared intent** — an agent config file (e.g. `CLAUDE.md`,
  `AGENTS.md`) with no AI-attributed commits or PRs (`bikespace/bikespace`,
  `CivicTechWR/accessible-housing-portal`, `CivicTechWR/project-pech`).

Within active use, **9 projects have AI agent-opened PRs** and **6 have
bot-authored commits** — i.e. autonomous agents (Copilot SWE agent, Devin, Jules)
contributing code directly, not merely assisting a human. The evidence base skews
**strong**: the most common sources are commit co-author trailers (20 repos) and
agent config files (14), rather than weak signals like topics.

### F4 — Adoption is a 2025–2026 phenomenon

Dating each project's first AI-development signal shows adoption is almost
entirely recent. Cumulative adopters by quarter:

| Quarter | New | Cumulative |
|---|--:|--:|
| 2025-Q1 | 1 | 1 |
| 2025-Q2 | 6 | 7 |
| 2025-Q3 | 2 | 9 |
| 2025-Q4 | 3 | 12 |
| 2026-Q1 | 7 | 19 |
| 2026-Q2 | 4 | 23 |

(23 of 24 adopters have a datable first signal; one is config-file-only.) AI
adoption in civic-tech tracks the broader 2025 surge in agentic developer tooling
— there is essentially no pre-2025 history.

### F5 — Adoption varies enormously across civic-tech communities

Adoption is highly uneven by organisational community:

| Community | Adopters / repos | Rate |
|---|---|--:|
| Meshtastic | 3 / 3 | 100% |
| Code for Japan | 2 / 2 | 100% |
| Canada — CivicTechWR / Toronto | 6 / 8 | 75% |
| USA — Code for America / CiviForm | 5 / 9 | 56% |
| Code for Africa | 3 / 9 | 33% |
| Other (mySociety, g0v, VoteIT, ...) | 2 / 6 | 33% |
| Germany — Code for / OK Lab | 3 / 18 | **17%** |

North American communities and certain orgs (Meshtastic, Code for Japan) have
embraced AI tooling, while the large **German OK-Lab cluster sits at 17%** — a
4–6× gap. This is consistent with **organisational/cultural diffusion** rather
than a uniform technological wave.

### F6 — Adopters are larger and busier, but not better-bussed

Comparing adopters (n = 24) to non-adopters (n = 31), Mann-Whitney U:

| Metric | Adopter median | Non-adopter median | p |
|---|--:|--:|--:|
| Total commits | 575 | 272 | **0.011** |
| Developers | 11 | 5 | **0.002** |
| Stars | 7 | 3 | 0.078 |
| Health % | 50 | 50 | 0.326 |
| Project age (yr) | 3.79 | 3.47 | 0.932 |
| Bus factor (no bots) | 1 | 1 | 0.104 |

AI adopters are significantly larger and more active, but show **no** difference in
single-maintainer risk (bus factor) or project age. The most AI-active projects —
`meshtastic/Meshtastic-Android` (199 AI-coauthored commits), `meshtastic/firmware`
(173), `codeforjapan/BirdXplorer` (52 coauthored + 15 bot-authored + 7 Devin PRs),
`openlegaldata/oldp` (62), `CivicTechWR/go-train-group-pass` (11 agent PRs) — are
among the corpus's more active repositories generally.

---

## 3. Discussion

**Civic-tech is an AI *consumer*, not an AI *vendor* (F1).** The 43%/4% split says
the sector's AI story is overwhelmingly about developer productivity, not
AI-powered civic services. For a sector chronically short on contributor capacity,
this is a rational allocation: AI is being pointed at the bottleneck (building and
maintaining software) rather than at new product surfaces that would expand scope.

**A duopoly with a thin moat (F2).** Claude Code and Copilot dominate, but the
presence of `AGENTS.md` in a quarter of adopters — a tool-agnostic convention —
signals that teams are hedging against lock-in. The visible toolchain is young and
likely volatile.

**Declared intent is a leading indicator (F3).** The 3 config-file-only projects
are plausibly *early* in adoption — the config landed, sustained AI-attributed
contribution has not yet followed. Separating intent from active use is important
methodologically: counting config files alone would overstate *practiced* AI
development. That 9 projects already accept **agent-authored pull requests** is the
more striking result — autonomous contribution, not just autocomplete, is present
in civic-tech today.

**Diffusion is organisational, not technological (F5).** The 100%-vs-17% spread
across communities is too large to be explained by project characteristics alone;
it points to community norms, leadership, and knowledge-sharing as the drivers. The
German OK-Lab cluster's low rate, despite being the largest community in the
corpus, suggests adoption is gated by local culture and possibly data-protection
caution rather than by project need. This is the most actionable finding for
civic-tech organisers: **AI adoption appears to spread through communities, not
through individual projects.**

**Selection, most likely — not effect (F6).** Adopters being larger and busier,
but no less fragile (bus factor unchanged), is best read as **selection**: active,
multi-contributor projects are the ones that take up AI tooling. We cannot, from a
cross-sectional snapshot, claim that AI tooling *causes* higher activity; reverse
causation is at least as plausible. Critically, AI adoption shows **no association
with the sector's defining structural weakness** — the median project, AI-assisted
or not, still has a bus factor of 1. AI is changing how civic-tech code gets
written; there is no evidence here that it changes who is left maintaining it.

---

## 4. Implications

- **For civic-tech organisations.** Adoption spreads by community (F5). Orgs
  seeking to benefit from AI tooling should treat it as a *community capability*
  to be shared (templates, `AGENTS.md`/`CLAUDE.md` starters, agent-PR review
  norms), not as a per-project choice. The 17% communities have the most headroom.
- **For sustainability research.** AI adoption does not (yet) move the bus factor
  (F6). If AI tooling is to improve civic-tech *sustainability* and not merely
  throughput, that benefit is not visible in 2026 structural metrics and should be
  a target of longitudinal study.
- **For measurement.** Distinguishing *shipped AI* from *AI-assisted development*,
  and *active use* from *declared intent*, materially changes the headline numbers.
  Studies that conflate these will mis-estimate both prevalence and practice.

---

## 5. Threats to validity & limitations

- **Lower bound.** Detection captures only **disclosed, configured, or automated**
  AI traces (config files, co-author trailers, agent bots, CI agents, LLM
  dependencies). Inline autocomplete and chat-paste workflows leave no artifact and
  are invisible. **True AI-assistance rates are necessarily higher than 44%.**
- **Correlational, cross-sectional.** §F6/§3 associations cannot establish
  causation or direction; a single snapshot cannot separate "AI raises activity"
  from "active teams adopt AI."
- **Small n; ecosystem bias.** n = 55 limits statistical power. Product-LLM
  detection reads only root-level Python/JS manifests, under-sampling shipped-AI in
  other language ecosystems (the 4% product figure is itself a floor).
- **Forks (3).** Inherited history can attribute a parent's AI signals to a fork
  (e.g. `connectedkw`'s product-LLM signal).
- **Recency of the phenomenon.** With adoption concentrated in 2025–2026 (F4),
  estimates are sensitive to crawl date; this snapshot is 2026-06.

---

## 6. What this enables (future work)

- **Longitudinal tracking.** The crawler is resumable and the corpus roster is
  stable across the 2026-05 → 2026-06 refreshes; repeating the crawl yields an
  adoption *trajectory* and a natural test of the selection-vs-effect question on
  the bus factor.
- **Community-level study.** The F5 variation invites qualitative follow-up with
  the high- and low-adoption communities (Meshtastic / Code for Japan vs. German
  OK-Lab).
- **Practice depth.** Linking agent-PR/commit volume to review outcomes and defect
  metrics would test whether agent-authored contribution helps or burdens
  maintainers.

---

*Reproduce: `uv run python scripts/ai_usage_analysis.py datasets/2026_06/`.
See `ai_usage_analysis/summary.md` for the generated tables and
`analysis_n56.md` for the structural (non-AI) analysis.*
