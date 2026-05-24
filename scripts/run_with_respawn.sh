#!/bin/bash
# Auto-respawn wrapper for civic-tech-crawler.
#
# Usage: scripts/run_with_respawn.sh <config> <output_dir> <expected_repos>
#
# Repeatedly invokes the crawler. Between invocations:
#   - Counts saved per-repo JSON files in output_dir
#   - If count >= expected_repos AND full_results.json exists, exit success
#   - If the crawler exits nonzero or is killed externally (SIGKILL has no
#     traceback, exit code 137), wait 10s and relaunch
#   - Per-repo cache means each relaunch skips already-saved repos
#
# Run with `setsid nohup ... &` so the wrapper survives parent shell exit.

set -uo pipefail

CONFIG="${1:?usage: $0 <config> <output_dir> <expected_repos>}"
OUTPUT_DIR="${2:?missing output_dir}"
EXPECTED="${3:?missing expected_repos}"

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
    echo "ERROR: GITHUB_TOKEN env var not set" >&2
    exit 1
fi

CRAWLER="$(cd "$(dirname "$0")/.." && pwd)/.venv/bin/civic-tech-crawler"
attempt=0
start_ts=$(date -u +%s)
prev_saved=-1
backoff=10
BACKOFF_MAX=120   # cap respawn backoff at 2 min during outages

while true; do
    attempt=$((attempt + 1))
    echo "============================================================"
    echo "[respawn-wrapper] attempt $attempt at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "============================================================"

    # Run the crawler; tee its output so the parent log gets everything
    "$CRAWLER" --config "$CONFIG"
    exit_code=$?

    saved=$(find "$OUTPUT_DIR" -maxdepth 1 -name '*_data.json' 2>/dev/null | wc -l)
    elapsed=$(($(date -u +%s) - start_ts))
    echo ""
    echo "[respawn-wrapper] crawler exit=${exit_code} saved=${saved}/${EXPECTED} elapsed=${elapsed}s"

    # Done condition: all per-repo cache files present AND aggregate exports written
    if [[ "$saved" -ge "$EXPECTED" && -f "$OUTPUT_DIR/full_results.json" ]]; then
        echo "[respawn-wrapper] all ${EXPECTED} repos cached and aggregate exports complete — exiting"
        exit 0
    fi

    # Adaptive backoff: retry promptly after an attempt that made progress; if an
    # attempt made NO progress (e.g. a DNS/network outage crashing the crawler at
    # startup), back off geometrically up to BACKOFF_MAX so we don't spin in a
    # tight loop — but keep retrying forever so the crawl auto-resumes once
    # connectivity returns. Per-repo cache means no work is ever repeated.
    if [[ "$saved" -gt "$prev_saved" ]]; then
        backoff=10
    else
        backoff=$(( backoff * 2 ))
        [[ "$backoff" -gt "$BACKOFF_MAX" ]] && backoff=$BACKOFF_MAX
    fi
    prev_saved=$saved
    echo "[respawn-wrapper] not done — sleeping ${backoff}s before respawn (no-progress backoff)"
    sleep "$backoff"
done
