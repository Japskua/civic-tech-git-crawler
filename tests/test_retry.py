from unittest.mock import MagicMock

import pytest
from github import GithubException

from civic_tech_crawler.utils.retry import retry_on_none, retry_with_backoff


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    # Tests should not actually sleep. Patch time.sleep in both retry modules.
    monkeypatch.setattr("civic_tech_crawler.utils.retry.time.sleep", lambda _s: None)


# ----- retry_on_none -----


def test_retry_on_none_returns_first_non_none_result():
    func = MagicMock(side_effect=[None, None, ["data"]])
    result = retry_on_none(func, max_retries=5, base_delay=0.0)
    assert result == ["data"]
    assert func.call_count == 3


def test_retry_on_none_returns_immediately_when_first_call_succeeds():
    func = MagicMock(return_value={"k": "v"})
    result = retry_on_none(func, max_retries=5, base_delay=0.0)
    assert result == {"k": "v"}
    assert func.call_count == 1


def test_retry_on_none_gives_up_after_max_retries():
    func = MagicMock(return_value=None)
    result = retry_on_none(func, max_retries=3, base_delay=0.0)
    assert result is None
    assert func.call_count == 3


def test_retry_on_none_treats_empty_list_as_none():
    func = MagicMock(side_effect=[[], [], [1, 2, 3]])
    result = retry_on_none(func, max_retries=5, base_delay=0.0)
    assert result == [1, 2, 3]
    assert func.call_count == 3


def test_retry_on_none_does_not_treat_zero_or_false_as_none():
    func = MagicMock(return_value=0)
    result = retry_on_none(func, max_retries=3, base_delay=0.0)
    assert result == 0
    assert func.call_count == 1


# ----- retry_with_backoff -----


def _github_exception(status: int) -> GithubException:
    return GithubException(status, {"message": "boom"}, None)


def test_retry_with_backoff_returns_first_successful_result():
    func = MagicMock(return_value="ok")
    assert retry_with_backoff(func, max_retries=3, base_delay=0.0) == "ok"
    assert func.call_count == 1


def test_retry_with_backoff_retries_on_retryable_error_then_succeeds():
    func = MagicMock(side_effect=[_github_exception(503), "ok"])
    result = retry_with_backoff(func, max_retries=3, base_delay=0.0)
    assert result == "ok"
    assert func.call_count == 2


@pytest.mark.parametrize("status", [403, 429, 500, 502, 503])
def test_retry_with_backoff_retries_documented_retryable_statuses(status):
    func = MagicMock(side_effect=[_github_exception(status), "ok"])
    result = retry_with_backoff(func, max_retries=3, base_delay=0.0)
    assert result == "ok"
    assert func.call_count == 2


def test_retry_with_backoff_does_not_retry_on_non_retryable_status():
    # 404 is not in the retry list and should propagate immediately.
    func = MagicMock(side_effect=_github_exception(404))
    with pytest.raises(GithubException):
        retry_with_backoff(func, max_retries=3, base_delay=0.0)
    assert func.call_count == 1


def test_retry_with_backoff_raises_after_exhausting_retries():
    func = MagicMock(side_effect=_github_exception(503))
    with pytest.raises(GithubException):
        retry_with_backoff(func, max_retries=2, base_delay=0.0)
    assert func.call_count == 2
