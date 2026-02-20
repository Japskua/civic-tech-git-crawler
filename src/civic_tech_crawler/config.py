import os
import re
from pathlib import Path

import yaml

from civic_tech_crawler.models import CrawlerConfig


def _expand_env_vars(value: str) -> str:
    """Replace ${VAR_NAME} with environment variable values."""
    pattern = re.compile(r"\$\{([^}]+)\}")
    return pattern.sub(lambda m: os.environ.get(m.group(1), m.group(0)), value)


def _expand_env_in_dict(d: dict) -> dict:
    """Recursively expand environment variables in dict values."""
    result = {}
    for key, value in d.items():
        if isinstance(value, str):
            result[key] = _expand_env_vars(value)
        elif isinstance(value, dict):
            result[key] = _expand_env_in_dict(value)
        elif isinstance(value, list):
            result[key] = [
                _expand_env_vars(item) if isinstance(item, str) else item for item in value
            ]
        else:
            result[key] = value
    return result


def load_config(
    config_path: str,
    token_override: str | None = None,
    repos_override: list[str] | None = None,
    output_dir_override: str | None = None,
    skip_chaoss: bool = False,
    skip_temporal: bool = False,
    skip_detection: bool = False,
) -> CrawlerConfig:
    """Load configuration from YAML file with CLI overrides."""
    path = Path(config_path)
    if path.exists():
        with open(path) as f:
            raw = yaml.safe_load(f) or {}
        raw = _expand_env_in_dict(raw)
    else:
        raw = {}

    github_cfg = raw.get("github", {})
    output_cfg = raw.get("output", {})
    detection_cfg = raw.get("detection", {})

    token = token_override or os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise ValueError(
            "GitHub token is required. Set GITHUB_TOKEN environment variable "
            "or provide --token argument."
        )

    repositories = repos_override or raw.get("repositories", [])
    if not repositories:
        raise ValueError("At least one repository is required.")

    return CrawlerConfig(
        token=token,
        repositories=repositories,
        output_dir=output_dir_override or output_cfg.get("directory", "./output"),
        max_retries=github_cfg.get("max_retries", 5),
        retry_delay=github_cfg.get("retry_delay", 3.0),
        rate_limit_buffer=github_cfg.get("rate_limit_buffer", 100),
        cloud_keywords=detection_cfg.get("cloud_keywords", {}),
        ai_ml_keywords=detection_cfg.get("ai_ml_keywords", {}),
        skip_chaoss=skip_chaoss,
        skip_temporal=skip_temporal,
        skip_detection=skip_detection,
    )
