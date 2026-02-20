import logging
import time
from datetime import datetime, timezone

from github import Github

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, github_client: Github, buffer: int = 100):
        self._github = github_client
        self._buffer = buffer
        self._call_count = 0
        self._check_interval = 50

    def wait_if_needed(self) -> None:
        """Check rate limit and sleep if we're running low."""
        self._call_count += 1
        if self._call_count % self._check_interval != 0:
            return

        rate = self._github.get_rate_limit().rate
        if rate.remaining <= self._buffer:
            reset_time = rate.reset.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            sleep_seconds = (reset_time - now).total_seconds() + 5
            if sleep_seconds > 0:
                logger.warning(
                    "Rate limit low (%d remaining). Sleeping %.0fs until reset.",
                    rate.remaining,
                    sleep_seconds,
                )
                time.sleep(sleep_seconds)

    @property
    def remaining(self) -> int:
        return self._github.get_rate_limit().rate.remaining
