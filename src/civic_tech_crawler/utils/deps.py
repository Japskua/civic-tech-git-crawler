"""Shared dependency-manifest parsing.

Extracts declared dependency names from the common manifest files at a repo's
root (requirements.txt, pyproject.toml, package.json). Used by both the
cloud/AI-ML detector and the AI-usage detector so the parsing logic lives in
one place.
"""

from __future__ import annotations

import json
import logging
import tomllib

logger = logging.getLogger(__name__)


def _strip_version(spec: str) -> str:
    """Turn a requirement spec like 'package[extra]>=1.0' into 'package'."""
    name = spec.split(">=")[0].split("<=")[0].split("==")[0].split("~=")[0]
    name = name.split(">")[0].split("<")[0].split("!=")[0]
    return name.split("[")[0].strip()


def extract_dependencies(client, slug: str) -> list[str]:
    """Extract lowercased dependency names from common dependency files.

    Reads requirements.txt, pyproject.toml ([project].dependencies) and
    package.json (dependencies + devDependencies). Missing/unparseable files
    are skipped silently.
    """
    deps: list[str] = []

    # requirements.txt
    content = client.get_file_content(slug, "requirements.txt")
    if content:
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("-"):
                name = _strip_version(line)
                if name:
                    deps.append(name.lower())

    # pyproject.toml dependencies
    content = client.get_file_content(slug, "pyproject.toml")
    if content:
        try:
            data = tomllib.loads(content)
            for dep in data.get("project", {}).get("dependencies", []):
                name = _strip_version(dep)
                if name:
                    deps.append(name.lower())
        except Exception:  # noqa: BLE001 — malformed manifests are best-effort
            pass

    # package.json
    content = client.get_file_content(slug, "package.json")
    if content:
        try:
            data = json.loads(content)
            for section in ("dependencies", "devDependencies"):
                for dep_name in data.get(section, {}):
                    deps.append(dep_name.lower())
        except Exception:  # noqa: BLE001
            pass

    return deps
