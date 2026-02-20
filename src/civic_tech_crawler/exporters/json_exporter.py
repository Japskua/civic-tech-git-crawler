import dataclasses
import json
import logging
from datetime import datetime
from pathlib import Path

from civic_tech_crawler.models import RepositoryData

logger = logging.getLogger(__name__)


class _DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def _to_dict(obj) -> dict | list | str | int | float | bool | None:
    """Convert dataclass instances to dicts recursively."""
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return dataclasses.asdict(obj)
    return obj


def export_json(data: list[RepositoryData], output_dir: str) -> None:
    """Export aggregated results to full_results.json.

    Per-repo JSON files are written by cache.py during crawling, not here.
    This function only produces the aggregated file.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    full_path = out / "full_results.json"
    full_data = [_to_dict(rd) for rd in data]
    with open(full_path, "w") as f:
        json.dump(full_data, f, indent=2, cls=_DateTimeEncoder)
    logger.info("Wrote %s (%d repositories)", full_path.name, len(data))
