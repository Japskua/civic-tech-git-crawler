"""Detailed issue analytics collector.

Iterates ALL issues (excluding PRs) to build per-issue records with:
- Author, closer, state, timestamps
- Comment counts, labels, time-to-close
- Summary statistics (who opens/closes, median resolution time)
"""

from __future__ import annotations

import logging
import statistics
from collections import defaultdict

from github import GithubException

from civic_tech_crawler.models import IssueAnalytics, IssueRecord

logger = logging.getLogger(__name__)

# Cap individual issue fetches (for closed_by) to limit API usage
_CLOSED_BY_CAP = 2000
# Hard cap on total issues processed per repo, to bound runtime/memory on
# very large issue trackers (e.g. civiform/civiform has 7000+ issues, where
# secondary rate limits made the run open-ended).
_MAX_ISSUES = 5000
# How often to emit a progress line during the silent PyGithub pagination
_PROGRESS_EVERY = 250


def collect_issue_analytics(client, repo) -> IssueAnalytics:
    """Collect per-issue records and summary analytics for a repository."""
    slug = repo.full_name
    logger.info("Collecting issue analytics for %s", slug)

    try:
        all_issues = repo.get_issues(state="all", sort="created", direction="asc")
    except GithubException as e:
        logger.warning("Failed to get issues for %s: %s", slug, e)
        return _empty_result(slug)

    records: list[IssueRecord] = []
    openers: dict[str, int] = defaultdict(int)
    closers: dict[str, int] = defaultdict(int)
    close_times: list[float] = []
    comment_counts: list[int] = []
    closed_fetched = 0
    seen = 0
    capped = False

    issue_iter = iter(all_issues)
    while True:
        try:
            issue = next(issue_iter)
        except StopIteration:
            break
        except GithubException as e:
            logger.warning(
                "%s: issue iteration aborted after %d records: %s", slug, len(records), e
            )
            break

        # Skip pull requests (GitHub treats them as issues too)
        if issue.pull_request is not None:
            continue

        seen += 1
        if seen % _PROGRESS_EVERY == 0:
            logger.info("%s: processed %d issues so far (records=%d)", slug, seen, len(records))

        if len(records) >= _MAX_ISSUES:
            logger.warning(
                "%s: hit issue cap (%d), stopping early to bound runtime", slug, _MAX_ISSUES
            )
            capped = True
            break

        try:
            author_login = None
            if issue.user is not None:
                try:
                    author_login = issue.user.login
                except Exception:
                    pass

            state = issue.state
            created_at = issue.created_at
            closed_at = issue.closed_at
            updated_at = issue.updated_at
            comment_count = issue.comments
            labels = [label.name for label in issue.labels]

            # Time to close (days)
            time_to_close = None
            if closed_at and created_at:
                time_to_close = round((closed_at - created_at).total_seconds() / 86400, 2)
                close_times.append(time_to_close)

            # Who closed? Access closed_by (triggers individual issue fetch)
            closed_by_login = None
            if state == "closed" and closed_fetched < _CLOSED_BY_CAP:
                try:
                    if issue.closed_by is not None:
                        closed_by_login = issue.closed_by.login
                except (AttributeError, GithubException):
                    pass
                closed_fetched += 1

            # Track openers/closers
            if author_login:
                openers[author_login] += 1
            if closed_by_login:
                closers[closed_by_login] += 1

            comment_counts.append(comment_count)

            records.append(
                IssueRecord(
                    number=issue.number,
                    title=issue.title or "",
                    state=state,
                    author_login=author_login,
                    closed_by_login=closed_by_login,
                    created_at=created_at,
                    closed_at=closed_at,
                    updated_at=updated_at,
                    comment_count=comment_count,
                    labels=labels,
                    time_to_close_days=time_to_close,
                )
            )
        except (AttributeError, TypeError, GithubException) as e:
            logger.debug("Skipping issue in %s: %s", slug, e)
            continue

    # Compute summary metrics
    total = len(records)
    open_count = sum(1 for r in records if r.state == "open")
    closed_count = sum(1 for r in records if r.state == "closed")

    avg_comments = None
    if comment_counts:
        avg_comments = round(statistics.mean(comment_counts), 2)

    median_close = None
    if close_times:
        median_close = round(statistics.median(close_times), 2)

    logger.info(
        "%s: %d issues (%d open, %d closed), %d unique openers, %d unique closers%s",
        slug,
        total,
        open_count,
        closed_count,
        len(openers),
        len(closers),
        " [CAPPED]" if capped else "",
    )

    return IssueAnalytics(
        repo_full_name=slug,
        issues=records,
        total_issues=total,
        open_issues=open_count,
        closed_issues=closed_count,
        avg_comments_per_issue=avg_comments,
        median_time_to_close_days=median_close,
        unique_openers=len(openers),
        unique_closers=len(closers),
        top_openers=dict(sorted(openers.items(), key=lambda x: -x[1])),
        top_closers=dict(sorted(closers.items(), key=lambda x: -x[1])),
    )


def _empty_result(slug: str) -> IssueAnalytics:
    """Return an empty IssueAnalytics for repos where issues can't be fetched."""
    return IssueAnalytics(
        repo_full_name=slug,
        issues=[],
        total_issues=0,
        open_issues=0,
        closed_issues=0,
        avg_comments_per_issue=None,
        median_time_to_close_days=None,
        unique_openers=0,
        unique_closers=0,
    )
