"""Tests for the per-repository cache: which entries a run may reuse."""

import json
from datetime import datetime, timezone

from civic_tech_crawler.cache import (
    CACHE_VERSION,
    SKIPPABLE_COLLECTORS,
    is_cached,
    load_repo_cache,
    save_repo_cache,
)
from civic_tech_crawler.models import RepoMetrics, RepositoryData

ALL_COLLECTORS = list(SKIPPABLE_COLLECTORS)


def _write_entry(tmp_path, **entry):
    payload = {"_cache_version": CACHE_VERSION, **entry}
    (tmp_path / "o_r_data.json").write_text(json.dumps(payload))


def _filled_collector_fields():
    # Stand-ins for every collector's output; is_cached only checks for None.
    return {field: {} for field in SKIPPABLE_COLLECTORS.values() if field}


def _repo_data():
    now = datetime(2026, 6, 3, tzinfo=timezone.utc)
    metrics = RepoMetrics(
        full_name="o/r", name="r", description=None, num_developers=1,
        total_commits=1, languages={}, primary_language=None,
        first_commit_date=None, last_commit_date=None, license_spdx=None,
        license_name=None, is_osi_approved=False, topics=[],
        has_contributing=False, has_code_of_conduct=False, has_governance=False,
        has_readme=True, has_issue_template=False, has_pr_template=False,
        health_percentage=0, stars=0, watchers=0, forks=0, cloud_detected=False,
        cloud_signals=[], ai_ml_detected=False, ai_ml_signals=[], has_ci_cd=False,
        ci_cd_workflows=[], deployments_count=0, created_at=now, updated_at=now,
    )
    return RepositoryData(
        repo_metrics=metrics, person_metrics=[], temporal_metrics=None,
        chaoss_metrics=None, crawled_at=now,
    )


def test_entry_with_no_skipped_collectors_is_reused(tmp_path):
    _write_entry(tmp_path, _skipped_collectors=[], **_filled_collector_fields())
    assert is_cached("o/r", str(tmp_path), ALL_COLLECTORS)


def test_entry_is_recrawled_when_a_needed_collector_was_skipped(tmp_path):
    _write_entry(
        tmp_path, _skipped_collectors=["chaoss", "issue_analytics"],
        **_filled_collector_fields(),
    )
    assert not is_cached("o/r", str(tmp_path), ALL_COLLECTORS)


def test_entry_is_reused_when_its_skipped_collector_is_not_needed(tmp_path):
    _write_entry(tmp_path, _skipped_collectors=["chaoss"], **_filled_collector_fields())
    needed = [c for c in ALL_COLLECTORS if c != "chaoss"]
    assert is_cached("o/r", str(tmp_path), needed)


def test_skipped_detection_is_recrawled_when_needed(tmp_path):
    # Detection writes into repo_metrics, so only the record can reveal the skip.
    _write_entry(tmp_path, _skipped_collectors=["detection"], **_filled_collector_fields())
    assert not is_cached("o/r", str(tmp_path), ALL_COLLECTORS)


def test_entry_without_record_infers_skipped_collectors_from_empty_fields(tmp_path):
    # The 2026-06 BirdXplorer case: a test run with --skip-chaoss and
    # --skip-issue-analytics left these fields empty, and the full crawl that
    # followed reused the entry as if it were complete.
    fields = _filled_collector_fields()
    fields["chaoss_metrics"] = None
    fields["issue_analytics"] = None
    _write_entry(tmp_path, **fields)
    assert not is_cached("o/r", str(tmp_path), ALL_COLLECTORS)


def test_complete_entry_without_record_is_reused(tmp_path):
    _write_entry(tmp_path, **_filled_collector_fields())
    assert is_cached("o/r", str(tmp_path), ALL_COLLECTORS)


def test_saved_entry_records_skipped_collectors(tmp_path):
    save_repo_cache(_repo_data(), str(tmp_path), skipped=["issue_analytics", "chaoss"])

    raw = json.loads((tmp_path / "o_r_data.json").read_text())
    assert raw["_skipped_collectors"] == ["chaoss", "issue_analytics"]
    assert not is_cached("o/r", str(tmp_path), ALL_COLLECTORS)
    # The record is trusted over the data: temporal ran but returned nothing.
    assert is_cached("o/r", str(tmp_path), ["temporal"])
    assert load_repo_cache("o/r", str(tmp_path)) is not None
