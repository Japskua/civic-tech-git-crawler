"""AI-usage detection collector.

Detects two independent phenomena and reports them as separate signal groups
(see utils/ai_detection.py for the rationale and vocabulary):

* **dev**     — an LLM coding tool helped build the code (agent config files,
  commit co-author trailers, agent-bot commits/PRs, CI agents, review bots).
* **product** — the project ships LLM/GenAI functionality (LLM SDK
  dependencies, GenAI topics).

This is kept distinct from the traditional ML detection on RepoMetrics
(``ai_ml_detected``), which now covers classical ML only.
"""

from __future__ import annotations

import logging
from datetime import datetime

from github import Repository

from civic_tech_crawler.client import GitHubClient
from civic_tech_crawler.models import (
    AISignal,
    AIUsageMetrics,
    CommitHistoryMetrics,
    RepoMetrics,
    TemporalMetrics,
)
from civic_tech_crawler.utils.ai_detection import (
    DEFAULT_AI_DEV_KEYWORDS,
    DEFAULT_PRODUCT_LLM_KEYWORDS,
    match_agent_bot,
)
from civic_tech_crawler.utils.deps import extract_dependencies

logger = logging.getLogger(__name__)

# Cap on how many recent PRs to deep-scan for body markers / review bots.
_PR_META_LIMIT = 200


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        return None


def collect_ai_usage(
    client: GitHubClient,
    repo: Repository.Repository,
    repo_metrics: RepoMetrics,
    temporal_metrics: TemporalMetrics | None,
    commit_history: CommitHistoryMetrics | None,
    ai_dev_keywords: dict | None = None,
    product_llm_keywords: dict | None = None,
) -> AIUsageMetrics:
    """Detect AI usage signals for a repository."""
    slug = repo.full_name
    logger.info("Detecting AI usage for %s", slug)

    dev_kw = ai_dev_keywords or DEFAULT_AI_DEV_KEYWORDS
    prod_kw = product_llm_keywords or DEFAULT_PRODUCT_LLM_KEYWORDS

    signals: list[AISignal] = []
    agent_config_files: list[str] = []
    ci_ai_workflows: list[str] = []
    review_bot_tools: set[str] = set()

    deps = extract_dependencies(client, slug)

    _detect_dependencies(signals, deps, dev_kw, prod_kw)
    _detect_config_files(client, slug, signals, agent_config_files, dev_kw)
    _detect_commits(commit_history, signals)
    ai_agent_pr_count = _detect_prs(
        client, slug, temporal_metrics, signals, review_bot_tools, dev_kw
    )
    _detect_ci_workflows(client, slug, signals, ci_ai_workflows, dev_kw)
    _detect_topics(repo_metrics, signals, prod_kw)

    # -- Aggregate -----------------------------------------------------------
    dev_signals = [s for s in signals if s.group == "dev"]
    product_signals = [s for s in signals if s.group == "product"]

    dev_tools = sorted({s.tool for s in dev_signals})
    # Providers come from dependency evidence only; topic signals are not providers.
    product_providers = sorted(
        {s.tool for s in product_signals if s.source == "dependency"}
    )
    product_llm_signals = sorted({s.evidence for s in product_signals})

    dev_dates = [s.first_seen for s in dev_signals if s.first_seen is not None]
    first_dev_ai_date = min(dev_dates) if dev_dates else None

    commits_scanned = commit_history.total_commits_scanned if commit_history else 0
    ai_coauthored = commit_history.ai_coauthored_commit_count if commit_history else 0
    ai_authored = commit_history.ai_authored_commit_count if commit_history else 0
    ai_commit_ratio = (
        round((ai_coauthored + ai_authored) / commits_scanned, 4)
        if commits_scanned > 0
        else 0.0
    )

    metrics = AIUsageMetrics(
        repo_full_name=slug,
        dev_ai_detected=len(dev_signals) > 0,
        dev_ai_tools=dev_tools,
        agent_config_files=sorted(set(agent_config_files)),
        ai_coauthored_commit_count=ai_coauthored,
        ai_authored_commit_count=ai_authored,
        commits_scanned=commits_scanned,
        ai_commit_ratio=ai_commit_ratio,
        ai_agent_pr_count=ai_agent_pr_count,
        ci_ai_workflows=sorted(set(ci_ai_workflows)),
        review_bot_tools=sorted(review_bot_tools),
        first_dev_ai_date=first_dev_ai_date,
        product_llm_detected=len(product_signals) > 0,
        product_llm_signals=product_llm_signals,
        product_llm_providers=product_providers,
        signals=signals,
    )

    logger.info(
        "%s: dev_ai=%s (%s), product_llm=%s (%s)",
        slug,
        metrics.dev_ai_detected,
        ",".join(dev_tools) or "-",
        metrics.product_llm_detected,
        ",".join(product_providers) or "-",
    )
    return metrics


def _detect_dependencies(
    signals: list[AISignal], deps: list[str], dev_kw: dict, prod_kw: dict
) -> None:
    """Match declared dependencies against product-LLM and dev-tool vocab."""
    for key, provider in prod_kw.get("dependencies", {}).items():
        if any(key.lower() in dep for dep in deps):
            signals.append(
                AISignal(
                    group="product",
                    tool=provider,
                    source="dependency",
                    evidence=f"dependency:{key}",
                )
            )
    for key, tool in dev_kw.get("dependencies", {}).items():
        if any(key.lower() in dep for dep in deps):
            signals.append(
                AISignal(
                    group="dev",
                    tool=tool,
                    source="dependency",
                    evidence=f"dependency:{key}",
                )
            )


def _detect_config_files(
    client: GitHubClient,
    slug: str,
    signals: list[AISignal],
    agent_config_files: list[str],
    dev_kw: dict,
) -> None:
    """Detect agent config files/dirs and date their first appearance."""
    root_files = set(client.get_repo_contents_names(slug))

    # Exact root files (cheap: one listing already fetched).
    for fname, tool in dev_kw.get("config_files", {}).items():
        if fname in root_files:
            first_seen = _parse_iso(
                client.get_first_commit_date_for_path(slug, fname)
            )
            agent_config_files.append(fname)
            signals.append(
                AISignal(
                    group="dev", tool=tool, source="file",
                    evidence=f"file:{fname}", first_seen=first_seen,
                )
            )

    # Exact nested paths (HEAD check each).
    for path, tool in dev_kw.get("config_paths", {}).items():
        if client.file_exists(slug, path):
            first_seen = _parse_iso(
                client.get_first_commit_date_for_path(slug, path)
            )
            agent_config_files.append(path)
            signals.append(
                AISignal(
                    group="dev", tool=tool, source="file",
                    evidence=f"file:{path}", first_seen=first_seen,
                )
            )

    # Directories (non-empty listing => exists).
    for dirpath, tool in dev_kw.get("config_dirs", {}).items():
        # Skip a dir whose parent we already know is absent at root.
        top = dirpath.split("/", 1)[0]
        if "/" not in dirpath and top not in root_files:
            continue
        if client.get_repo_contents_names(slug, dirpath):
            agent_config_files.append(f"{dirpath}/")
            signals.append(
                AISignal(
                    group="dev", tool=tool, source="file",
                    evidence=f"dir:{dirpath}",
                )
            )


def _detect_commits(
    commit_history: CommitHistoryMetrics | None, signals: list[AISignal]
) -> None:
    """Lift the AI-commit tallies computed during the commit-history walk."""
    if commit_history is None:
        return
    first_dates = commit_history.ai_commit_tool_first_dates or {}
    for tool, count in (commit_history.ai_coauthor_tool_counts or {}).items():
        signals.append(
            AISignal(
                group="dev", tool=tool, source="commit_trailer",
                evidence=f"commit_trailer:{tool}", count=count,
                first_seen=_parse_iso(first_dates.get(tool)),
            )
        )
    for tool, count in (commit_history.ai_author_tool_counts or {}).items():
        signals.append(
            AISignal(
                group="dev", tool=tool, source="commit_author",
                evidence=f"commit_author:{tool}", count=count,
                first_seen=_parse_iso(first_dates.get(tool)),
            )
        )


def _detect_prs(
    client: GitHubClient,
    slug: str,
    temporal_metrics: TemporalMetrics | None,
    signals: list[AISignal],
    review_bot_tools: set[str],
    dev_kw: dict,
) -> int:
    """Detect agent-authored PRs (all PRs), and AI body markers + review bots
    (recent PRs only). Returns the agent-authored PR count."""
    # Agent-authored PRs across all temporal PRs (free — already fetched).
    login_tool: dict[str, str] = {}  # login -> tool
    login_counts: dict[str, int] = {}  # login -> PR count
    if temporal_metrics:
        for pr in temporal_metrics.prs:
            tool = match_agent_bot(pr.author_login, None, dev_kw)
            if tool:
                login = pr.author_login or ""
                login_tool[login] = tool
                login_counts[login] = login_counts.get(login, 0) + 1
    ai_agent_pr_count = sum(login_counts.values())
    for login, count in login_counts.items():
        signals.append(
            AISignal(
                group="dev", tool=login_tool[login], source="pr_author",
                evidence=f"pr_author:{login}", count=count,
            )
        )

    # Recent-PR deep scan: body markers + review/comment bots.
    review_logins = {
        k.lower(): v for k, v in dev_kw.get("review_bot_logins", {}).items()
    }
    trailer_tools = dev_kw.get("trailer_tools", {})
    body_marker_tools: dict[str, datetime | None] = {}
    review_first_seen: dict[str, datetime | None] = {}
    try:
        recent = client.iter_recent_prs_with_meta(slug, limit=_PR_META_LIMIT)
    except Exception as exc:  # noqa: BLE001 — best-effort enrichment
        logger.warning("PR meta scan failed for %s: %s", slug, exc)
        recent = []

    for pr in recent:
        created = _parse_iso(pr.get("created_at"))
        body = (pr.get("body") or "").lower()
        for needle, tool in trailer_tools.items():
            if needle in body and ("generated with" in body or "co-authored-by" in body):
                prev = body_marker_tools.get(tool, "missing")
                if prev == "missing" or (created and (prev is None or created < prev)):
                    body_marker_tools[tool] = created
        for login in pr.get("participant_logins", []):
            lo = (login or "").lower()
            tool = review_logins.get(lo)
            if tool is None:
                tool = next(
                    (v for k, v in review_logins.items() if k in lo), None
                )
            if tool:
                review_bot_tools.add(tool)
                prev = review_first_seen.get(tool, "missing")
                if prev == "missing" or (created and (prev is None or created < prev)):
                    review_first_seen[tool] = created

    for tool, first_seen in body_marker_tools.items():
        signals.append(
            AISignal(
                group="dev", tool=tool, source="pr_body",
                evidence=f"pr_body:{tool}", first_seen=first_seen,
            )
        )
    for tool, first_seen in review_first_seen.items():
        signals.append(
            AISignal(
                group="dev", tool=tool, source="bot_comment",
                evidence=f"bot_comment:{tool}", first_seen=first_seen,
            )
        )

    return ai_agent_pr_count


def _detect_ci_workflows(
    client: GitHubClient,
    slug: str,
    signals: list[AISignal],
    ci_ai_workflows: list[str],
    dev_kw: dict,
) -> None:
    """Scan .github/workflows/* file contents for AI action references."""
    workflow_files = client.get_repo_contents_names(slug, ".github/workflows")
    refs = dev_kw.get("workflow_refs", {})
    for fname in workflow_files:
        if not (fname.endswith(".yml") or fname.endswith(".yaml")):
            continue
        content = client.get_file_content(slug, f".github/workflows/{fname}")
        if not content:
            continue
        lowered = content.lower()
        matched_tools = {
            tool for needle, tool in refs.items() if needle.lower() in lowered
        }
        if matched_tools:
            ci_ai_workflows.append(fname)
        for tool in sorted(matched_tools):
            signals.append(
                AISignal(
                    group="dev", tool=tool, source="workflow",
                    evidence=f"workflow:{fname}:{tool}",
                )
            )


def _detect_topics(
    repo_metrics: RepoMetrics, signals: list[AISignal], prod_kw: dict
) -> None:
    """Detect product-LLM topics (reusing topics already on repo_metrics)."""
    topics = {t.lower() for t in (repo_metrics.topics or [])}
    for kw in prod_kw.get("topics", []):
        if kw.lower() in topics:
            signals.append(
                AISignal(
                    group="product", tool=kw.lower(), source="topic",
                    evidence=f"topic:{kw}",
                )
            )
