"""Recompute is_osi_approved / osi_approved_license in an existing snapshot.

Datasets crawled before the osi_licenses.py fix (which added GitHub's deprecated
SPDX short forms such as "GPL-3.0") carry stale is_osi_approved=False values for
GPL/AGPL/LGPL repositories. This re-derives the flag from license_spdx using the
current (fixed) is_osi_approved() across every artifact in a snapshot:

    repo_metrics.csv      (is_osi_approved)
    chaoss_summary.csv    (osi_approved_license; license joined from repo_metrics)
    full_results.json     (repo_metrics.is_osi_approved + chaoss_metrics.osi_approved_license)
    <owner>_<repo>/data.json  (same nested fields, per repo)

It does NOT re-run the crawler — no API calls. Re-run build_repo_folders.py
afterwards to refresh the per-repo repo_results.md tables.

Usage:
    uv run python scripts/recompute_osi.py [snapshot-dir]   (default: datasets/2026_05)
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from civic_tech_crawler.utils.osi_licenses import is_osi_approved  # noqa: E402


def _rewrite_csv(path: Path, license_col: str | None, flag_col: str,
                 license_map: dict[str, str] | None, key_col: str) -> tuple[int, int]:
    """Recompute *flag_col* in a CSV. license comes from license_col in-row, or
    from license_map[key_col] when the CSV lacks a license column."""
    if not path.exists():
        return (0, 0)
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    before = sum(r.get(flag_col, "") == "True" for r in rows)
    for r in rows:
        lic = r.get(license_col) if license_col else (license_map or {}).get(r.get(key_col, ""))
        r[flag_col] = str(is_osi_approved(lic or None))
    after = sum(r[flag_col] == "True" for r in rows)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    return (before, after)


def _rewrite_json_items(items: list[dict]) -> int:
    """Recompute the two OSI fields on a list of repo records; return new True count."""
    changed = 0
    for it in items:
        rm = it.get("repo_metrics", {})
        ch = it.get("chaoss_metrics", {})
        lic = rm.get("license_spdx")
        new = is_osi_approved(lic)
        if rm.get("is_osi_approved") != new:
            changed += 1
        rm["is_osi_approved"] = new
        if "osi_approved_license" in ch:
            ch["osi_approved_license"] = new
    return changed


def main() -> int:
    snap = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "datasets" / "2026_05"
    if not snap.exists():
        print(f"ERROR: snapshot not found: {snap}", file=sys.stderr)
        return 1

    # Build full_name -> license_spdx map from repo_metrics.csv for the chaoss join.
    rm_path = snap / "repo_metrics.csv"
    license_map: dict[str, str] = {}
    if rm_path.exists():
        with rm_path.open(newline="") as f:
            for row in csv.DictReader(f):
                license_map[row["full_name"]] = row.get("license_spdx", "")

    b, a = _rewrite_csv(rm_path, "license_spdx", "is_osi_approved", None, "full_name")
    print(f"repo_metrics.csv      is_osi_approved:      {b} -> {a}")

    cb, ca = _rewrite_csv(snap / "chaoss_summary.csv", None, "osi_approved_license",
                          license_map, "repo_full_name")
    print(f"chaoss_summary.csv    osi_approved_license: {cb} -> {ca}")

    fr = snap / "full_results.json"
    if fr.exists():
        data = json.loads(fr.read_text())
        ch = _rewrite_json_items(data)
        fr.write_text(json.dumps(data, indent=2))
        print(f"full_results.json     records updated:      {ch}")

    per_repo = sorted(snap.glob("*/data.json"))
    updated = 0
    for p in per_repo:
        d = json.loads(p.read_text())
        if _rewrite_json_items([d]):
            updated += 1
        p.write_text(json.dumps(d, indent=2))
    print(f"per-repo data.json     files updated:        {updated}/{len(per_repo)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
