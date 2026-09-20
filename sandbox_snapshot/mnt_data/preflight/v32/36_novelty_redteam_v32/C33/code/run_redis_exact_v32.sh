#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   OPENAI_API_KEY=... bash run_redis_exact_v32.sh /path/to/agent-memory-server /path/to/work
# The key remains in the caller's environment and is never written by this script.

REPO="${1:?redis/agent-memory-server checkout required}"
WORK="${2:?empty work directory required}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$WORK/v32-output"
mkdir -p "$OUT"

python "$SCRIPT_DIR/preflight_redis_exact_v32.py" \
  --repo "$REPO" \
  --output "$OUT/preflight.json"

python "$SCRIPT_DIR/redis_exact_paired_probe_v32.py" \
  --repo "$REPO" \
  --work "$WORK/runtime" \
  --split oracle \
  --fail-after 1 \
  --top-k 10 \
  --answer-model gpt-4o \
  --with-judge \
  --judge-model gpt-4o \
  --output "$OUT/result.json"

python "$SCRIPT_DIR/validate_redis_result_v32.py" \
  "$OUT/result.json" \
  --output "$OUT/claim_gate.json"

python - <<'PY' "$OUT"
import hashlib, json, sys
from pathlib import Path
root=Path(sys.argv[1])
rows=[]
for p in sorted(root.rglob('*')):
    if p.is_file():
        rows.append({"path":str(p.relative_to(root)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size})
(root/'MANIFEST.json').write_text(json.dumps(rows,indent=2,sort_keys=True)+'\n')
PY

echo "V32 exact Redis gate complete: $OUT"
