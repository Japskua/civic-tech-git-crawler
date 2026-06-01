from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from civic_tech_crawler.utils.rate_limiter import RateLimiter


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr("civic_tech_crawler.utils.rate_limiter.time.sleep", lambda _s: None)


def _mock_github(remaining: int, reset_seconds_from_now: float = 60.0):
    """Build a fake Github client that returns the given rate-limit state."""
    rate = MagicMock()
    rate.remaining = remaining
    rate.reset = datetime.now(timezone.utc) + timedelta(seconds=reset_seconds_from_now)
    gh = MagicMock()
    gh.get_rate_limit.return_value.rate = rate
    return gh


def test_no_check_before_check_interval_reached():
    gh = _mock_github(remaining=5)
    limiter = RateLimiter(gh, buffer=100)
    # Default check_interval is 50; under 50 calls should not trigger get_rate_limit()
    for _ in range(49):
        limiter.wait_if_needed()
    gh.get_rate_limit.assert_not_called()


def test_checks_rate_limit_at_interval_boundary():
    gh = _mock_github(remaining=5000)
    limiter = RateLimiter(gh, buffer=100)
    for _ in range(50):
        limiter.wait_if_needed()
    gh.get_rate_limit.assert_called_once()


def test_does_not_sleep_when_remaining_above_buffer(monkeypatch):
    gh = _mock_github(remaining=500)
    limiter = RateLimiter(gh, buffer=100)

    sleep_calls = []
    monkeypatch.setattr(
        "civic_tech_crawler.utils.rate_limiter.time.sleep",
        lambda s: sleep_calls.append(s),
    )

    for _ in range(50):
        limiter.wait_if_needed()
    assert sleep_calls == []


def test_sleeps_when_remaining_is_at_or_below_buffer(monkeypatch):
    gh = _mock_github(remaining=50, reset_seconds_from_now=120)
    limiter = RateLimiter(gh, buffer=100)

    sleep_calls = []
    monkeypatch.setattr(
        "civic_tech_crawler.utils.rate_limiter.time.sleep",
        lambda s: sleep_calls.append(s),
    )

    for _ in range(50):
        limiter.wait_if_needed()
    assert len(sleep_calls) == 1
    # Sleep should be near 120s + 5s buffer; allow some slack for scheduling.
    assert 100 <= sleep_calls[0] <= 140


def test_remaining_property_reflects_underlying_rate_limit():
    gh = _mock_github(remaining=4123)
    limiter = RateLimiter(gh, buffer=100)
    assert limiter.remaining == 4123
