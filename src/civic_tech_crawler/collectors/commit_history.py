"""Full commit history collector for weekly snapshots and contributor lifecycle analysis.

Iterates ALL commits (not limited to 52-week stats window) to build:
- Weekly project-level snapshots (commits, contributors, growth)
- Per-contributor weekly activity breakdown
- Contributor lifecycle metrics (appearance, departure, duration)
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timezone

from civic_tech_crawler.models import (
    CommitHistoryMetrics,
    ContributorLifecycle,
    ContributorWeek,
    WeeklySnapshot,
)
from civic_tech_crawler.utils.ai_detection import (
    DEFAULT_AI_DEV_KEYWORDS,
    detect_ai_in_commit,
)

logger = logging.getLogger(__name__)

# Contributors with no commits in the last 90 days are considered "departed"
_DEPARTURE_THRESHOLD_DAYS = 90


def _iso_week_start(dt: datetime) -> str:
    """Return the Monday of the ISO week containing *dt* as 'YYYY-MM-DD'."""
    from datetime import timedelta

    monday = dt.date() - timedelta(days=dt.weekday())
    return monday.isoformat()


def collect_commit_history(
    client, repo, ai_dev_keywords: dict | None = None
) -> CommitHistoryMetrics:
    """Parse the full commit history into weekly snapshots and contributor lifecycles.

    Uses GraphQL (100 commits per API call, includes additions/deletions) — about
    35x faster than the REST-per-commit approach and avoids the PyGithub
    RecursionError on 202 retries.

    The same single pass also tallies AI-assisted-development signals from each
    commit's message/author (co-author trailers, agent-bot commits) so the
    ai_usage collector needs no second commit walk.
    """
    slug = repo.full_name
    logger.info("Collecting commit history for %s", slug)

    if client is None:
        logger.warning("%s: client is None, cannot iterate commits via GraphQL", slug)
        return _empty_result(slug)

    dev_kw = ai_dev_keywords or DEFAULT_AI_DEV_KEYWORDS

    # Per-contributor tracking
    # Key = contributor_id (login or email)
    contributor_info: dict[str, dict] = {}  # id -> {login, name, email}
    contributor_commits: dict[str, list[datetime]] = defaultdict(list)
    # (contributor_id, week_start) -> {additions, deletions}
    contributor_week_lines: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"additions": 0, "deletions": 0}
    )

    # Weekly tracking
    week_commits: dict[str, int] = defaultdict(int)  # week_start -> count
    week_contributors: dict[str, set[str]] = defaultdict(set)  # week_start -> set of ids

    # AI-assisted-development tally (piggybacks this commit walk)
    ai_coauthored = 0
    ai_authored = 0
    ai_coauthor_tool_counts: dict[str, int] = defaultdict(int)
    ai_author_tool_counts: dict[str, int] = defaultdict(int)
    ai_tool_first_dates: dict[str, datetime] = {}

    commit_count = 0
    for rec in client.iter_commits_graphql(slug):
        commit_count += 1
        author_date = rec.committed_date
        author_email = rec.author_email or "unknown"
        author_name = rec.author_name or ""
        login = rec.author_login

        # AI commit detection (co-author trailers + agent-bot authors)
        co_tools, auth_tools = detect_ai_in_commit(
            rec.message, login, author_email, dev_kw
        )
        if co_tools:
            ai_coauthored += 1
        if auth_tools:
            ai_authored += 1
        for tool in co_tools:
            ai_coauthor_tool_counts[tool] += 1
        for tool in auth_tools:
            ai_author_tool_counts[tool] += 1
        for tool in co_tools | auth_tools:
            prev = ai_tool_first_dates.get(tool)
            if prev is None or author_date < prev:
                ai_tool_first_dates[tool] = author_date

        # Determine contributor ID: prefer GitHub login, fall back to email
        contributor_id = login if login else author_email

        # Store contributor info (last seen wins for name)
        if contributor_id not in contributor_info:
            contributor_info[contributor_id] = {
                "login": login,
                "name": author_name,
                "email": author_email,
            }
        elif login and not contributor_info[contributor_id]["login"]:
            contributor_info[contributor_id]["login"] = login

        # Record commit date for this contributor
        contributor_commits[contributor_id].append(author_date)

        # Weekly aggregation
        week = _iso_week_start(author_date)
        week_commits[week] += 1
        week_contributors[week].add(contributor_id)

        # Per-contributor weekly line changes (from GraphQL payload — no extra calls)
        bucket = contributor_week_lines[(contributor_id, week)]
        bucket["additions"] += rec.additions
        bucket["deletions"] += rec.deletions

    logger.info("%s: iterated %d commits via GraphQL", slug, commit_count)

    if not week_commits:
        return _empty_result(slug)

    # -- Step 2: Build sorted weekly snapshots --------------------------------
    all_weeks = sorted(week_commits.keys())
    seen_contributors: set[str] = set()
    cumulative_commits = 0
    snapshots: list[WeeklySnapshot] = []

    for week in all_weeks:
        week_contribs = week_contributors[week]
        new_contribs = week_contribs - seen_contributors
        seen_contributors.update(week_contribs)
        cumulative_commits += week_commits[week]

        snapshots.append(
            WeeklySnapshot(
                week_start=week,
                total_commits=week_commits[week],
                unique_contributors=len(week_contribs),
                new_contributors=len(new_contribs),
                cumulative_commits=cumulative_commits,
                cumulative_contributors=len(seen_contributors),
            )
        )

    # -- Step 3: Build contributor lifecycles ---------------------------------
    now = datetime.now(timezone.utc)
    lifecycles: list[ContributorLifecycle] = []

    for cid, commit_dates in contributor_commits.items():
        info = contributor_info[cid]
        commit_dates_sorted = sorted(commit_dates)
        first = commit_dates_sorted[0]
        last = commit_dates_sorted[-1]

        duration_days = max((last - first).days, 0)

        # Count active weeks (unique ISO weeks with commits)
        active_week_set = {_iso_week_start(d) for d in commit_dates_sorted}
        active_weeks = len(active_week_set)

        # Total weeks span from first to last commit
        total_weeks_span = max(duration_days // 7, 1)
        activity_ratio = round(active_weeks / total_weeks_span, 4) if total_weeks_span > 0 else 1.0

        # Departure detection
        # Make last timezone-aware if needed
        last_aware = last if last.tzinfo else last.replace(tzinfo=timezone.utc)
        days_since_last = (now - last_aware).days
        departed = days_since_last > _DEPARTURE_THRESHOLD_DAYS
        departed_weeks_ago = days_since_last // 7 if departed else None

        total = len(commit_dates_sorted)
        avg_per_week = round(total / active_weeks, 2) if active_weeks > 0 else 0.0

        lifecycles.append(
            ContributorLifecycle(
                repo_full_name=slug,
                contributor_id=cid,
                login=info["login"],
                name=info["name"],
                email=info["email"],
                first_commit_date=first,
                last_commit_date=last,
                duration_days=duration_days,
                total_commits=total,
                active_weeks=active_weeks,
                total_weeks_span=total_weeks_span,
                activity_ratio=activity_ratio,
                status="departed" if departed else "active",
                departed_weeks_ago=departed_weeks_ago,
                avg_commits_per_active_week=avg_per_week,
            )
        )

    # Sort lifecycles: most commits first
    lifecycles.sort(key=lambda lc: -lc.total_commits)

    # -- Step 4: Build per-contributor weekly activity -------------------------
    contributor_weeks: list[ContributorWeek] = []
    for cid, commit_dates in contributor_commits.items():
        # Count commits per week for this contributor
        cid_week_counts: dict[str, int] = defaultdict(int)
        for d in commit_dates:
            cid_week_counts[_iso_week_start(d)] += 1
        for week, count in sorted(cid_week_counts.items()):
            lines = contributor_week_lines.get((cid, week), {"additions": 0, "deletions": 0})
            contributor_weeks.append(
                ContributorWeek(
                    contributor_id=cid,
                    week_start=week,
                    commits=count,
                    lines_added=lines["additions"],
                    lines_removed=lines["deletions"],
                )
            )

    # -- Step 5: Compute new contributor rate ---------------------------------
    total_unique = len(contributor_info)
    if len(all_weeks) >= 4:
        first_week = datetime.fromisoformat(all_weeks[0])
        last_week = datetime.fromisoformat(all_weeks[-1])
        span_months = max((last_week - first_week).days / 30.44, 1)
        new_rate = round(total_unique / span_months, 2)
    else:
        new_rate = None

    logger.info(
        "%s: %d weeks, %d contributors, %d weekly activity records",
        slug,
        len(snapshots),
        total_unique,
        len(contributor_weeks),
    )

    return CommitHistoryMetrics(
        repo_full_name=slug,
        weekly_snapshots=snapshots,
        contributor_lifecycles=lifecycles,
        contributor_weeks=contributor_weeks,
        total_weeks=len(snapshots),
        total_unique_contributors=total_unique,
        new_contributor_rate_per_month=new_rate,
        total_commits_scanned=commit_count,
        ai_coauthored_commit_count=ai_coauthored,
        ai_authored_commit_count=ai_authored,
        ai_coauthor_tool_counts=dict(ai_coauthor_tool_counts),
        ai_author_tool_counts=dict(ai_author_tool_counts),
        ai_commit_tool_first_dates={
            tool: dt.isoformat() for tool, dt in ai_tool_first_dates.items()
        },
    )


def _empty_result(slug: str) -> CommitHistoryMetrics:
    """Return an empty CommitHistoryMetrics for repos with no commits."""
    return CommitHistoryMetrics(
        repo_full_name=slug,
        weekly_snapshots=[],
        contributor_lifecycles=[],
        contributor_weeks=[],
        total_weeks=0,
        total_unique_contributors=0,
        new_contributor_rate_per_month=None,
    )
