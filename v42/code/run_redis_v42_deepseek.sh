#!/bin/zsh
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BENCHMARK_REPO="$PROJECT_ROOT/third_party/agent-memory-server"
BENCHMARK_DIR="$BENCHMARK_REPO/agent-memory-benchmark"
V40_ROOT="$PROJECT_ROOT/sandbox_snapshot/mnt_data/v40"
V42_ROOT="$PROJECT_ROOT/v42"
OUT="${1:-$PROJECT_ROOT/experiment_outputs/redis_v42_deepseek_$(date +%Y%m%d_%H%M%S)}"

export MEM0_TELEMETRY=false

set -a
source "$PROJECT_ROOT/.env"
set +a

if [[ -z "${DEEPSEEK_API_KEY:-}" ]]; then
  print -u2 "DEEPSEEK_API_KEY is not set by $PROJECT_ROOT/.env"
  exit 2
fi

# The frozen benchmark answer path constructs AsyncOpenAI from environment.
# Point only that compatibility client at DeepSeek; embeddings are local.
export OPENAI_API_KEY="$DEEPSEEK_API_KEY"
export OPENAI_BASE_URL="https://api.deepseek.com"
export PATH="$BENCHMARK_DIR/.venv/bin:$PATH"

CACHE="$OUT/cache"
RESULTS="$OUT/results"
WORK="$OUT/work"
COHORT="$V42_ROOT/redis_v42_cohort.json"

mkdir -p "$OUT"
HTTP_PROXY="http://127.0.0.1:7891" \
HTTPS_PROXY="http://127.0.0.1:7891" \
ALL_PROXY="http://127.0.0.1:7891" \
http_proxy="http://127.0.0.1:7891" \
https_proxy="http://127.0.0.1:7891" \
all_proxy="http://127.0.0.1:7891" \
python "$V40_ROOT/code/fetch_frozen_longmemeval_v40.py" --cache-dir "$CACHE"

# DeepSeek is directly reachable on the target Mac. Do not couple a long formal
# run to the lifecycle of the optional local proxy used for Hugging Face fetches.
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
export NO_PROXY="localhost,127.0.0.1,::1"
export no_proxy="$NO_PROXY"
python "$V42_ROOT/code/preflight_redis_v42.py" \
  --repo "$BENCHMARK_REPO" --cache-dir "$CACHE" --cohort-file "$COHORT" \
  --output "$OUT/PREFLIGHT_V42.json"
python "$V42_ROOT/code/run_redis_v42_pilot.py" \
  --repo "$BENCHMARK_REPO" --cache-dir "$CACHE" --cohort-file "$COHORT" \
  --work-root "$WORK" --results-dir "$RESULTS" \
  --probe "$V42_ROOT/code/redis_v42_deepseek_paired_probe.py" \
  --answer-model deepseek-flash --no-judge
python "$V42_ROOT/code/validate_redis_v42_pilot.py" \
  --results-dir "$RESULTS" --cohort-file "$COHORT" \
  --output "$OUT/REDIS_V42_DEEPSEEK_PILOT_ANALYSIS.json"
python "$V40_ROOT/code/hash_tree_v40.py" "$OUT" \
  --output "$OUT/SHA256SUMS_RUNTIME_V42.txt"

print "V42 DeepSeek Redis pilot finished: $OUT"
