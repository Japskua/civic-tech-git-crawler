import logging
import time
from typing import Any, Callable

from github import GithubException

logger = logging.getLogger(__name__)


def retry_on_none(
    func: Callable[[], Any],
    max_retries: int = 5,
    base_delay: float = 3.0,
    description: str = "stats",
) -> Any:
    """Retry a function that returns None due to GitHub 202 computing responses."""
    for attempt in range(max_retries):
        result = func()
        if result is not None and result != []:
            return result
        delay = base_delay * (attempt + 1)
        logger.info(
            "%s computing (attempt %d/%d), waiting %.1fs...",
            description,
            attempt + 1,
            max_retries,
            delay,
        )
        time.sleep(delay)
    logger.warning("%s returned None after %d attempts", description, max_retries)
    return None


def retry_with_backoff(
    func: Callable[[], Any],
    max_retries: int = 3,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
) -> Any:
    """Retry with exponential backoff for rate limit or server errors."""
    for attempt in range(max_retries):
        try:
            return func()
        except GithubException as e:
            if e.status in (403, 429, 500, 502, 503) and attempt < max_retries - 1:
                delay = base_delay * (backoff_factor**attempt)
                logger.warning(
                    "GitHub API error %d, backing off %.1fs (attempt %d/%d)",
                    e.status,
                    delay,
                    attempt + 1,
                    max_retries,
                )
                time.sleep(delay)
            else:
                raise
    return None  # unreachable but satisfies type checker
