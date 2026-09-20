#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <redis-agent-memory-server-checkout> <output-root>" >&2
  exit 64
fi
REPO="$(cd "$1" && pwd)"
OUT="$(mkdir -p "$2" && cd "$2" && pwd)"
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
CACHE="$OUT/cache"
RESULTS="$OUT/results"
WORK="$OUT/work"
COHORT="$ROOT/redis_v34_cohort.json"

python "$HERE/fetch_frozen_longmemeval_v40.py" --cache-dir "$CACHE"
python "$HERE/preflight_redis_v34_v40.py" \
  --repo "$REPO" --cache-dir "$CACHE" --cohort-file "$COHORT" \
  --output "$OUT/PREFLIGHT_V40.json"
python "$HERE/run_redis_v34_pilot_v40.py" \
  --repo "$REPO" --cache-dir "$CACHE" --cohort-file "$COHORT" \
  --work-root "$WORK" --results-dir "$RESULTS" \
  --probe "$HERE/redis_v34_exact_paired_probe_v40.py"
python "$HERE/validate_redis_v34_pilot_v40.py" \
  --results-dir "$RESULTS" --cohort-file "$COHORT" \
  --output "$OUT/REDIS_V34_PILOT_ANALYSIS_V40.json"
python "$HERE/hash_tree_v40.py" "$OUT" --output "$OUT/SHA256SUMS_RUNTIME_V40.txt"

echo "V34 Redis pilot finished: $OUT"
