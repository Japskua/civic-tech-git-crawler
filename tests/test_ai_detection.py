from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from civic_tech_crawler.cache import _dict_to_commit_history_metrics
from civic_tech_crawler.client import CommitRecord
from civic_tech_crawler.collectors.ai_usage import _detect_commits, _detect_prs
from civic_tech_crawler.collectors.commit_history import collect_commit_history
from civic_tech_crawler.models import AISignal, CommitHistoryMetrics
from civic_tech_crawler.utils.ai_detection import (
    DEFAULT_AI_DEV_KEYWORDS,
    detect_ai_in_commit,
    match_trailer_tools,
)


def _utc(*args) -> datetime:
    return datetime(*args, tzinfo=timezone.utc)


# ----- match_trailer_tools (shared line-level rule) -----


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>", {"claude_code"}),
        ("🤖 Generated with Claude Code", {"claude_code"}),
        ("Generated with Cursor", {"cursor"}),
        ("Co-authored-by: Copilot <copilot@github.com>", {"github_copilot"}),
        ("  co-authored-by: devin-ai-integration[bot]  ", {"devin"}),
        # Several trailers in one message credit each tool once.
        (
            "Fix bug\n\nCo-authored-by: Claude <noreply@anthropic.com>\n"
            "Co-authored-by: aider (gpt-4o) <noreply@aider.chat>",
            {"claude_code", "aider"},
        ),
    ],
)
def test_marker_line_naming_a_tool_credits_it(text, expected):
    assert match_trailer_tools(text, DEFAULT_AI_DEV_KEYWORDS) == expected


@pytest.mark.parametrize(
    "text",
    [
        # Prose mention with no marker line at all.
        "Switch to a server-side cursor for the export",
        "Asked Claude about this approach",
        # A marker line that names no known tool.
        "Generated with a custom script",
        # "co-authored-by" in prose is not a trailer (must start the line).
        "Remember to add co-authored-by: claude when pairing",
    ],
)
def test_text_without_tool_on_marker_line_credits_nothing(text):
    assert match_trailer_tools(text, DEFAULT_AI_DEV_KEYWORDS) == set()


def test_tool_named_off_the_marker_line_is_not_credited():
    # Shape of openlegaldata/oldp PR #213: a Claude Code PR body that also
    # mentions a database "server-side cursor" in its summary.
    body = (
        "Summary\n"
        "Replaces the Paginator loop in handle_items with "
        "items.iterator(chunk_size=...). Server-side cursor, streams rows.\n"
        "Test plan\n"
        "Ran the export command locally\n"
        "🤖 Generated with Claude Code"
    )
    assert match_trailer_tools(body, DEFAULT_AI_DEV_KEYWORDS) == {"claude_code"}


def test_empty_or_missing_text_credits_nothing():
    assert match_trailer_tools(None, DEFAULT_AI_DEV_KEYWORDS) == set()
    assert match_trailer_tools("", DEFAULT_AI_DEV_KEYWORDS) == set()


def test_mixed_case_needles_from_config_still_match():
    dev_kw = {"trailer_tools": {"Claude": "claude_code"}}
    assert match_trailer_tools("Co-Authored-By: Claude", dev_kw) == {"claude_code"}


def test_detect_ai_in_commit_splits_trailer_and_author_tools():
    co_tools, auth_tools = detect_ai_in_commit(
        "Add feature\n\nCo-Authored-By: Claude <noreply@anthropic.com>",
        "devin-ai-integration[bot]",
        "158243242+devin-ai-integration[bot]@users.noreply.github.com",
        DEFAULT_AI_DEV_KEYWORDS,
    )
    assert co_tools == {"claude_code"}
    assert auth_tools == {"devin"}


def test_detect_ai_in_commit_ignores_prose_mentions():
    co_tools, auth_tools = detect_ai_in_commit(
        "Use a cursor for pagination\n\nAlso tried copilot suggestions",
        "alice",
        "alice@example.org",
        DEFAULT_AI_DEV_KEYWORDS,
    )
    assert co_tools == set()
    assert auth_tools == set()


# ----- _detect_prs: PR body markers -----


class _FakePRClient:
    def __init__(self, prs):
        self._prs = prs

    def iter_recent_prs_with_meta(self, slug, limit=200):
        return self._prs


def _pr(number, created_at, body, participants=()):
    return {
        "number": number,
        "created_at": created_at,
        "author": "alice",
        "body": body,
        "participant_logins": list(participants),
    }


def test_pr_body_cursor_mention_is_not_credited_to_cursor_editor():
    prs = [
        _pr(
            215,
            "2026-05-22T09:00:00Z",
            "Replaced with qs.iterator(chunk_size=...). With .order_by(\"pk\") "
            "over a single table the server-side cursor is used.\n"
            "🤖 Generated with Claude Code",
        ),
        _pr(
            213,
            "2026-05-20T13:07:16Z",
            "Server-side cursor, streams rows.\n🤖 Generated with Claude Code",
        ),
        _pr(145, "2026-02-13T11:36:29Z", "Fix typo\n🤖 Generated with Claude Code"),
    ]
    signals: list[AISignal] = []
    _detect_prs(_FakePRClient(prs), "o/r", None, signals, set(), DEFAULT_AI_DEV_KEYWORDS)

    pr_body = [s for s in signals if s.source == "pr_body"]
    assert [s.evidence for s in pr_body] == ["pr_body:claude_code"]
    assert pr_body[0].first_seen == _utc(2026, 2, 13, 11, 36, 29)


def test_pr_body_credits_tool_named_on_marker_line():
    prs = [_pr(7, "2026-03-01T00:00:00Z", "Refactor\n\nGenerated with Cursor")]
    signals: list[AISignal] = []
    _detect_prs(_FakePRClient(prs), "o/r", None, signals, set(), DEFAULT_AI_DEV_KEYWORDS)

    assert [s.evidence for s in signals if s.source == "pr_body"] == ["pr_body:cursor"]


# ----- commit first dates: co-author trailer vs agent author -----


class _FakeCommitClient:
    def __init__(self, records):
        self._records = records

    def iter_commits_graphql(self, slug):
        yield from self._records


def _commit(sha, when, message="", login="alice", email="alice@example.org"):
    return CommitRecord(
        sha=sha,
        additions=1,
        deletions=0,
        committed_date=when,
        author_email=email,
        author_name=login,
        author_login=login,
        message=message,
    )


def _birdxplorer_like_history() -> CommitHistoryMetrics:
    # Shape of codeforjapan/BirdXplorer: Devin-authored commits from 2025-04,
    # Claude co-author trailers from 2026-01-13, and a single claude[bot]
    # commit on 2026-01-22.
    trailer = "Fix\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
    records = [
        _commit("a1", _utc(2025, 4, 28, 4, 0, 21), "Add X", login="devin-ai-integration[bot]",
                email="158243242+devin-ai-integration[bot]@users.noreply.github.com"),
        _commit("a2", _utc(2025, 5, 2), "Fix Y", login="devin-ai-integration[bot]",
                email="158243242+devin-ai-integration[bot]@users.noreply.github.com"),
        _commit("h1", _utc(2026, 1, 13, 8, 20, 35), trailer),
        _commit("h2", _utc(2026, 1, 20), trailer),
        _commit("b1", _utc(2026, 1, 22, 10, 0, 0), "Bot change", login="claude[bot]",
                email="claude[bot]@users.noreply.github.com"),
        _commit("h3", _utc(2026, 2, 1), "Plain human commit"),
    ]
    # iter_commits_graphql yields newest first.
    records.reverse()
    repo = SimpleNamespace(full_name="o/r")
    return collect_commit_history(_FakeCommitClient(records), repo)


def test_commit_history_tracks_first_dates_per_signal_kind():
    ch = _birdxplorer_like_history()

    assert ch.ai_coauthor_tool_counts == {"claude_code": 2}
    assert ch.ai_author_tool_counts == {"devin": 2, "claude_code": 1}
    assert ch.ai_coauthor_tool_first_dates == {
        "claude_code": _utc(2026, 1, 13, 8, 20, 35).isoformat(),
    }
    assert ch.ai_author_tool_first_dates == {
        "devin": _utc(2025, 4, 28, 4, 0, 21).isoformat(),
        "claude_code": _utc(2026, 1, 22, 10, 0, 0).isoformat(),
    }


def test_combined_first_dates_keep_earliest_of_either_kind():
    ch = _birdxplorer_like_history()

    assert ch.ai_commit_tool_first_dates == {
        "claude_code": _utc(2026, 1, 13, 8, 20, 35).isoformat(),
        "devin": _utc(2025, 4, 28, 4, 0, 21).isoformat(),
    }


def test_commit_author_signal_is_dated_by_first_agent_authored_commit():
    signals: list[AISignal] = []
    _detect_commits(_birdxplorer_like_history(), signals)

    by_evidence = {s.evidence: s for s in signals}
    assert by_evidence["commit_trailer:claude_code"].first_seen == _utc(2026, 1, 13, 8, 20, 35)
    assert by_evidence["commit_trailer:claude_code"].count == 2
    assert by_evidence["commit_author:claude_code"].first_seen == _utc(2026, 1, 22, 10, 0, 0)
    assert by_evidence["commit_author:claude_code"].count == 1
    assert by_evidence["commit_author:devin"].first_seen == _utc(2025, 4, 28, 4, 0, 21)


def test_trailer_signal_is_not_dated_by_earlier_agent_authored_commit():
    # The reverse case: the agent bot commits first, trailers come later.
    records = [
        _commit("h1", _utc(2026, 3, 1), "Fix\n\nCo-authored-by: Copilot <copilot@github.com>"),
        _commit("b1", _utc(2025, 11, 20), "Initial plan", login="copilot-swe-agent[bot]",
                email="198982749+Copilot@users.noreply.github.com"),
    ]
    ch = collect_commit_history(_FakeCommitClient(records), SimpleNamespace(full_name="o/r"))
    signals: list[AISignal] = []
    _detect_commits(ch, signals)

    by_evidence = {s.evidence: s for s in signals}
    assert by_evidence["commit_trailer:github_copilot"].first_seen == _utc(2026, 3, 1)
    assert by_evidence["commit_author:github_copilot"].first_seen == _utc(2025, 11, 20)


def test_cache_loads_per_kind_first_dates_and_defaults_for_old_entries():
    base = {
        "repo_full_name": "o/r",
        "weekly_snapshots": [],
        "contributor_lifecycles": [],
        "contributor_weeks": [],
        "total_weeks": 0,
        "total_unique_contributors": 0,
        "ai_commit_tool_first_dates": {"claude_code": "2026-01-13T08:20:35+00:00"},
    }
    old = _dict_to_commit_history_metrics(base)
    assert old.ai_coauthor_tool_first_dates == {}
    assert old.ai_author_tool_first_dates == {}

    new = _dict_to_commit_history_metrics(
        {
            **base,
            "ai_coauthor_tool_first_dates": {"claude_code": "2026-01-13T08:20:35+00:00"},
            "ai_author_tool_first_dates": {"claude_code": "2026-01-22T10:00:00+00:00"},
        }
    )
    assert new.ai_coauthor_tool_first_dates == {"claude_code": "2026-01-13T08:20:35+00:00"}
    assert new.ai_author_tool_first_dates == {"claude_code": "2026-01-22T10:00:00+00:00"}


# ----- anchored matching: false-positive shapes found in review -----


@pytest.mark.parametrize(
    "text",
    [
        # PR-template line listing tools: no tool directly follows the marker.
        "- [ ] Code generated with AI tools (Copilot, Cursor, Claude, Codex) is disclosed",
        # Human co-authors who share a tool's name have ordinary e-mails.
        "Co-authored-by: Devin Smith <devin@example.org>",
        "Co-authored-by: Claude Dupont <claude.dupont@example.fr>",
        "Co-authored-by: Jules Verne <12345+julesverne@users.noreply.github.com>",
        # "regenerated" is not the marker, and "precursor" is not Cursor.
        "Lockfile regenerated with npm; precursor to #12",
    ],
)
def test_lookalikes_credit_nothing(text):
    assert match_trailer_tools(text, DEFAULT_AI_DEV_KEYWORDS) == set()


def test_same_line_prose_does_not_credit_a_second_tool():
    line = "Uses a server-side cursor. Generated with [Claude Code](https://claude.ai/code)"
    assert match_trailer_tools(line, DEFAULT_AI_DEV_KEYWORDS) == {"claude_code"}


# Trailer and marker lines observed in the 2026-06 corpus audit.
@pytest.mark.parametrize(
    "text, expected",
    [
        ("Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>", "github_copilot"),
        ("Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>",
         "github_copilot"),
        ("Co-authored-by: Copilot Autofix powered by AI "
         "<62310815+github-advanced-security[bot]@users.noreply.github.com>", "github_copilot"),
        ("Co-authored-by: google-labs-jules[bot] "
         "<161369871+google-labs-jules[bot]@users.noreply.github.com>", "jules"),
        ("Co-authored-by: Codex", "openai_codex"),
        ("Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>", "claude_code"),
        ("🤖 Generated with [Claude Code](https://claude.com/claude-code)", "claude_code"),
        ("Generated by GitHub Copilot", "github_copilot"),
    ],
)
def test_audited_ai_markers_are_credited(text, expected):
    assert match_trailer_tools(text, DEFAULT_AI_DEV_KEYWORDS) == {expected}


@pytest.mark.parametrize(
    "text",
    [
        "Co-authored-by Claude <noreply@anthropic.com>",  # no colon
        "> Co-authored-by: Claude <noreply@anthropic.com>",  # quoted
        "- 🤖 Generated with Claude Code",  # bulleted
        "​Co-authored-by: Claude <noreply@anthropic.com>",  # zero-width prefix
        "Generated with:\nClaude Code",  # marker split across lines
    ],
)
def test_rendered_body_shapes_still_match(text):
    assert match_trailer_tools(text, DEFAULT_AI_DEV_KEYWORDS) == {"claude_code"}


def test_config_without_coauthor_emails_falls_back_to_defaults():
    # A user config that predates coauthor_emails: only the e-mail can credit
    # this line, because the address is not a [bot] address.
    dev_kw = {"trailer_tools": {"claude": "claude_code"}}
    line = "Co-authored-by: Claude Sonnet 4.6 <noreply@anthropic.com>"
    assert match_trailer_tools(line, dev_kw) == {"claude_code"}


def test_pr_body_signals_are_emitted_in_stable_order():
    body = (
        "Co-authored-by: Claude <noreply@anthropic.com>\n"
        "Co-authored-by: aider (gpt-4o) <noreply@aider.chat>"
    )
    signals: list[AISignal] = []
    _detect_prs(_FakePRClient([_pr(1, "2026-01-01T00:00:00Z", body)]), "o/r", None,
                signals, set(), DEFAULT_AI_DEV_KEYWORDS)
    assert [s.evidence for s in signals] == ["pr_body:aider", "pr_body:claude_code"]


# ----- dates: authored date and old cache entries -----


def test_ai_first_dates_use_authored_date_not_commit_date():
    # Authored on 2026-01-10, rebased and committed on 2026-01-22.
    from dataclasses import replace

    rec = replace(
        _commit("b1", _utc(2026, 1, 22), "Bot change", login="claude[bot]",
                email="claude[bot]@users.noreply.github.com"),
        authored_date=_utc(2026, 1, 10),
    )
    ch = collect_commit_history(_FakeCommitClient([rec]), SimpleNamespace(full_name="o/r"))

    assert ch.ai_author_tool_first_dates == {"claude_code": _utc(2026, 1, 10).isoformat()}
    assert ch.weekly_snapshots[0].week_start == "2026-01-19"


def test_old_cache_entry_falls_back_to_combined_first_dates():
    old = _dict_to_commit_history_metrics(
        {
            "repo_full_name": "o/r",
            "weekly_snapshots": [],
            "contributor_lifecycles": [],
            "contributor_weeks": [],
            "total_weeks": 0,
            "total_unique_contributors": 0,
            "ai_coauthor_tool_counts": {"claude_code": 2},
            "ai_author_tool_counts": {"claude_code": 1},
            "ai_commit_tool_first_dates": {"claude_code": "2026-01-13T08:20:35+00:00"},
        }
    )
    signals: list[AISignal] = []
    _detect_commits(old, signals)
    assert {s.evidence: s.first_seen for s in signals} == {
        "commit_trailer:claude_code": _utc(2026, 1, 13, 8, 20, 35),
        "commit_author:claude_code": _utc(2026, 1, 13, 8, 20, 35),
    }


# ----- cache versioning -----


def test_cache_entries_from_older_crawler_versions_are_recrawled(tmp_path):
    import json

    from civic_tech_crawler.cache import CACHE_VERSION, is_cached

    path = tmp_path / "o_r_data.json"
    assert not is_cached("o/r", str(tmp_path))

    path.write_text(json.dumps({"repo_metrics": {}}))  # pre-versioning entry
    assert not is_cached("o/r", str(tmp_path))

    path.write_text(json.dumps({"_cache_version": CACHE_VERSION}))
    assert is_cached("o/r", str(tmp_path))
