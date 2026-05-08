"""Recompute burstiness_cv from cached weekly_snapshots.csv.

The crawler's chaoss collector computes burstiness from GitHub's
/stats/commit_activity endpoint, which is async-built and frequently
times out for active repos (32 of 37 repos in the May 2026 n=37
crawl). When it times out, weekly_commits is cached as [] and
burstiness_cv as None, with no fallback.

But the same per-week commit data exists in weekly_snapshots.csv,
derived independently from the GraphQL bulk commit fetcher. This script
recomputes burstiness from that data — same metric (CV of weekly commit
counts), different (more reliable) source.

Usage:
    uv run python scripts/recompute_burstiness.py [snapshot-dir]

Default snapshot-dir is example_results/may_2026/. The script:
  1. Reads weekly_snapshots.csv and chaoss_summary.csv
  2. Computes trailing-52-week CV per repo (matches existing metric)
  3. Computes full-history CV per repo (a richer alternative not
     subject to the 52-week truncation bias of the original)
  4. Overwrites chaoss_summary.csv's burstiness_cv with the
     trailing-52w value (same column, more populated) and adds
     burstiness_cv_full_history as a new column
  5. Updates each per-repo data.json's chaoss_metrics.burstiness_cv

Where the existing burstiness_cv from /stats was already populated, the
trailing-52w-from-weekly-snapshots agrees within ±0.1 in 4 of 5 cases.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SNAPSHOT = ROOT / "example_results" / "may_2026"


def cv(values) -> float | None:
    """Population CV (matches src/civic_tech_crawler/collectors/chaoss_metrics.py:114)."""
    s = pd.Series(values, dtype=float)
    if len(s) < 2:
        return None
    m = s.mean()
    if m == 0:
        return None
    # ddof=0 to match math.sqrt(sum((c-mean)**2)/n) in chaoss_metrics._compute_burstiness
    return float(s.std(ddof=0) / m)


def compute_per_repo(ws: pd.DataFrame) -> pd.DataFrame:
    """Return DataFrame indexed by repo with cv_trailing_52w and cv_full_history."""
    ws = ws.sort_values(["repo_full_name", "week_start"])
    rows = []
    for repo, g in ws.groupby("repo_full_name", sort=False):
        full = g["total_commits"].astype(float)
        trailing = full.tail(52)
        rows.append(
            {
                "repo_full_name": repo,
                "burstiness_cv_trailing_52w": cv(trailing),
                "burstiness_cv_full_history": cv(full),
                "weeks_full_history": int(len(full)),
                "weeks_trailing_window": int(len(trailing)),
            }
        )
    return pd.DataFrame(rows)


def update_chaoss_summary(snapshot: Path, per_repo: pd.DataFrame) -> tuple[int, int]:
    csv_path = snapshot / "chaoss_summary.csv"
    backup = snapshot / "chaoss_summary.csv.before_burstiness_recompute"
    df = pd.read_csv(csv_path)
    df.to_csv(backup, index=False)

    before = int(df["burstiness_cv"].notna().sum())

    # Build a lookup: repo → trailing-52w CV
    trailing = per_repo.set_index("repo_full_name")["burstiness_cv_trailing_52w"]
    full = per_repo.set_index("repo_full_name")["burstiness_cv_full_history"]

    # Overwrite burstiness_cv with the (more populated) trailing-52w value where available.
    # Where weekly_snapshots has no data (very small projects with <2 weeks of activity)
    # we keep the existing value if any.
    df["burstiness_cv"] = df.apply(
        lambda r: round(trailing[r["repo_full_name"]], 2)
        if r["repo_full_name"] in trailing.index
        and pd.notna(trailing.get(r["repo_full_name"]))
        else r["burstiness_cv"],
        axis=1,
    )

    # Add the full-history alternative as a new column (may be more meaningful than 52-week
    # window for projects with long histories; left as a separate column to preserve
    # backward-compat with the existing metric).
    df["burstiness_cv_full_history"] = df["repo_full_name"].map(
        lambda r: round(full[r], 2) if r in full.index and pd.notna(full.get(r)) else None
    )

    df.to_csv(csv_path, index=False)
    after = int(df["burstiness_cv"].notna().sum())
    return before, after


def update_per_repo_jsons(snapshot: Path, per_repo: pd.DataFrame) -> int:
    """Sync each repo's data.json chaoss_metrics.burstiness_cv with the recomputed value.

    Looks for both flat-layout (<owner>_<repo>_data.json) and nested-layout
    (<owner>_<repo>/data.json).
    """
    trailing = per_repo.set_index("repo_full_name")["burstiness_cv_trailing_52w"]
    full = per_repo.set_index("repo_full_name")["burstiness_cv_full_history"]

    updated = 0
    for repo, val in trailing.items():
        if pd.isna(val):
            continue
        slug = repo.replace("/", "_")
        candidates = [
            snapshot / f"{slug}_data.json",
            snapshot / slug / "data.json",
        ]
        for path in candidates:
            if not path.exists():
                continue
            d = json.loads(path.read_text())
            chaoss = d.get("chaoss_metrics") or {}
            chaoss["burstiness_cv"] = round(float(val), 2)
            full_v = full.get(repo)
            if pd.notna(full_v):
                chaoss["burstiness_cv_full_history"] = round(float(full_v), 2)
            d["chaoss_metrics"] = chaoss
            path.write_text(json.dumps(d, indent=2, default=str))
            updated += 1
            break  # only update one layout per repo
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "snapshot",
        nargs="?",
        default=str(DEFAULT_SNAPSHOT),
        help=f"Snapshot directory (default: {DEFAULT_SNAPSHOT.relative_to(ROOT)})",
    )
    parser.add_argument(
        "--no-jsons",
        action="store_true",
        help="Skip per-repo data.json updates (only edit chaoss_summary.csv)",
    )
    args = parser.parse_args()

    snapshot = Path(args.snapshot).resolve()
    ws_csv = snapshot / "weekly_snapshots.csv"
    ch_csv = snapshot / "chaoss_summary.csv"
    if not ws_csv.exists() or not ch_csv.exists():
        print(f"ERROR: missing {ws_csv} or {ch_csv}", file=sys.stderr)
        return 1

    ws = pd.read_csv(ws_csv)
    print(f"Loaded {len(ws):,} rows from {ws_csv}")
    print(f"  {ws['repo_full_name'].nunique()} repos, weeks {ws['week_start'].min()} → {ws['week_start'].max()}")

    per_repo = compute_per_repo(ws)
    print(f"Computed burstiness for {per_repo['burstiness_cv_trailing_52w'].notna().sum()} of {len(per_repo)} repos")

    before, after = update_chaoss_summary(snapshot, per_repo)
    print(f"chaoss_summary.csv burstiness_cv: {before} → {after} populated rows")

    if not args.no_jsons:
        n = update_per_repo_jsons(snapshot, per_repo)
        print(f"Updated burstiness_cv in {n} per-repo data.json files")

    print(f"\nDone. Backup at {snapshot}/chaoss_summary.csv.before_burstiness_recompute")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
